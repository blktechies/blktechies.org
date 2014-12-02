from datetime import timedelta
from blacktechies.utils.signer import time_signer
from blacktechies.utils.string import random_string


class FormSigner(object):
    def generate_ts(self):
        random = random_string(10)
        return time_signer.sign(random)

    def validate_ts(self, value, max_age=0, max_seconds=0, max_minutes=0, max_hours=0, max_days=0, max_weeks=0):
        """Validates that a form field with a timestamp has been submitted
        within the specified time range.

        Named arguments are passed into :cls:datetime.timedelta.
        """
        if not max_age:
            max_age = timedelta(days=max_days, seconds=max_seconds, minutes=max_minutes, hours=max_hours, weeks=max_weeks).total_seconds()
        if max_age <= 0:
            raise ValueError("Expiration of '%s' time was invalid." % max_age)

        return time_signer.validate(value, max_age=max_age)

_form_signer = FormSigner()
generate_ts = _form_signer.generate_ts
validate_ts = _form_signer.validate_ts
