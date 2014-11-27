from flask import jsonify

def json_response(code=200, body=None, errors=None, extra=None):
    if not errors:
        errors = []
    elif not isinstance(errors, list):
        errors = [errors, ]
    if not extra:
        extra = None

    response_data = {
        'meta': {
            'status_code': code,
            'errors': errors,
        },
        'data': body,
        'extra': extra,
    }

    response = jsonify(response_data)
    response.status_code = code
    return response

def json_error(code=400, errors=None, **kwargs):
    if code < 400:
        raise ValueError("json_error should only be called for errors")
    kwargs['code'] = code
    kwargs['errors'] = errors
    response = json_response(**kwargs)
    return response
