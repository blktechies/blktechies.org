import string
from random import choice

from blacktechies.database import db


class User(db.Model):
    STATUS_ACTIVE = 0
    STATUS_NEEDS_ACTIVATION = 1
    STATUS_SPAM = 2
    STATUS_DELETED = -1

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # user auth
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')
    reset_password_token = db.Column(db.String(100), nullable=False, default='')
    is_enabled = db.Column(db.Boolean, nullable=False, default=False)
    first_name = db.Column(db.String(127), nullable=False, default='')
    last_name = db.Column(db.String(127), nullable=False, default='')
    status = db.Column(db.Integer, nullable=False, default=STATUS_NEEDS_ACTIVATION)
    # Relationship columns
    email_addresses = db.relationship('UserEmail')
    roles = db.relationship('Role', secondary='user_roles')
    open_ids = db.relationship('UserOpenID')
    job_postings = db.relationship('JobPosting')

    @staticmethod
    def new_inactive_user():
        user = User(is_enabled=False, status=User.STATUS_NEEDS_ACTIVATION)
        user.username = random_username()
        return user


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
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())
    is_primary = db.Column(db.Boolean(), nullable=True, default=False)
    # Relationship columns
    user = db.relationship(User, uselist=False)
    # This index should prevent a user from having multiple primary emails
    __table_args__ = (db.Index('idx_primary_email', 'user_id', 'is_primary',
                            postgresql_where=is_primary == True, unique=True),)

class Role(db.Model):
    ROLE_ADMIN = 'admin'
    ROLE_MODERATOR = 'moderator'

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
    random_suffix = join_str.join(choice(string.ascii_uppercase + string.digits) for _ in range(suffix_length))
    return prefix + random_suffix
