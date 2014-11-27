# -*- coding: utf-8 -*-
import hashlib
import hmac

from blacktechies import app

class HMACHashBase(object):
    default_keys = ('key', 'hash_algo', 'hex_digest', 'errors')

    def __init__(self, key=None, hash_algo=None, hex_digest=True, errors=False):
        self.key = key if key else app.secret_key
        self.hash_algo = hash_algo
        self.hex_digest = hex_digest
        self.errors = errors

    def _defaults(self, **kwargs):
        defaults = {}
        keys = self.default_keys
        for key in keys:
            if key in kwargs and kwargs[key] is not None:
                defaults[key] = kwargs[key]
            else:
                defaults[key] = getattr(self, key)
        return tuple([defaults[key] for key in keys])


class HMACHash(HMACHashBase):
    def __call__(self, raw, **kwargs):
        kwargs['raw'] = raw
        return self.make_digest(**kwargs)

    def make_digest(self, raw, key=None, hash_algo=None, hex_digest=None, errors=None):
        kwargs = locals()
        del(kwargs['self'])
        key, hash_algo, hex_digest, errors = self._defaults(**kwargs)
        digest = None
        try:
            hashed = hmac.new(key, raw, hash_algo)
            digest = hashed.hexdigest() if hex_digest else hashed.digest()
        except:
            if errors:
                raise
        return digest


class HMACHashMatch(HMACHashBase):
    def __call__(self, digest, raw, **kwargs):
        kwargs['digest'] = digest
        kwargs['raw'] = raw
        return self.match_digest2val(**kwargs)

    def match_digest2val(self, digest=None, raw=None, key=None, hash_algo=None, hex_digest=None, errors=None):
        """Verifies that a digest matches the the hash for the 'raw'
        value.

        The 'raw' value is hashed internally within the function.

        For Python < 2.7.8, this is subject to a timing attack and should
        not be used for items which need to be cryptographically
        secure. The :mod:'itsdangerous' module should be used instead.
        """
        if digest is None or raw is None:
            raise ValueError("Must supply hashed value and unhashed base value")

        kwargs = locals()
        del(kwargs['self'])
        key, hash_algo, hex_digest, errors = self._defaults(**kwargs)
        is_match = False
        assert key is not None
        try:
            r = hmac.new(key, raw, hash_algo)
            raw_digest = r.hexdigest() if hex_digest else r.digest()
            is_match = self.compare_digest(digest, raw_digest)
        except:
            if errors:
                raise
        return is_match


    def compare_digest(self, x, y):
        if hasattr(hmac, 'compare_digest'):
            return hmac.compare_digest(x, y)

        if len(x) != len(y):
            return False

        assert len(x) != 0
        is_match = True
        for a, b in zip(x, y):
            is_match = (a == b) and is_match
        return is_match

hmac_match = HMACHashMatch()
hmac_hash = HMACHash()
