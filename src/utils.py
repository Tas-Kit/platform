from werkzeug.exceptions import BadRequest


def handle_error(error, error_code):
    print('error_code', error_code, error)
    bad_request = BadRequest()
    bad_request.data = {
        'detail': str(error),
        'error_code': error_code
    }
    raise bad_request
