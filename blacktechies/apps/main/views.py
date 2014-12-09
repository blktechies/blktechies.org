from flask import Blueprint, render_template

mod = Blueprint('main', __name__, template_folder="templates")

@mod.route('/')
def index():
    return render_template('index.html')

@mod.route('/meetup')
def meetup():
    return render_template('meetup.html')
