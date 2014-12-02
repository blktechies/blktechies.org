from flask import Blueprint, render_template, request, current_app, redirect, flash
from flask_login import login_user

from blacktechies.models.user import User, UserEmail
from blacktechies.forms.user import RegistrationForm, LoginForm
from blacktechies.utils.form import generate_ts
from blacktechies.utils.signer import serializer

mod = Blueprint('login_register', __name__)

@mod.route('/login', methods=['GET', 'POST'])
def login():
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
        if user and user_manager.verify_password(request.form['password'], user.password):
            login_user(user, remember_me=form.remember_me.data)
            redirect_loc = request.args.get('next', None)
            if redirect_loc:
                try:
                    redirect_loc = serializer.loads(redirect_loc)
                except:
                    pass
            return redirect(redirect_loc or url_for('user.home'), 303)
        else:
            errors = ['Username or password were incorrect.']
    login_form.timestamp.data = generate_ts()
    return render_template('users/login.html', errors=errors, login_form=login_form)

@mod.route('/register', methods=['GET', 'POST'])
def register():
    registration_form = RegistrationForm()
    errors = []
    if registration_form.validate_on_submit():
        username = registration_form.username.data or User.random_username()
        user = User(username=username, password=request.form['password'])
        user.status = User.STATUS_ACTIVE
        email = UserEmail(email=request.form['email'], is_primary=True)
        user.email_addresses.add(email)
        db.session.add_all([user, email])
        try:
            db.session.commit()
            login_user(user)
            return redirect('users.home', 303)
        except:
            errors.append("There was a problem committing the registration. Please try again.")
    registration_form.timestamp.data = generate_ts()
    return render_template('users/register.html', errors=errors, registration_form=registration_form)

@mod.route('/home')
def home():
    pass
