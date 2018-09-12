from werkzeug.exceptions import BadRequest
from . import blowfish
import base64
import json


def handle_error(error, error_code):
    print('error_code', error_code, error)
    bad_request = BadRequest()
    bad_request.data = {
        'detail': str(error),
        'error_code': error_code
    }
    raise bad_request


def encrypt(message):
    message = json.dumps(message).encode('utf-8')
    space = (int(len(message) / 8) + 1) * 8
    code = blowfish.encrypt(message.ljust(space))
    return base64.b64encode(code).decode('utf-8')


def decrypt(code):
    code = base64.b64decode(code.encode('utf-8'))
    message = blowfish.decrypt(code).decode('utf-8')
    return json.loads(message)
