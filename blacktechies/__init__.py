from os import getenv

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from blacktechies import config

app = Flask('blacktechies', template_folder='views')
if getenv('BLACKTECHIES_ENVIRONMENT', False) == 'Development':
    app.config.from_object(config.Development)
else:
    app.config.from_object(config.Production)

db = SQLAlchemy(app)

from blacktechies import app_init

app, db = app_init.init_app(app, db)


from blacktechies.controllers import jobs, main, users
app.register_blueprint(jobs.mod)
app.register_blueprint(main.mod)
app.register_blueprint(users.mod)
