from flask_wtf import Form
from wtforms import validators
from wtforms.fields import StringField, TextAreaField, IntegerField, HiddenField, PasswordField, BooleanField

from blacktechies.utils.validation import FormTimestamp
from blacktechies.utils.form import generate_ts
from blacktechies.apps.user.models import User

class LoginForm(Form):
    timestamp = HiddenField('timestamp', validators=[validators.required(), FormTimestamp(days=1)], default=generate_ts())
    username = StringField('Username or Email', validators=[validators.required()], description="Username or Email")
    password = PasswordField('Password', validators=[validators.required()], description="Password")
    remember_me = BooleanField('Remember me')

class RegistrationForm(Form):
    timestamp = HiddenField('timestamp', validators=[validators.required(), FormTimestamp(hours=12)])
    email = StringField('Email address', description="you@example.com", validators=[validators.required(), validators.email(message="You must provide a valid email address")])
    username = StringField('Screen name', description="Screen name (optional)", validators=[
        validators.regexp(regex=User.USERNAME_REGEX, message="Usernames may only contain alphanumeric characters, dashes and underscores"),
        validators.length(min=3, max=16, message="Usernames may be between 3 and 16 characters, inclusive"),
        validators.optional()])
    password = PasswordField('Password', description="Password", validators=[validators.required(), validators.length(min=8, message="Password must be at least %(min)d characters in length")])
    confirm_password = PasswordField('Confirm password', description="Confirm password", validators=[validators.required(), validators.EqualTo('password', message="Passwords must match")])
