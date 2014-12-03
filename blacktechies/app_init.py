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
    from blacktechies import login
    login_manager = LoginManager(app)
    bt_manager = login.BlacktechiesLoginManager(login_manager)
    login_manager.login_view = login_manager.refresh_view = 'users.login'
    login_manager.login_message = "Please login to access this page."



def _init_flask_user(app, db):
    from flask_user import SQLAlchemyAdapter, UserManager
    from blacktechies.models.user import User, UserEmail
    # We really want to get away from this module. All it's really
    # giving us is password hashing. We can probably just pluck that
    # out and use only the password hashing.
    db_adapter = SQLAlchemyAdapter(db, User, UserEmailClass=UserEmail)
    user_manager = UserManager(db_adapter)
    def noop(*args, **kwargs): pass
    user_manager.add_url_routes = noop
    user_manager.init_app(app)

def init_app(app, db):
    _init_csrf_protection(app, db)
    _init_mail(app, db)
    _init_login(app, db)
    # _init_flask_user(app, db)
    return app, db
