from os import getenv
from os.path import getmtime

from flask import Flask, session, g, render_template
from flask.globals import _app_ctx_stack

from babel.dates import format_datetime, get_timezone

app = Flask('blacktechies', template_folder='views')


if getenv('BLACKTECHIES_COM_ENVIRONMENT', False) == 'Development':
    app.debug = True

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

def render_template_with_mtime(template_name_or_list, **context):
    ctx = _app_ctx_stack.top
    template = ctx.app.jinja_env.get_or_select_template(template_name_or_list)
    mtime = getmtime(template.filename)
    us_eastern = get_timezone('US/Eastern')
    long_date = format_datetime(mtime, tzinfo=us_eastern)
    context.update({'template_mtime': mtime, 'template_mdate': long_date, 'template_name_or_list': template})
    return render_template(**context)

# from kylewpppd_com.views import main
# from kylewpppd_com.views import blog
# from kylewpppd_com.views import projects
# from kylewpppd_com.views import photography


# app.register_blueprint(main.mod)
# app.register_blueprint(blog.mod)
# app.register_blueprint(projects.mod)
# app.register_blueprint(photography.mod)


