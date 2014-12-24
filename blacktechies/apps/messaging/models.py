import datetime
import time
from blacktechies.database import db


class Message(db.Model):
    """Model representing a message from one user to one or more
    users. The `is_read` flag only makes sense when the conversation
    has two people."""

    STATUS_ACTIVE = 0
    STATUS_DELETED = 1

    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
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
        self.status = self.STATUS_DELETED

    @classmethod
    def from_string(cls, message, subject=None, **kwargs):
        msg_args = {
            'body': message,
            'status': cls.STATUS_ACTIVE,
            'timestamp': datetime.datetime.now(),
            'is_read': False,
        }
        msg_args.update(kwargs)
        return cls(**msg_args)

    @classmethod
    def most_recent(cls, conversations, limit=None):
        if limit is None:
            limit = 1
        selects = []
        seen_ids = set()
        # These are dealing with the SQLAlchemy metadata objects and not
        # instances of the class.
        message = db.metadata.tables.get(cls.__tablename__)
        c_meta = db.metadata.tables.get(Conversation.__tablename__)
        for conversation in conversations:
            if conversation.id in seen_ids:
                continue
            seen_ids.add(conversation.id)
            selects.append(
                db.select([message]).where(
                    message.c.conversation_id == c_meta.c.id).limit(limit)
            )
        result = db.engine.execute(db.union_all(*selects))
        if not result or not result.returns_rows:
            raise RuntimeError("Query for most recent messages did not return a valid result")
        message_map = {}
        for row in result.fetchall():
            if row.conversation_id not in message_map:
                message_map[row.conversation_id] = []
            message_map[row.conversation_id].append(row)
        return message_map

    @classmethod
    def for_conversation(cls, conversation, before_id=None, limit=None):
        query = cls.query.filter(cls.conversation_id == conversation.id)
        query.filter(cls.status == cls.STATUS_ACTIVE)
        if before_id:
            query.filter(Message.id < before_id)
        query.order_by(Message.id.desc()).limit(limit)
        return query.all()


class Conversation(db.Model):
    STATUS_ACTIVE = 0
    STATUS_DELETED = 1

    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer, nullable=False, default=STATUS_ACTIVE)
    last_updated = db.Column(db.Integer, nullable=False, default=int(time.time()))
    subject = db.Column(db.Text, nullable=False, default='')
    messages = db.relationship('Message')
    users = db.relationship('User', backref="conversations",
                            secondary="conversations_users")


    def add_user(self, user):
        conv_user = ConversationUser(status=ConversationUser.STATUS_ACTIVE,
                                     joined=datetime.datetime.now())
        conv_user.user = user
        self.users.append(conv_user)

    def has_user(self, user, active_only=True):
        for conv_user in self.users:
            if conv_user.id == user.id:
                if not active_only or (active_only and conv_user.is_active()):
                    return True
        return False

    def remove_user(self, user):
        for conv_user in self.users:
            if conv_user.user_id == user.id:
                conv_user.status = ConversationUser.STATUS_PARTED

    def add_message(self, message):
        self.messages.append(message)

    def new_message(self, message, user):
        m = Message.new_message(message, user=user, conversation=self)
        self.add_message(m)
        return m

    def other_users(self, user):
        others = []
        for other in self.users:
            if other.id != user.id:
                others.append(other)
        return others

class ConversationUser(db.Model):
    """ All of the users who can participate in a conversation.

    All conversations are able to be shared between multiple users.
    """
    STATUS_ACTIVE = 0
    STATUS_PARTED = 1

    __tablename__ = 'conversations_users'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    # When a user has parted a conversation, they no longer should see messages
    status = db.Column(db.Integer, nullable=False, default=STATUS_ACTIVE)
    __table_args__ = (db.UniqueConstraint('user_id', 'conversation_id', name="uix_conversation_users"),)
    # Relationship attributes
    user = db.relationship("User")

    @classmethod
    def exists(cls, user_id, conversation_id):
        return db.exists(ConversationUser.query.filter(db.and_(
            cls.user_id == user_id, cls.conversation_id == conversation_id)))
