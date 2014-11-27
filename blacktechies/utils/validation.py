# -*- coding: utf-8 -*-
import hashlib
import hmac
from binascii import unhexlify

from flask import current_app
from blacktechies import app

class HMACHashMatch(object):
    def __init__(self, key=None, hash_algo=None, hex_digest=True, errors=False):
        self._key = key if key else app.secret_key
        self._hash_algo = hash_algo
        self._hex_digest = hex_digest
        self._errors = errors

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

        if key is None:
            key = self._key
        if hash_algo is None:
            hash_algo = self._hash_algo
        if hex_digest is None:
            hex_digest = self._hex_digest
        if errors is None:
            errors = self._errors

        is_match = False
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

        if not (isinstance(x, bytes) and isinstance(y, bytes)):
            err = TypeError("Both inputs must be hexstring or type bytes")
            if (isinstance(x, basestring) and isinstance(y, basestring)):
                try:
                    x = unhexlify(x)
                    y = unhexlify(y)
                except:
                    raise err
            else:
                raise err
            x = bytearray(x)
            y = bytearray(y)
        if len(x) != len(y):
            return False
        assert (isinstance(x, bytes) and isinstance(y, bytes)) == True

        result = 0
        for a, b in zip(x, y):
            result |= a ^ b
        return result == 0

hmac_match = HMACHashMatch()
