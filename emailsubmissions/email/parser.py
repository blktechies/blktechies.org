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


class EmailParser(object):
    FROM_ADDR = 'from'
    SUBJECT = 'subject'
    TO_ADDR = 'to'
    DATE = 'date'
    RECEIVED = 'received'
    MESSAGE_ID = 'message-id'

    HEADERS = (
        FROM_ADDR, SUBJECT, TO_ADDR, DATE, RECEIVED, MESSAGE_ID
    )

    MIME_HTML = 'text/html'
    MIME_PLAINTEXT = 'text/plain'

    def __init__(self, msg):
        self.msg = msg

    def get_part(self, part_mime_type):
        msg = self.email_obj(self.email_body)
        body = None
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == part_mime_type:
                    charset = part.get_content_charset()
                    encoded_body = part.get_payload(decode=True)
                    body = str(encoded_body, charset)
        else:
            raise TypeError("Message is not multi-part")
        return body

    def get_headers(self):
        headers = {}
        for header in self.HEADERS:
            headers[header] = self.msg.get_all(header) or []
        return headers

    def get_header(self, header, only_first=False, default=None):
        headers = self.msg.get_all(header)
        if only_first:
            try:
                return header[0]
            except IndexError:
                return default
        else:
            return headers

    def get_first(self, header, default=None):
        return self.get_header(header, only_first=True, default=default)

    def get_sender(self):
        sender = self.get_first(self.FROM_ADDR, default='')
        sender_address = email.utils.parseaddr(sender)[1]
        return sender_address

    def get_subject(self):
        return self.get_first(self.SUBJECT, default=None)

    def get_body(self, prefer_plaintext=True):
        mime = self.MIME_PLAINTEXT if prefer_plaintext else self.MIME_HTML
        body = self.get_part(mime)
        return body
