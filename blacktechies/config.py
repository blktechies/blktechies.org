import os

if os.getenv('BLACKTECHIES_SECRET_KEY') is None:
    raise RuntimeError("Secret key must be specified")

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.getenv('BLACKTECHIES_SECRET_KEY')

class Development(Config):
    DEBUG = True

class Production(Config):
    DEBUG = False
