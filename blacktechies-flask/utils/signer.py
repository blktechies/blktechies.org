# -*- coding: utf-8 -*-
import string
from random import choice

from itsdangerous import Signer, TimestampSigner
from blacktechies import app

signer = Signer(app.secret_key)
time_signer = TimestampSigner(app.secret_key)

_random_string = lambda length: "".join(choice(string.ascii_letters + string.digits)
form_timestamp = time_signer.sign()
