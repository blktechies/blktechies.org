from blacktechies.models.user import User
from blacktechies import app

class BlacktechiesLoginManager(object):
    enable_tokens = True
    token_hasher = None

    def __init__(self, login_manager):
        self.login_manager = login_manager

        @login_manager.user_loader
        def user_loader(string_id):
            try:
                user_id = int(string_id)
            except:
                user_id = 0
            return self.find_by_id(user_id)

        @login_manager.token_loader
        def token_loader(token):
            if not self.token_hasher and self.enable_tokens:
                return None
            user_id = self.token_hasher.decrypt_id(token, errors=False)
            return self.find_by_id(user_id)

    def find_by_id(self, user_id):
        if not user_id:
            return None
        return User.query.get(user_id) or None
