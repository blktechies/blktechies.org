import email
from datetime import datetime

from blacktechies.database import db
from blacktechies.models.user import User, UserEmail
from blacktechies.utils import html_sanitizer

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

    ACTIVE = 0
    PENDING = 1
    DECLINED = 2
    NEEDS_PARSE = 3

    statuses = {
        ACTIVE: 'active',
        PENDING: 'pending',
        DECLINED: 'declined',
        NEEDS_PARSE: 'needs parse',
    }


class JobSubmissionType(JobOption):
    _option_key = 'types'

    EMAIL = 0
    WEB = 1

    types = {
        EMAIL: 'email',
        WEB: 'web',
    }


class JobPosting(db.Model):
    __tablename__ = 'job_postings'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(252), nullable=False)
    body = db.Column(db.Text, nullable=False)
    posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Integer, nullable=False, default=JobStatus.PENDING)
    email_body = db.Column(db.Text)
    posted_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    # relationship columns
    user = db.relationship('User', uselist=False)
    status_changes = db.relationship('JobPostingStatusChange')

    def __repr__(self):
        summary = ''
        if self.title:
            summary = self.title
        elif self.body:
            summary = self.body[:50]
        return '<Job %r: %r>' % (self.id, summary)

class JobPostingEmailSubmission(db.Model):
    __tablename__ = 'job_posting_email_submissions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    email_id = db.Column(db.Integer, db.ForeignKey('user_emails.id'), nullable=False, index=True)
    subject = db.Column(db.String(252), nullable=True, index=True)
    email_body = db.Column(db.Text, nullable=False) # always unsafe to print to client
    status = db.Column(db.Integer, nullable=False, default=JobStatus.NEEDS_PARSE, index=True)
    html = db.Column(db.Text)
    plain_text = db.Column(db.Text)
    created = db.Column(db.DateTime)
    # relationship columns
    from_user = db.relationship('User', uselist=False)
    from_email = db.relationship('UserEmail', uselist=False)

    def __init__(self, **kwargs):
        super(JobPostingEmailSubmission, self).__init__(**kwargs)
        self.created = kwargs.get('created', datetime.now())

    def _raw_part(self, part_mime_type):
        msg = email.message_from_string(self.email_body)
        body = None
        for part in msg.walk():
            if part.get_content_type == part_mime_type:
                encoded_body = part.get_payload()
                body = quopri.decodestring(encoded_body)
        return body

    def raw_html(self):
        return self._raw_part('text/html')

    def raw_text(self):
        return self._raw_part('text/html')

    def clean_html(self):
        return self._clean_html(self.raw_html())

    def _clean_html(self, html):
        return html_sanitizer.clean_html(html)

    def separate_text_fields(self):
        if self.html or self.plain_text:
            raise ValueError("This submission has already been separated")
        self.plain_text = self.raw_text()
        self.html = self.clean_html()

    def get_headers(self):
        msg = email.message_from_string(self.email_body)
        headers = {}
        for header in ('subject', 'from', 'to', 'date', 'received', 'message-id'):
            headers[header] = msg.get_all(header) or []
        return headers

    def get_header(self, header):
        pass

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
