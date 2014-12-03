from passlib.context import CryptContext

from blacktechies import app

context = CryptContext(schemes=[app.config['USER_PASSWORD_HASH']])
encrypt_password = context.encrypt
verify_password = context.verify
