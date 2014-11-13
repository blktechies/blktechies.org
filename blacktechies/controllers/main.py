from flask import Blueprint, render_template

mod = Blueprint('main', __name__)

@mod.route('/')
def index():
    return render_template('main/index.html')
