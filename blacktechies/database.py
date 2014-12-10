# -*- coding: utf-8 -*-

from flask import Flask
from blacktechies import db

def create_all():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from blacktechies.apps.user import models as user_models
    from blacktechies.apps.job import models as job_models
    from blacktechies.apps.messaging import models as messaging_models
    db.create_all()

def teardown_db():
    from blacktechies.apps.user import models as user_models
    from blacktechies.apps.job import models as job_models
    from blacktechies.apps.messaging import models as messaging_models
    db.drop_all()
