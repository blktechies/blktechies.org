# -*- coding: utf-8 -*-
import os
from datetime import time, timedelta


from flask import Blueprint, render_template, abort, request, make_response, current_app
from flask_wtf import Form
from flask.ext.login import current_user, login_required
from wtforms import validators
from wtforms.fields import StringField, TextAreaField, IntegerField, HiddenField
from blacktechies.utils.validation import FormTimestamp
from blacktechies.utils.form import generate_ts

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
    return render_template('jobs/index.html', jobs=jobs)


@mod.route('/pending')
@login_required
def pending():
    pending_posts = JobPostingEmailSubmission().query.all()
    return render_template('jobs/all_pending.html', pending_posts=pending_posts)

@mod.route('/pending/<int:post_id>', methods=['GET'])
@login_required
def pending_detail(post_id, title=None, body=None):
    if not post:
        abort(404)
    return render_template('pending_detail.html', post=post)

@mod.route("/pending/<int:post_id>/promote", methods=['GET', 'POST'])
@login_required
def promote_pending_post(post_id):
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
    return render_template('jobs/pending_promote.html', post=post, form=form)


class NewJobForm(Form):
    timestamp = HiddenField('timestamp', validators=[validators.required(), FormTimestamp(days=1)], default=generate_ts())
    title = StringField('Job Post Title', validators=[validators.required(message="Your post must have a title"),
                                             validators.Length(min=10, max=200, message="Title can be from 10 to 200 characters long")])
    body = TextAreaField('Job Description', validators=[validators.required(message="The post must have a description"),
                                                        validators.length(max=2500, min=140, message="Job post was too small. (Or too big).")])


@mod.route("/new_post", methods=['GET', 'POST'])
@login_required
def new_jobs_post():
    form = NewJobForm()
    if form.validate_on_submit():
        posting = JobPosting()
        posting.title = form.title.data
        posting.body = form.body.data
        posting.posted_by_user_id = current_user.id
        db.session.add(posting)
        if db.session.commit():
            return redirect(url_for('.jobs_post', post_id=posting.id), code=303)
    return render_template('jobs/new_post.html', form=form)

@mod.route("/post/<int:post_id>")
def jobs_post(post_id):
    post = JobPosting.query.get(id=post_id)
    if not post:
        abort(404)
    return render_template('jobs/post_detail.html', post=post)
