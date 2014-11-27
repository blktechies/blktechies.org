import string
from random import choice

class RandomString(object):
    def __init__(self, chars=None):
        self.chars = chars if chars is not None else string.ascii_letters + string.digits

    def __call__(self, length):
        return self.random_string(length)

    def random_string(self, length, chars=None):
        if chars is None:
            chars = self.chars

        return ''.join(choice(chars) for _ in range(length))

random_string = RandomString()
