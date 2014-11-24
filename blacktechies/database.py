# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from blacktechies import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
# db_session = scoped_session(sessionmaker(autocommit=False,
#                                          autoflush=False,
#                                          bind=engine))
# Base = declarative_base()
# Base.query = db_session.query_property()

def create_all():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import blacktechies.models.job
    import blacktechies.models.user
    db.create_all()

def teardown_db():
    import blacktechies.models.job
    import blacktechies.models.user
    db.drop_all()
