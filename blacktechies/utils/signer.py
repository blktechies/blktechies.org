# -*- coding: utf-8 -*-
from itsdangerous import Signer, TimestampSigner, URLSafeSerializer
from blacktechies import app

signer = Signer(app.secret_key)
time_signer = TimestampSigner(app.secret_key)
serializer = URLSafeSerializer(app.secret_key)
