from flask import Blueprint, render_template

from blacktechies.models.job import JobPosting

mod = Blueprint('jobs', __name__, url_prefix='/jobs')

@mod.route('/')
def index():
    jobs = JobPosting.query.all()
    return render_template('jobs/index.html', jobs=jobs)
