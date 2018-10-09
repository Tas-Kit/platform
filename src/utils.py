from . import blowfish
import base64
import json
from .constants import ERROR_CODE, ROLE
from werkzeug.exceptions import BadRequest


def handle_error(error, error_code):
    print('error_code', error_code, error)
    bad_request = BadRequest()
    bad_request.data = {
        'detail': str(error),
        'error_code': error_code
    }
    raise bad_request


def assert_admin(role):
    if role < ROLE.ADMIN:
        handle_error('Permission deny. You do not have write permission.', ERROR_CODE.NO_WRITE_PERMISSION)


def assert_higher_permission(role, target_role):
    if role <= target_role:
        handle_error('Permission deny. You need higher permission to perform this action.', ERROR_CODE.REQUIRE_HIHGER_PERMISSION)


def encrypt(message):
    message = json.dumps(message).encode('utf-8')
    space = (int(len(message) / 8) + 1) * 8
    code = blowfish.encrypt(message.ljust(space))
    return base64.b64encode(code).decode('utf-8')


def decrypt(code):
    code = base64.b64decode(code.encode('utf-8'))
    message = blowfish.decrypt(code).decode('utf-8')
    return json.loads(message)
