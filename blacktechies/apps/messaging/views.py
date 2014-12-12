import os
from flask import Blueprint, render_template, request, current_app, redirect
from flask_login import current_user, login_required

from blacktechies.database import db
from blacktechies.apps.user.models import User, UserEmail
from blacktechies.apps.messaging.models import Message, Conversation, ConversationUser

_template_dir = os.path.dirname(__file__)
mod = Blueprint('messaging', __name__, url_prefix='/inbox', template_folder=_template_dir + "/templates")


@mod.route("/")
@login_required
def inbox():
    conversations = Conversation.query.join(ConversationUser).\
                    filter(ConversationUser.user_id==current_user.id).\
                    order_by(Conversation.last_updated).\
                    limit(25).all()
    # Select * from messages where conversation_id in [] order by id desc
    return str(conversations)

