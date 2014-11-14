from flask import Blueprint, render_template

from blacktechies.models.job import Job

mod = Blueprint('jobs', __name__, url_prefix='/jobs')

@mod.route('/')
def index():
    jobs = Job.query.all()
    return render_template('jobs/index.html', jobs=jobs)
