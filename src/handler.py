from time import time
from . import db, blowfish
from .utils import handle_error, decrypt
from .models import User, MiniApp, TObject
from .constants import ERROR_CODE


def get_user(uid):
    try:
        # TODO assert no label TObject
        return User.match(db).where("_.uid = '{uid}'".format(uid=uid)).first()
    except Exception as e:
        handle_error(e, ERROR_CODE.USER_NOT_FIND)


def get_app(aid):
    try:
        return MiniApp.match(db, aid).where("_.aid = '{aid}'".format(aid=aid)).first()
    except Exception as e:
        handle_error(e, ERROR_CODE.APP_NOT_FIND)


def verify_platform_root_key(uid, platform_root_key):
    try:
        data = decrypt(platform_root_key)
    except Exception as e:
        handle_error(e, ERROR_CODE.UNABLE_TO_DECRYPT)
    if uid != data['uid']:
        handle_error("User does not match the platform root key.", ERROR_CODE.USER_NOT_MATCH)
    if int(time()) > data['exp']:
        handle_error("Platfor root key expired.", ERROR_CODE.PLATFORM_KEY_EXPIRED)


def get_platform_root_key(uid):
    user = get_user(uid)
    return {
        'platform_root_key': user.generate_platform_root_key()
    }


def get_mini_app_key(uid, aid, platform_root_key):
    user = get_user(uid)
    app = get_app(aid)
    verify_platform_root_key(uid, platform_root_key)
    return {
        'mini_app_key': user.generate_app_key(app)
    }
