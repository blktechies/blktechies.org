# -*- coding: utf-8 -*-
import json
import hashlib
import hmac

from flask import Blueprint, render_template, abort, request, make_response, jsonify, current_app
from flask_wtf import Form
from wtforms import validators
from wtforms.fields import StringField, TextAreaField, IntegerField, HiddenField


from blacktechies.models.job import JobPosting, JobPostingEmailSubmission
from blacktechies.models.user import User
from blacktechies.utils.validation import hmac_match

mod = Blueprint('jobs', __name__, url_prefix='/jobs')

def json_response(code=200, body=None, errors=None, extra=None):
    if not errors:
        errors = []
    elif not isinstance(errors, list):
        errors = [errors, ]
    if not extra:
        extra = None

    response_data = {
        'meta': {
            'status_code': code,
            'errors': errors,
        },
        'data': body,
        'extra': extra,
    }

    response = jsonify(response_data)
    response.status_code = code
    return response

def json_error(code=400, errors=None, **kwargs):
    if code < 400:
        raise ValueError("json_error should only be called for errors")
    kwargs['code'] = code
    kwargs['errors'] = errors
    response = json_response(**kwargs)
    return response


class ModerateEmailSubmissionForm(Form):
    title = StringField(u'Job Post Title', [validators.required(), validators.length(max=250, min=10)])
    body = TextAreaField(u'Job Post Description',[validators.required(), validators.length(min=140, max=3*1024)])
    submission_id = HiddenField(validators=[validators.required()])

@mod.route('/')
def index():
    jobs = JobPosting.query.all()
    return render_template('jobs/index.html', jobs=jobs)

@mod.route('/pending')
def pending():
    pending_posts = JobPostingEmailSubmission().query.all()
    return render_template('jobs/all_pending.html', pending_posts=pending_posts)

@mod.route('/pending/<int:post_id>', methods=['GET'])
def pending_detail(post_id):

    return render_template('jobs/pending_detail.html', post=post, form=form)

@mod.route("/pending/<int:post_id>")
def new_jobs_post():
    post = JobPostingEmailSubmission.query.get(post_id)
    if not post:
        abort(404)
    form = ModerateEmailSubmissionForm()
    if request.method == 'GET':
        form.submission_id.data = hmac.new(current_app.secret_key, str(post_id))
    elif request.method == 'POST':
        if form.validate_on_submit():
            title = request.form['title']
            body = request.form['body']
            submission_id = request.form['submission_id']
        if not hmac_match(submission_id, str(post_id)):
            return redirect(url_for(pending_detail, post_id=post_id))


@mod.route("/listing", methods=['POST'])
def new_jobs_post_boom():
    needs_submission_id = False


    if json:
        title = json.get('title')
        body = json.get('body')
        submission_id = json.get('submission_id')
    else:
        title = request.form['title']
        body = request.form['body']
        submission_id = request.form['submission_id']
    if not (title and body):
        abort(400)
    submission = JobPostingEmailSubmission.query.get(submission_id)
    if not submission:
        abort(400)

    posting = JobPosting
