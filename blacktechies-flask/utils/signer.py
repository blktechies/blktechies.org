# -*- coding: utf-8 -*-

from random import choice

from itsdangerous import Signer, TimestampSigner
from blacktechies import app

signer = Signer(app.secret_key)
time_signer = TimestampSigner(app.secret_key)
form_timestamp = time_signer.sign()
