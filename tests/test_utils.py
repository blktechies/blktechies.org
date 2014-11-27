import pytest
import hmac

import blacktechies


def test_hmac_validation():
    test_str = 'test'
    hexdigest = hmac.new('', test_str).hexdigest()
    is_match = blacktechies.utils.validation.hmac_match(hexdigest, test_str, errors=True)
    assert is_match == True

    digest = hmac.new('', test_str).digest()
    is_match = blacktechies.utils.validation.hmac_match(digest, test_str, errors=True, hex_digest=False)
    assert is_match == True

    digest = hmac.new('', test_str).digest()
    is_match = blacktechies.utils.validation.hmac_match(digest, test_str + test_str, errors=True, hex_digest=False)
    assert is_match == False
