from flask import Blueprint, render_template

from blacktechies.models.job import JobPosting, JobPostingEmailSubmission
from blacktechies.models.user import User

mod = Blueprint('jobs', __name__, url_prefix='/jobs')

@mod.route('/')
def index():
    jobs = JobPosting.query.all()
    return render_template('jobs/index.html', jobs=jobs)

@mod.route('/pending')
def pending():
    pending_posts = JobPostingEmailSubmission().query.all()
    return render_template('jobs/all_pending.html', pending_posts=pending_posts)
