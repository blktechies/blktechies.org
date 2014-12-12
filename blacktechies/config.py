import os

class MailConfig(object):
    MAIL_USERNAME = os.getenv('BLACKTECHIES_MAIL_USER', '')
    MAIL_PASSWORD = os.getenv('BLACKTECHIES_MAIL_PASSWORD', '')
    MAIL_SERVER = os.getenv('BLACKTECHIES_MAIL_SERVER', '')
    MAIL_DEFAULT_SENDER = "'Black Techies Mailer' <%s>" % MAIL_USERNAME
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

class Config(FlaskUserConfig, FlaskLoginConfig, FlaskWTFConfig, MailConfig):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/blackteches-dev-db.sqlite3'
    SECRET_KEY = os.getenv('BLACKTECHIES_SECRET_KEY')


class Development(Config):
    DEBUG = True

class Production(Config):
    DEBUG = False

