# -*- coding: utf-8 -*-
import re
import string

from flask import current_app
from flask_login import UserMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

from blacktechies import app
from blacktechies.database import db
from blacktechies.utils.string import random_string
from blacktechies.utils.password import encrypt_password, verify_password


class User(db.Model, UserMixin):
    STATUS_ACTIVE = 0
    STATUS_UNCONFIRMED_EMAIL = 1
    STATUS_SPAM = 2
    STATUS_INACTIVE = 3
    STATUS_DELETED = 9

    STATUSES = {
        STATUS_ACTIVE: 'active',
        STATUS_UNCONFIRMED_EMAIL: 'unconfirmed email',
        STATUS_INACTIVE: 'inactive',
        STATUS_SPAM: 'spam',
        STATUS_DELETED: 'deleted',
    }

    USERNAME_REGEX = re.compile('\A[a-zA-Z0-9-_]{3,24}\Z')

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # user auth
    username = db.Column(db.String(50), nullable=False, unique=True, index=True)
    _password = db.Column('password', db.String(255), nullable=False, default='')
    reset_password_token = db.Column(db.String(100), nullable=False, default='')
    is_enabled = db.Column(db.Boolean, nullable=False, default=False)
    first_name = db.Column(db.String(127), nullable=False, default='')
    last_name = db.Column(db.String(127), nullable=False, default='')
    status = db.Column(db.Integer, nullable=False, default=STATUS_UNCONFIRMED_EMAIL)
    # Relationship columns
    email_addresses = db.relationship('UserEmail', uselist=True, back_populates='user')
    roles = db.relationship('Role', secondary='user_roles')
    open_ids = db.relationship('UserOpenID')
    job_postings = db.relationship('JobPosting', primaryjoin="User.id == JobPosting.posted_by_user_id")

    @staticmethod
    def new_inactive_user():
        user = User(is_enabled=False, status=User.STATUS_UNCONFIRMED_EMAIL)
        user.username = random_username()
        return user

    @staticmethod
    def random_username(prefix=None, length=8, separator='_'):
        if not prefix:
            prefix = 'anonymous'
        return separator.join([prefix, random_string(length)])

    def has_confirmed_email(self, filter_=None):
        for email in self.email_addresses:
            if filter_:
                if email.email == filter_:
                    return email.is_confirmed()
            elif email.is_confirmed():
                return True
        return False

    @validates('username')
    def validate_username(self, key, username):
        if len(username) < 3:
            raise ValueError("Username is too short")
        elif len(username) > 24:
            raise ValueError("Username is too long")
        elif not User.USERNAME_REGEX.match(username):
            raise ValueError("Username may only contain alphanumeric, dash, and underscore characters")
        return username

    @validates('password')
    def validate_password(self, key, password):
        bs_passwords = ['password', 'iloveyou', '12345678', 'abc', '1234']
        bs_regexes = [
            ('^p.{6}d', re.IGNORECASE), # Nothing that looks like 'password', 'p4ssw0rd', etc
            ('i\s*love\s*you', re.IGNORECASE), # No more "I love yous"
            ('123|789|890|abc|xyz', re.IGNORECASE), # keep out the simple stuff
            ('(.)\1{3,}', 0), # No character repeated 3+ times
        ]
        too_simple = ValueError("Password is too simple")
        if len(password) < 8:
            raise ValueError("Passwords must be at least 8 characters in length")
        if password in bs_passwords:
            raise too_simple

        for pattern, flags in bs_regexes:
            if re.match(pattern, password, flags):
                raise too_simple
        password = encrypt_password(password)
        return password

    @validates('first_name', 'last_name')
    def validate_name(self, key, name):
        valid = re.compile('^[\w\s-]*$') # only word-characters and whitespace.
        if not valid.match(name):
            raise ValueError("%s contains invalid characters" % (key))
        return name

    @validates('status')
    def validate_status(self, key, status):
        status = int(status)
        if status not in self.STATUSES:
            raise ValueError("Invalid status '%d' for user" % status)

    def is_active(self):
        return ((self.status == self.STATUS_ACTIVE or
                 self.status == self.STATUS_UNCONFIRMED_EMAIL) and
                self.is_enabled)


    @property
    def secure_token(self):
        return make_secure_token(str(self.id), self.password)

    @property
    def primary_email(self):
        for email in self.email_addresses:
            if email.is_primary:
                return email
        else:
            return None
        # No primary email, so we have to set one...
        self.email_addresses[0].is_primary = true

    @primary_email.setter
    def primary_email(self, new_email):
        for email in self.email_addresses:
            email.is_primary = Falsee
        new_email.is_primary = True
        if new_email not in self.email_addresses:
            self.email_addresses.append(new_email)

    def verify_password(self, plaintext_password):
        """Verifies that the plaintext_password hashes to the same value as
        the user's password.
        """
        return verify_password(plaintext_password, self.password)

    @hybrid_property
    def password(self):
        # if re.match('^\$2a\$\d\d\$[a-zA-Z0-9\./]{53}$', self._password):
        return self._password

    @password.setter
    def password(self, password):
        self.validate_password(None, password)
        self._password = password

    def get_id(self):
        if self.id:
            return str(self.id)
        # allows two unsaved objects to be compared
        return ':'.join(['None', str(id(self))])


class UserOpenID(db.Model):
    """Allows users to connect multiple OpenIDs to their account so they can login with
    an external provider as well as email and password
    """
    PROVIDER_GOOGLE = 1
    PROVIDER_YAHOO = 2
    PROVIDER_FACEBOOK = 3

    __tablename__ = 'user_openids'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider_id = db.Column(db.Integer, nullable=False)
    open_id_url = db.Column(db.Text, nullable=False)
    # relationship columns
    user = db.relationship('User', uselist=False)


class UserEmail(db.Model):
    __tablename__ = 'user_emails'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    confirmed_at = db.Column(db.DateTime())
    is_primary = db.Column(db.Boolean(), nullable=True, default=False)
    # Relationship columns
    user = db.relationship(User, uselist=False, back_populates='email_addresses')
    # This index should prevent a user from having multiple primary emails
    __table_args__ = (db.Index('idx_primary_email', 'user_id', 'is_primary',
                            postgresql_where=is_primary == True, unique=True),)

    def is_confirmed(self):
        return bool(self.confirmed_at)

    def __str__(self):
        return self.email

class Role(db.Model):
    ADMIN = 'admin'
    MODERATOR = 'moderator'


    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(31), index=True, unique=True, nullable=False)
    description = db.Column(db.Text(), nullable=False)
    # relationship columns
    users = db.relationship('User', secondary='user_roles')


class UserRole(db.Model):
    __tablename__ = 'user_roles'
    # Primary key on tuple: (user_id, role_id)
    __table_args__ = (db.PrimaryKeyConstraint('user_id', 'role_id', name="pk_user_roles"),)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), index=True)


def random_username(prefix="anonymous", suffix_length=16, join_str="_"):
    return join_str.join([prefix, random_string(suffix_length)])
