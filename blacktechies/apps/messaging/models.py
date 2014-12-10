import time
from blacktechies.database import db

class Message(db.Model):
    STATUS_ACTIVE = 0
    STATUS_DELETED = 1
    
    __tablename__ = 'messages'
    id = db.Column(db.BigInteger, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False, index=True)
    from_user_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=STATUS_ACTIVE)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    sender = db.relationship('User', uselist=False, foreign_keys=[from_user_id])

    def __str__(self):
        return self.body

class Conversation(db.Model):
    STATUS_ACTIVE = 0
    STATUS_DELETED = 1

    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer, nullable=False, default=STATUS_ACTIVE)
    last_updated = db.Column(db.Integer, nullable=False, default=time.time())

    messages = db.relationship('Message')
    users = db.relationship('ConversationUser', secondary='conversations_users')


class ConversationUser(db.Model):
    """ All of the users who can participate in a conversation """

    __tablename__ = 'conversations_users'
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined = db.Column(db.DateTime, nullable=False)
    __table_args__ = (db.PrimaryKeyConstraint('user_id', 'conversation_id', name="pk_conversation_users"),)
