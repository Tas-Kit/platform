from . import db
from .utils import handle_error
from .models import User, MiniApp, TObject
from .constants import ERROR_CODE


def get_user(uid):
    try:
        return User.match(db).where("_.uid = '{uid}'".format(uid=uid)).first()
    except Exception as e:
        handle_error(e, ERROR_CODE.USER_NOT_FIND)


def get_app(aid):
    try:
        return MiniApp.match(db, aid).where("_.aid = '{aid}'".format(aid=aid)).first()
    except Exception as e:
        handle_error(e, ERROR_CODE.APP_NOT_FIND)


def verify_platform_root_key(platform_root_key):
    print(platform_root_key)


def get_platform_root_key(uid):
    user = get_user(uid)
    return {
        'platform_root_key': user.generate_platform_root_key()
    }


def get_mini_app_key(uid, aid, platform_root_key):
    user = get_user(uid)
    app = get_app(aid)
    return {
        'app_key': user.generate_app_key(app)
    }
