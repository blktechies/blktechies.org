# -*- coding: utf-8 -*-
from datetime import time, timedelta

from flask import Blueprint, render_template, abort, request, make_response, current_app
from flask_wtf import Form
from wtforms import validators
from wtforms.fields import StringField, TextAreaField, IntegerField, HiddenField

from blacktechies.apps.job.models.jobposting import JobPosting
from blacktechies.apps.job.models.emailedjobsubmission import JobPostingEmailSubmission
from blacktechies.apps.user.models import User

mod = Blueprint('jobs', __name__, url_prefix='/jobs', template_folder="templates")

class ModerateEmailSubmissionForm(Form):
    title = StringField('Job Post Title', [validators.required(), validators.length(max=250, min=10)])
    body = TextAreaField('Job Post Description',[validators.required(), validators.length(min=140, max=3*1024)])
    submission_id = HiddenField(validators=[validators.required()])
    timestamp = HiddenField(validators=[validators.required()])

@mod.route('/')
def index():
    jobs = JobPosting.query.all()
    return render_template('index.html', jobs=jobs)

@mod.route('/pending')
def pending():
    pending_posts = JobPostingEmailSubmission().query.all()
    return render_template('all_pending.html', pending_posts=pending_posts)

@mod.route('/pending/<int:post_id>', methods=['GET'])
def pending_detail(post_id, title=None, body=None):
    if not post:
        abort(404)
    return render_template('pending_detail.html', post=post)

@mod.route("/pending/<int:post_id>/promote", methods=['GET', 'POST'])
def new_jobs_post(post_id):
    post = JobPostingEmailSubmission.query.get(post_id)
    if not post:
        abort(404)

    form = ModerateEmailSubmissionForm()
    # refresh status code and timestamp because the user may have
    # tampered with them
    form.submission_id.data = signer.sign(str(post_id))
    form.timestamp.data = time_signer.sign(random_string(16))

    http_status = 200
    if request.method == 'POST' and form.validate_on_submit():
        try:
            title = request.form['title']
            body = request.form['body']
            submission_id = int(signer.unsign(request.form['submission_id']))
            _ = timestamp_signer.unsign(request.form['timestamp'], max_age=timedelta(minutes=30).total_seconds())
        except:
            http_status = 400
        if http_status != 400:
            new_posting = JobPosting(title=title, body=body, submission_id=post_id,
                                     posted_by_user_id=post.user_id)
            db.session.add(new_posting)
            if db.session.commit():
                http_status = 303
                return redirect(url_for('jobs_post', post_id=new_posting.id), code=303)
    return render_template('pending_promote.html', post=post, form=form)

# @mod.route("/listing", methods=['POST'])
# def new_jobs_post_boom():
#     needs_submission_id = False

#     if json:
#         title = json.get('title')
#         body = json.get('body')
#         submission_id = json.get('submission_id')
#     else:
#         title = request.form['title']
#         body = request.form['body']
#         submission_id = request.form['submission_id']
#     if not (title and body):
#         abort(400)
#     submission = JobPostingEmailSubmission.query.get(submission_id)
#     if not submission:
#         abort(400)

#     posting = JobPosting
