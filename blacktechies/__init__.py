from os import getenv
from os.path import getmtime

from flask import Flask, session, g, render_template
from flask.globals import _app_ctx_stack

# from babel.dates import format_datetime, get_timezone

app = Flask('blacktechies', template_folder='views')


if getenv('BLACKTECHIES_COM_ENVIRONMENT', False) == 'Development':
    app.debug = True

## @@FIXME ##
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


from blacktechies.controllers import main
app.register_blueprint(main.mod)
