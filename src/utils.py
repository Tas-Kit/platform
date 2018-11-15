import json

import traceback as tb

import base62

from werkzeug.exceptions import BadRequest

from . import blowfish

from .constants import ERROR_CODE, ROLE


def handle_error(error, error_code):
    print('error_code', error_code, error)
    # tb.print_exc(error)
    bad_request = BadRequest()
    bad_request.data = {'detail': str(error), 'error_code': error_code}
    raise bad_request


def assert_standard(role):
    if role is None or role < ROLE.STANDARD:
        handle_error('Permission deny. You do not have read permission.',
                     ERROR_CODE.NO_READ_PERMISSION)


def assert_admin(role):
    assert_standard(role)
    if role < ROLE.ADMIN:
        handle_error('Permission deny. You do not have write permission.',
                     ERROR_CODE.NO_WRITE_PERMISSION)


def assert_higher_permission(role, target_role):
    if role is None or role <= target_role:
        handle_error(
            'Permission deny. '
            'You need higher permission to perform this action.',
            ERROR_CODE.REQUIRE_HIHGER_PERMISSION)


def encrypt(message):
    message = json.dumps(message).encode('utf-8')
    space = (int(len(message) / 8) + 1) * 8
    code = blowfish.encrypt(message.ljust(space))
    return base62.encodebytes(code)


def decrypt(code):
    code = base62.decodebytes(code)
    message = blowfish.decrypt(code).decode('utf-8')
    return json.loads(message)
