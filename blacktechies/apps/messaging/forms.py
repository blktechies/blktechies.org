from wtforms import validators
from wtforms.fields import StringField, TextAreaField, HiddenField

from blacktechies.utils.validation import FormTimestamp
from blacktechies.utils.form import Form, generate_ts


class NewMessageForm(Form):
    """ A class for sending a message to another user """
    subject = StringField('Subject', validators=[
        validators.optional(),
        validators.length(max=200, message="The subject is too long")])
    body = TextAreaField('Your Message', validators=[
        validators.required(),
        validators.length(max=5*1024, message="Your message is too long")])
    timestamp = HiddenField(default=generate_ts(), validators=[
        validators.required(),
        FormTimestamp(days=1, message="This form has expired, please reload the page.")])
    to_usernames = TextAreaField(validators=[validators.required(message="You have to send this message to someone")])

    def filtered_usernames(self, usernames_str=None):
        if usernames_str is None:
            usernames_str = self.to_usernames.data or ''
        names = map(usernames_str.strip, usernames_str.split(','))
        return names


class ReplyForm(Form):
    body = TextAreaField('Your Message', validators=[
        validators.required(message="You must include a message"),
        validators.length(max=5*1024, message="Your message is too long")])
    timestamp = HiddenField(default=generate_ts(), validators=[
        validators.required(),
        FormTimestamp(days=1, message="This form has expired, please reload the page.")])
    conversation_id = HiddenField(validators=[validators.required(message="Replies to a thread must have a conversation_id")])
