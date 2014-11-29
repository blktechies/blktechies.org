import email
import string
from random import choice

from django.db import models
from django.contrib.auth.models import User
from users.models import UserAlternateEmail

class EmailSubmission(models.Model):
    NEEDS_MODERATION = 0
    ADDED = 1
    DELETED = 2
    EXPIRED = 3
    DECLINED = 4
    SPAM = 5
    STATUS_CHOICES = (
        (NEEDS_MODERATION, 'needs moderation'),
        (ADDED, 'added'),
        (DELETED, 'deleted'),
        (EXPIRED, 'expired'),
        (DECLINED, 'declined'),
        (SPAM, 'spam'),
    )

    id = models.AutoField(primary_key=True)
    from_user = models.ForeignKey(User, db_index=True)
    from_email = models.ForeignKey(UserEmail)
    moderated_by_user = models.ForeignKey(User)
    status = models.IntegerField(db_index=True, choices=STATUS_CHOICES)
    subject = models.charField(max_length=200)
    email_body = models.TextField(max_length=1024*30)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def email_obj(self):
        return email.message_from_string(self.email_body)

    def raw_html(self):
        return self._raw_part('text/html')

    def raw_text(self):
        return self._raw_part('text/plain')

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

    @classmethod
    def from_email_message(cls, email_msg):
        msg = email.parser.EmailParser(email_msg)
        submission.subject = parser.get_subject()
        from_email = parser.get_sender()
        user = User.objects.get(email=from_email)
        if not user:
            random_suffix = ''.join(choice(string.ascii_letters + string.digits) for _ in range(16))
            user = User('anonymous_' + random_suffix, email=from_email)
            user.set_unusable_password()
        submission.user = user
