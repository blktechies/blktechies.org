from os import getenv

from flask import Flask, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask_login import current_user

app = Flask('blacktechies', template_folder='views')
if getenv('BLACKTECHIES_ENVIRONMENT', False) == 'Development':
    from blacktechies.config import Development
    app.config.from_object(Development)
    if app.secret_key is None:
        app.secret_key = 'blahblahblah'
else:
    from blacktechies.config import Production
    app.config.from_object(Production)
    if app.secret_key is None:
        raise RuntimeError("A secret key must be specified to run in production mode")

db = SQLAlchemy(app)

from blacktechies import app_init

app, db = app_init.init_app(app, db)

from blacktechies.apps.main import views as main_views
from blacktechies.apps.user import views as user_views
from blacktechies.apps.job import views as job_views
from blacktechies.apps.messaging import views as messaging_views

app.register_blueprint(job_views.mod)
app.register_blueprint(main_views.mod)
app.register_blueprint(user_views.mod)
app.register_blueprint(messaging_views.mod)

@app.before_request
def g_user():
    g.user = current_user
