"""This module is responsible for retrieving new email submissions off of the email server"""

import imaplib
import email
import quopri
import logger


class EmailFetcher(object):
    def __init__(self, host=None, use_ssl=True):
        self.host = host
        self.use_ssl = use_ssl
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
        data = self._check_ok(self.client.search(None, '(UNSEEN)'))
        msg_ids = data[0].split()
        for msg_id in msg_ids:
            yield self.retrieve_message(msg_id)

    def retrieve_message(self, msg_id):
        data = self._check_ok(self.client.fetch(msg_id, '(RFC822)'))
        return email.message_from_string(data[0][1])

    def _check_ok(self, imap_response):
        ok, data = imap_response
        if ok != 'OK':
            raise ValueError("Expected IMAP:OK and got '%s' instead. Data:(%s)" % (ok, data))
        return data

if __name__ == '__main__':
    FORMAT = "%(asctime)-15s %(message)s"
    logging.basicConfig(format=FORMAT)
    fetcher = EmailFetcher('imap.gmail.com')
    if fetcher.connect():
        for msg in fetcher.get_messages():
            posting = JobPostingEmailSubmission()
            posting.email_body = msg.as_string()
            headers = posting.get_headers()
            email_from = email.utils.parseaddr(headers.get('from', ''))[1]
            if not email_from:
                logging.warning("Email message: %s did not have a from header (%s)", (headers.get('subject', '')[:50], headers))
                continue
            posting.subject = headers.get('subject', "(no subject)")
            # See if we can find the user by their email address.
            known_address = UserEmail.query.filter_by(email=email_from)
            if known_address:
                posting.email_id = known_address.id
                posting.user_id = known_address.user_id
            else: #We need to implicitly create an inactive user
                new_user = User.new_inactive_user(email=email_from)
                db.session.add(new_user)
                db.session.commit()
