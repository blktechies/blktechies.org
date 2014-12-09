from os import getenv

from flask import Flask, g
from flask.ext.sqlalchemy import SQLAlchemy
from blacktechies import config
from flask_login import current_user

app = Flask('blacktechies', template_folder='views')
if getenv('BLACKTECHIES_ENVIRONMENT', False) == 'Development':
    app.config.from_object(config.Development)
else:
    app.config.from_object(config.Production)

db = SQLAlchemy(app)

from blacktechies import app_init

app, db = app_init.init_app(app, db)

from blacktechies.apps.main import views as main_views
from blacktechies.apps.user import views as user_views
from blacktechies.apps.job import views as job_views

app.register_blueprint(job_views.mod)
app.register_blueprint(main_views.mod)
app.register_blueprint(user_views.mod)

@app.before_request
def g_user():
    g.user = current_user
