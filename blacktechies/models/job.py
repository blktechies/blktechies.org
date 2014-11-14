from sqlalchemy import Column, Integer, String, Text, DateTime
from blacktechies.database import Base

STATUS_ACTIVE = 0
STATUS_PENDING = 1
STATUS_DECLINED = 2

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    body = Column(Text)
    email_body = Column(Text)
    posted = Column(DateTime)
    status = Column(Integer)

    def __init__(self, title=None, body=None, email_body=None, posted=None, status=None):
        self.title = title
        self.body = body
        self.email_body = email_body
        self.posted = posted
        self.status = status

    def __repr__(self):
        return '<Job %r: %r>' % (self.id, self.title)
