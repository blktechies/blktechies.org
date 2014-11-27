import pytest
import hmac

import blacktechies


def test_hmac_validation():
    test_str = 'test'
    hexdigest = blacktechies.utils.validation.hmac_hash(test_str)
    is_match = blacktechies.utils.validation.hmac_match(hexdigest, test_str, errors=True)
    assert is_match == True

    digest = blacktechies.utils.validation.hmac_hash(test_str, hex_digest=False)
    is_match = blacktechies.utils.validation.hmac_match(digest, test_str, errors=True, hex_digest=False)
    assert is_match == True

    digest = blacktechies.utils.validation.hmac_hash(test_str, hex_digest=False)
    is_match = blacktechies.utils.validation.hmac_match(digest, test_str + test_str, errors=True, hex_digest=False)
    assert is_match == False

    hexdigest = blacktechies.utils.validation.hmac_hash(test_str)
    is_match = blacktechies.utils.validation.hmac_match(digest, test_str + test_str, errors=True)
    assert is_match == False
