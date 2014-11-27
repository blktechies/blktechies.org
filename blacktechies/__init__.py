# -*- coding: utf-8 -*-
from os import getenv

from flask import Flask, session, g, render_template
from flask_wtf.csrf import CsrfProtect
from blacktechies import config

app = Flask('blacktechies', template_folder='views')
CsrfProtect(app)

if getenv('BLACKTECHIES_COM_ENVIRONMENT', False) == 'Development':
    app.config.from_object(config.Development)
else:
    app.config.from_object(config.Production)


from blacktechies.controllers import main
from blacktechies.controllers import jobs

app.register_blueprint(main.mod)
app.register_blueprint(jobs.mod)
