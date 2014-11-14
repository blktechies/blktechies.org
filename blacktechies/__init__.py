from os import getenv
from os.path import getmtime

from flask import Flask, session, g, render_template

from blacktechies.database import db_session

app = Flask('blacktechies', template_folder='views')
if getenv('BLACKTECHIES_COM_ENVIRONMENT', False) == 'Development':
    app.debug = True

## @@FIXME ##
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

from blacktechies.controllers import main
from blacktechies.controllers import jobs

app.register_blueprint(main.mod)
app.register_blueprint(jobs.mod)
