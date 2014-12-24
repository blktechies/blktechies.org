# -*- coding: utf-8 -*-

from datetime import timedelta

from flask import Blueprint, render_template, abort, request, redirect, url_for
from flask.ext.login import current_user, login_required
from blacktechies.database import db
from blacktechies.utils.validation import FormTimestamp
from blacktechies.utils.form import generate_ts
from blacktechies.apps.job.forms import ModerateEmailSubmissionForm, NewJobForm
from blacktechies.apps.job.models.jobposting import JobPosting
from blacktechies.apps.job.models.emailedjobsubmission import JobPostingEmailSubmission
from blacktechies.apps.user.models import User

mod = Blueprint('jobs', __name__, url_prefix='/jobs', template_folder="templates")


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
    post = JobPostingEmailSubmission.query.get(post_id)
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
    if form.validate_on_submit():
        try:
            title = request.form['title']
            body = request.form['body']
            submission_id = int(form['submission_id'])
            if submission_id != post_id:
                http_status = 400
        except:
            http_status = 400
        if http_status != 400:
            new_posting = JobPosting(title=title, body=body, submission_id=post_id,
                                     posted_by_user_id=post.user_id)
            db.session.add(new_posting)
            if db.session.commit():
                http_status = 303
                return redirect(url_for('jobs_post', post_id=new_posting.id), code=303)
    form.submission_id.data = str(post_id)
    return render_template('jobs/pending_promote.html', post=post, form=form)


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
    post = JobPosting.query.get(post_id)
    if not post:
        abort(404)
    return render_template('jobs/post_detail.html', job=post)
