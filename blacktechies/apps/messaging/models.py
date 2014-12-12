import datetime, time
from blacktechies.database import db

class Message(db.Model):
    """Model representing a message from one user to one or more
    users. The `is_read` flag only makes sense when the conversation
    has two people."""

    STATUS_ACTIVE = 0
    STATUS_DELETED = 1

    __tablename__ = 'messages'
    id = db.Column(db.BigInteger, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False, index=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=STATUS_ACTIVE)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    # Relationship columns
    sender = db.relationship('User', uselist=False, foreign_keys=[from_user_id])
    conversation = db.relationship('Conversation', uselist=False, foreign_keys=[conversation_id])

    def __str__(self):
        return self.body

    def delete(self):
        self.status = STATUS_DELETED

    @classmethod
    def new_message(cls, message, **kwargs):
        msg_args = {
            'body': message,
            'status': cls.STATUS_ACTIVE,
            'timestamp': datetime.datetime.now(),
            'is_read': False,
        }
        msg_args.update(kwargs)
        return cls(msg_args)


class Conversation(db.Model):
    STATUS_ACTIVE = 0
    STATUS_DELETED = 1

    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer, nullable=False, default=STATUS_ACTIVE)
    last_updated = db.Column(db.Integer, nullable=False, default=int(time.time()))

    messages = db.relationship('Message')
    users = db.relationship('ConversationUser', backref="conversations")

    def most_recent_messages(self, limit=10, before_id=None):
        return Message.query.filter_by(
            and_(conversation_id==self.id, id < before_id))\
                            .order_by(Message.id.desc())\
                            .limit(limit)

    def add_user(self, user):
        conv_user = ConversationUser(status=ConversationUser.STATUS_ACTIVE,
                                     joined=datetime.datetime.now())
        conv_user.user = user
        self.users.append(conv_user)

    def remove_user(self, user):
        for conv_user in self.users:
            if conv_user.id == user.id:
                conv_user.status=STATUS_PARTED

    def add_message(self, message):
        self.messages.append(message)

    def new_message(self, message, user):
        m = Message.new_message(message, user=user, conversation=self)
        self.add_message(m)
        return m

class ConversationUser(db.Model):
    """ All of the users who can participate in a conversation.

    All conversations are able to be shared between multiple users.
    """
    STATUS_ACTIVE = 0
    STATUS_PARTED = 1

    __tablename__ = 'conversations_users'
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined = db.Column(db.DateTime, nullable=False)
    # When a user has parted a conversation, they no longer should see messages
    status = db.Column(db.Integer, nullable=False, default=STATUS_ACTIVE)
    __table_args__ = (db.PrimaryKeyConstraint('user_id', 'conversation_id', name="pk_conversation_users"),)
    # Relationship attributes
    user = db.relationship("User", foreign_keys=[user_id])
