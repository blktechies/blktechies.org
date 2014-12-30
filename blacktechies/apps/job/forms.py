from flask_wtf import Form
from wtforms import validators
from wtforms.fields import StringField, TextAreaField, HiddenField

from blacktechies.utils.validation import FormTimestamp
from blacktechies.utils.form import generate_ts
from blacktechies.utils.html import html_cleaner

class ModerateEmailSubmissionForm(Form):
    """ A class for promoting an emailed job submission into a proper job post """
    title = StringField('Job Post Title', [validators.required(), validators.length(max=250, min=10)])
    body = TextAreaField('Job Post Description', [validators.required(), validators.length(min=140, max=10*1024)])
    submission_id = HiddenField(validators=[validators.required()])
    timestamp = HiddenField(default=generate_ts(), validators=[
        validators.required(),
        FormTimestamp(days=1, message="This form has expired, please retry the submission")])


class NewJobForm(Form):
    timestamp = HiddenField('timestamp', validators=[validators.required(), FormTimestamp(days=1)], default=generate_ts())
    title = StringField('Job Post Title', validators=[
        validators.required(message="Your post must have a title"),
        validators.Length(min=10, max=200, message="Title can be from 10 to 200 characters long")])
    body = TextAreaField('Job Description', validators=[
        validators.required(message="The post must have a description"),
        validators.length(min=140, message="Job post was too small. Please try adding some additional details to the post."),
        validators.length(max=10*1024, message="Job post was too long. Please try writing something shorter than War and Peace.")])
