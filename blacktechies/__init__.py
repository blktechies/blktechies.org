from os import getenv

from flask import Flask, session, g, render_template

app = Flask('blacktechies', template_folder='views')
if getenv('BLACKTECHIES_COM_ENVIRONMENT', False) == 'Development':
    app.debug = True

## @@FIXME ##
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

from blacktechies.controllers import main
from blacktechies.controllers import jobs

app.register_blueprint(main.mod)
app.register_blueprint(jobs.mod)
