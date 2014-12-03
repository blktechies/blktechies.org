import os

if os.getenv('BLACKTECHIES_SECRET_KEY') is None:
    raise RuntimeError("Secret key must be specified")

class MailConfig(object):
    MAIL_USERNAME = os.environ['BLACKTECHIES_MAIL_USER']
    MAIL_PASSWORD = os.environ['BLACKTECHIES_MAIL_PASSWORD']
    MAIL_DEFAULT_SENDER = "'Black Techies Mailer' <%s>" % MAIL_USERNAME
    MAIL_SERVER = os.environ['BLACKTECHIES_MAIL_SERVER']
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = True

class FlaskWTFConfig(object):
    pass

class FlaskLoginConfig(object):
    from datetime import timedelta
    REMEMBER_COOKIE_NAME = 'rm_rf'
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True

class FlaskUserConfig(object):
    USER_PASSWORD_HASH = 'bcrypt'

class Config(MailConfig, FlaskUserConfig, FlaskLoginConfig, FlaskWTFConfig):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['BLACKTECHIES_SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/blackteches-dev-db.sqlite3'

class Development(Config):
    DEBUG = True


class Production(Config):
    DEBUG = False
