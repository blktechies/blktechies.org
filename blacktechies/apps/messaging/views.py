import datetime

from flask import Blueprint, render_template, request, current_app, redirect, abort, url_for
from flask_login import current_user, login_required

from blacktechies.database import db
from blacktechies.apps.user.models import User
from blacktechies.apps.messaging.forms import NewMessageForm, ReplyForm
from blacktechies.apps.messaging.models import Message, Conversation, ConversationUser

mod = Blueprint('messaging', __name__, url_prefix='/messages', template_folder="templates")


@mod.route("/")
@login_required
def index():
    before_timestamp = request.args.get('before', 0)

    conversations = Conversation.query.from_statement(db.text(
        """
        SELECT c.* FROM conversations c
        INNER JOIN conversations_users cu
        ON c.id = cu.conversation_id
        WHERE cu.user_id = :userid
        AND c.last_updated > :before
        LIMIT 25
        """)).params(userid=current_user.id, before=before_timestamp).all()
    messages = Message.most_recent(conversations)
    return render_template('messaging/index.html',
                           conversations=conversations,
                           messages=messages)


@mod.route("/new", methods=['GET', 'POST'])
@login_required
def new_message():
    form = NewMessageForm()
    try:
        if form.validate_on_submit():
            message = Message.from_string(request.form['body'])
            message.sender = current_user

        conversation = Conversation()
        conversation.subject = request.form.get('subject')
        to_usernames = form.filtered_usernames(request.form['to_usernames'])
        if not to_usernames:
            raise ValueError("No valid recipients found")

        # Find all users with the usernames
        users = User.query.filter(User.username.in_(to_usernames)).all()
        if len(users) != len(set(to_usernames)):
            raise ValueError("Not all recipients were found")

        conversation.users.append(current_user)
        for user in users:
            if user.id != current_user.id:
                conversation.users.append(user)

        conversation.messages.append(message)
        db.session.add(conversation)
        if db.session.commit():
            return redirect(url_for('messaging.conversation_index',
                                    conversation_id=conversation.id), 303)
    except:
        raise
    form.timestamp.data = form.current_timestamp()
    return render_template('messaging/new.html',
                           conversation=conversation,
                           form=form)


@mod.route("/<int:conversation_id>/reply", methods=['GET', 'POST'])
@login_required
def new_reply(conversation_id):
    form = ReplyForm()
    conversation = Conversation.query.get(conversation_id)
    if not conversation or not conversation.has_user(current_user):
        return abort(404)

    try:
        if (form.validate_on_submit() and
                int(request.form['conversation_id']) == conversation_id):
            message = Message.from_string(request.form['body'])
            message.sender = current_user
            conversation.messages.append(message)
            db.session.add(conversation)
            db.session.commit()
            return redirect(url_for('messaging.conversation_index',
                                    conversation_id=conversation.id), 303)
    except:
        raise
    form.timestamp.data = form.current_timestamp()
    return conversation_index(conversation_id, form)

@mod.route("/<int:conversation_id>")
@login_required
def conversation_index(conversation_id, form=None):
    before = request.args.get('before', 0)
    limit = request.args.get('limit', 25)
    try:
        limit = int(limit)
    except:
        limit = 0
    if limit < 1 or limit > 50:
        limit = 25

    c = Conversation.query.filter_by(id=conversation_id).first_or_404()
    if not c.has_user(current_user):
        return abort(404)
    if form is None:
        form = ReplyForm()

    form.conversation_id.data = conversation_id
    messages = Message.for_conversation(c, limit=limit, before_id=before)
    return render_template('messaging/conversation.html', conversation=c,
                           messages=messages, form=form)
