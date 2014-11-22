from string import ascii_lowercase, digits
from random import choice

from blacktechies.database import db

def get_user_id(user=None, user_id=None):
    if user and user_id:
        raise ValueError(msg="Cannot set both 'user' and 'user_id'")
    elif user:
        return user.id
    else:
        return user_id

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
    email_addresses = db.relationship('UserEmail', backref='user')
    roles = db.relationship('Role', secondary='user_roles')
    open_ids = db.relationship('UserOpenID', backref='user')

    @staticmethod
    def new_inactive_user(email, roles=None):
        if roles is None:
            roles = []
        user = User()
        random_suffix = ''.join(choice(ascii_lowercase + string.digits) for _ in range(16))
        user.username = 'anonymous' + random_suffix
        email = UserEmail()
        email.email = email
        email.is_primary = True
        email.user = user
        user.email_addresses.append(email)
        for role in roles:
            user.roles.append(Role(role))

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

    def __init__(self, user_id=None, provider_id=None, open_id_url=None, user=None):
        user_id = get_user_id(user=user, user_id=user_id)


class UserEmail(db.Model):
    __tablename__ = 'user_emails'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())
    is_primary = db.Column(db.Boolean(), nullable=True, default=False)
    # Relationship columns
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


class UserRole(db.Model):
    __tablename__ = 'user_roles'
    # Primary key on tuple: (user_id, role_id)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))
    __table_args__ = (db.PrimaryKeyConstraint('user_id', 'role_id', name="pk_user_roles"),)
