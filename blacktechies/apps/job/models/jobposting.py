# -*- coding: utf-8 -*-
import email
import quopri
from datetime import datetime

from blacktechies.database import db
from blacktechies.apps.user.models import User, UserEmail
from blacktechies.apps.job.models.emailedjobsubmission import JobPostingEmailSubmission
# What a hack...
class JobOption(object):
    _option_key = None

    def __init__(self, option):
        if option not in self[_option_key]:
            raise KeyError(msg='No such option: %r' % option)
        self.value = option

    def __repr__(self):
        return self.options[self.value]

class JobStatus(JobOption):
    _option_key = 'statuses'

class JobPosting(db.Model):
    STATUS_ACTIVE = 1
    STATUS_EXPIRED = 2
    STATUS_DECLINED = 3
    STATUS_SPAM = 4
    STATUS_NEEDS_APPROVAL = 5

    STATUSES = {
        STATUS_ACTIVE: 'active',
        STATUS_EXPIRED: 'expired',
        STATUS_DECLINED: 'declined',
        STATUS_SPAM: 'spam',
        STATUS_NEEDS_APPROVAL: 'needs approval',
    }

    SOURCE_WEB = 1
    SOURCE_EMAIL = 2
    SOURCE_API = 3

    SOURCES = {
        SOURCE_WEB: 'web',
        SOURCE_EMAIL: 'email',
        SOURCE_API: 'API',
    }

    __tablename__ = 'job_postings'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(252), nullable=False)
    body = db.Column(db.Text, nullable=False)
    posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Integer, nullable=False, default=STATUS_NEEDS_APPROVAL, index=True)
    submission_id = db.Column(db.Integer, db.ForeignKey(JobPostingEmailSubmission.__tablename__ + '.id'), nullable=True)
    posted_by_user_id = db.Column(db.Integer, db.ForeignKey(User.__tablename__ + '.id'), index=True)
    moderator_user_id = db.Column(db.Integer, db.ForeignKey(User.__tablename__ + '.id'))
    source = db.Column(db.Integer, default=SOURCE_WEB)
    # relationship columns
    posted_by = db.relationship('User', uselist=False, foreign_keys=[posted_by_user_id], back_populates="job_postings")
    moderated_by = db.relationship('User', uselist=False, foreign_keys=[moderator_user_id])
    submission = db.relationship('JobPostingEmailSubmission', uselist=False)
    status_changes = db.relationship('JobPostingStatusChange')

    def __repr__(self):
        summary = ''
        if self.title:
            summary = self.title
        elif self.body:
            summary = self.body[:50]
        return '<Job %r: %r>' % (self.id, summary)

    @db.validates('title', 'body')
    def clean(self, key, html):
        html = html_cleaner.strip_tags(html)
        if key == 'title':
            assert len(html) > 10
        elif key == 'body':
            assert len(html) > 200

        setattr(self, key, html)

class JobPostingStatusChange(db.Model):
    __tablename__ = 'job_posting_status_changes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), index=True, nullable=False)
    status = db.Column(db.Integer, index=True, nullable=False)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('User', uselist=False)

    def __repr__(self):
        return '<Job status change to: %s on %s by id:%d>' % (JobStatus(self.status), self.updated, self.user_id)
