# -*- coding: utf-8 -*-
"""This module is responsible for retrieving new email submissions off of the email server"""

import imaplib
import email
import quopri
import logging

class EmailFetcher(object):
    def __init__(self, host=None, use_ssl=True):
        self.host = host
        self.use_ssl = use_ssl
        self.client = None
        self.init()

    def init(self):
        if self.client:
            self.close_client()
        self.client = imaplib.IMAP4_SSL(host=self.host) if self.use_ssl else imaplib.IMAP4(host=self.host)

    def close(self):
        if self.client:
            try:
                ok, data = self.client.close()
            except:
                pass
            try:
                ok, data = self.client.logout()
            except:
                pass

    def connect(self, username, password):
        ok, data = self.client.login(username, password)
        return ok == 'OK'

    def get_messages(self):
        data = self._check_ok(self.client.select())
        data = self._check_ok(self.client.search(None, '(ALL)'))
        msg_ids = data[0].split()
        for msg_id in msg_ids:
            yield (msg_id, self.retrieve_message(msg_id))

    def retrieve_message(self, msg_id):
        data = self._check_ok(self.client.fetch(msg_id, '(RFC822)'))
        return email.message_from_string(data[0][1])

    def _check_ok(self, imap_response):
        ok, data = imap_response
        if ok != 'OK':
            raise ValueError("Expected IMAP:OK and got '%s' instead. Data:(%s)" % (ok, data))
        return data

if __name__ == '__main__' and __package__ is None:
    # PYTHONPATH magic to add the blacktechies folder from the parent
    # sys.path[0] would usually include this folder, but we really want it to appear
    # that we're not in the folder at all.
    import os
    import sys
    sys.path[0] = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]

    from blacktechies.database import db
    from blacktechies.models.user import User, UserEmail
    from blacktechies.models.job import JobPostingEmailSubmission

    FORMAT = "%(asctime)-15s %(message)s"
    logging.basicConfig(format=FORMAT)
    fetcher = EmailFetcher('imap.gmail.com')
    username = os.getenv('BLACKTECHIES_EMAIL_USERNAME')
    password = os.getenv('BLACKTECHIES_EMAIL_PASSWORD')
    new_users = {}

    if fetcher.connect(username, password):
        for msg_id, msg in fetcher.get_messages():
            posting = JobPostingEmailSubmission()
            posting.email_body = msg.as_string()
            headers = posting.get_headers()
            # FIXME -- does not separate out the email it seems.
            from_email = email.utils.parseaddr(headers.get('from', '')[0])[1]
            if not from_email:
                logging.warning("Email message: %s did not have a from header (%s)", (headers.get('subject', '')[:50], headers))
                print "Email message: %s did not have a from header (%s)", (headers.get('subject', '')[:50], headers)
                continue
            posting.subject = headers.get('subject', None)[0]
            # See if we can find the user by their email address.
            known_address = UserEmail.query.filter_by(email=from_email).first()
            if known_address:
                posting.from_email = known_address
                posting.from_user = known_address.user
            elif from_email in new_users:
                posting.from_user = new_users[from_email]
                # Because the user is new, they should only have 1 email address
                posting.from_email = posting.user.email_addresses[0]
            else: #We need to implicitly create an inactive user
                new_user = User.new_inactive_user()
                email = UserEmail(email=from_email, is_primary=True)
                new_user.email_addresses = [email]
                posting.from_user = new_user
                posting.from_email = email
                db.session.add(new_user)
                new_users[from_email] = new_user
            db.session.add(posting)
        db.session.commit()
