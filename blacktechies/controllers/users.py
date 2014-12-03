from flask import Blueprint, render_template, request, current_app, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user

from blacktechies import app
from blacktechies.database import db
from blacktechies.models.user import User, UserEmail
from blacktechies.forms.user import RegistrationForm, LoginForm
from blacktechies.utils.form import generate_ts
from blacktechies.utils.signer import serializer

mod = Blueprint('users', __name__)

@mod.route('/login', methods=['GET', 'POST'])
def login(unauthorized=False):
    login_form = LoginForm()
    errors = []
    user = None

    if login_form.validate_on_submit():
        if '@' in request.form['username']:
            email = UserEmail.query.filter_by(email=request.form['username']).first()
            if email:
                user = email.user
        else:
            user = User.query.filter_by(username=request.form['username']).first()
        if user and user.verify_password(request.form['password']):
            login_user(user, remember=login_form.remember_me.data)
            redirect_loc = None
            return redirect(redirect_loc or url_for('users.home'), 303)
        else:
            errors.append("Username or password were incorrect.")
    login_form.timestamp.data = generate_ts()
    return render_template('users/login.html', errors=errors, login_form=login_form)

# @app.login_manager.unauthorized_handler
# def unauthorized():
#     return "NOPE"

@mod.route('/register', methods=['GET', 'POST'])
def register():
    registration_form = RegistrationForm()
    errors = []
    if registration_form.validate_on_submit():
        username = registration_form.username.data or User.random_username()
        user = User(username=username, password=request.form['password'], is_active=True)
        user.status = User.STATUS_ACTIVE
        email = UserEmail(email=request.form['email'], is_primary=True)
        user.email_addresses.append(email)
        db.session.add_all([user, email])
        try:
            db.session.commit()
            login_user(user)
            return redirect(url_for('users.home'), 303)
        except:
            if app.debug:
                raise
            errors.append("There was a problem committing the registration. Please try again.")
    registration_form.timestamp.data = generate_ts()
    return render_template('users/register.html', errors=errors, registration_form=registration_form)

@mod.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash("You have been successfully logged out.")
    return redirect(url_for('main.index'), 303)

@mod.route('/home')
@login_required
def home():
    name = current_user.username or current_user.primary_email.email
    return "Welcome, %s!" % name
