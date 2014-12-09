import email
from datetime import datetime

from blacktechies.database import db
from blacktechies.apps.user.models import User, UserEmail
from blacktechies.utils.email import EmailParser
from blacktechies.utils.html import html_cleaner

class JobPostingEmailSubmission(db.Model):
    ACTIVE = 0
    PENDING = 1
    DECLINED = 2
    NEEDS_PARSE = 3

    STATUSES = {
        ACTIVE: 'active',
        PENDING: 'pending',
        DECLINED: 'declined',
        NEEDS_PARSE: 'needs parse',
    }

    __tablename__ = 'job_posting_email_submissions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.__tablename__ + '.id'), nullable=False, index=True)
    email_id = db.Column(db.Integer, db.ForeignKey(UserEmail.__tablename__ + '.id'), nullable=False, index=True)
    subject = db.Column(db.String(252), nullable=True, index=True)
    email_body = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=NEEDS_PARSE, index=True)
    created = db.Column(db.DateTime)
    # relationship columns
    from_user = db.relationship(User, uselist=False)
    from_email = db.relationship(UserEmail, uselist=False)

    def email_obj(self):
        return email.message_from_string(self.email_body)

    def raw_html(self):
        parser = EmailParser(self.email_body)
        return parser.get_part(EmailParser.MIME_HTML)

    def raw_text(self):
        parser = EmailParser(self.email_body)
        return parser.get_part(EmailParser.MIME_PLAINTEXT)

    def get_clean_html(self):
        html = self.raw_html()
        return html.html_cleaner(html)
