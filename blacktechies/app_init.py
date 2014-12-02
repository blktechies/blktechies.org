from os import getenv
from blacktechies import config

def _init_sqlalchemy(app, _):
    return db

def _init_csrf_protection(app, db):
    from flask_wtf.csrf import CsrfProtect
    CsrfProtect(app)

def _init_mail(app, db):
    from flask.ext.mail import Mail
    mail = Mail()
    mail.init_app(app)

def _init_login(app, db):
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)

def _init_flask_user(app, db):
    from flask_user import SQLAlchemyAdapter, UserManager
    from blacktechies.models.user import User, UserEmail
    db_adapter = SQLAlchemyAdapter(db, User, UserEmailClass=UserEmail)
    UserManager(db_adapter, app)

def init_app(app, db):
    _init_csrf_protection(app, db)
    _init_mail(app, db)
    _init_login(app, db)
    _init_flask_user(app, db)
    return app, db
