from py2neo import Subgraph
from . import db
from .utils import handle_error
from .models import User, MiniApp, TObject
from .constants import ERROR_CODE, ROLE


def get_user(uid):
    try:
        # TODO assert no label TObject
        return User.match(db).where("_.uid = '{uid}'".format(uid=uid)).first()
    except Exception as e:
        handle_error(e, ERROR_CODE.USER_NOT_FIND)


def get_tobject(oid):
    try:
        # TODO assert no label TObject
        return TObject.match(db).where("_.oid = '{oid}'".format(oid=oid)).first()
    except Exception as e:
        handle_error(e, ERROR_CODE.TOBJECT_NOT_FIND)


def get_app(aid):
    try:
        return MiniApp.match(db, aid).where("_.aid = '{aid}'".format(aid=aid)).first()
    except Exception as e:
        handle_error(e, ERROR_CODE.APP_NOT_FIND)


def get_platform_root_key(uid):
    user = get_user(uid)
    return {
        'platform_root_key': user.generate_platform_root_key()
    }


def get_mini_app_key(uid, aid, platform_root_key):
    user = get_user(uid)
    user.verify_key(platform_root_key)
    app = get_app(aid)
    return {
        'mini_app_key': user.generate_app_key(app)
    }


def get_obj(oid, obj_parser):
    args = obj_parser.parse_args()
    uid = args['uid']
    mini_app_key = args['MiniAppKey']
    user = get_user(uid)
    data = user.verify_key(mini_app_key)
    if oid == 'root':
        obj = get_app(data['_id'])
    else:
        obj = get_tobject(data['_id'])
    return user, obj, data['role']


def serialize_objs(user, objs, role):
    return [obj.serialize(user, role) for obj in objs]


def handle_obj_get(user, obj, role):
    return serialize_objs(user, list(obj.children), role)


def handle_obj_delete(obj, role, oid_list):
    print(obj, role, oid_list)
    if role < ROLE.ADMIN:
        handle_error('Permission deny. You do not have write permission.', ERROR_CODE.NO_WRITE_PERMISSION)
    children = [child for child in list(obj.children) if child.oid in set(oid_list)]
    all_children = []
    for child in children:
        all_children += child.get_all_children()
    all_children += children
    print([child.__node__ for child in all_children])
    subgraph = Subgraph([child.__node__ for child in all_children])
    try:
        db.delete(subgraph)
    except Exception as e:
        handle_error(e, ERROR_CODE.NEO4J_PUSH_FAILURE)
    return 'SUCCESS'


def handle_obj_replace(user, obj, role, oid_list, children):
    handle_obj_delete(obj, role, oid_list)
    db.pull(obj)
    return handle_obj_post(user, obj, role, children)


def handle_obj_post(user, obj, role, children):
    """
    Children example:
    [{'labels': ['Person'], 'properties': {'age':10, 'name':'owen'}}]
    """
    if role < ROLE.ADMIN:
        handle_error('Permission deny. You do not have write permission.', ERROR_CODE.NO_WRITE_PERMISSION)
    objs = []
    for child in children:
        child_obj = TObject.new(child['labels'], child['properties'])
        obj.children.add(child_obj)
        objs.append(child_obj)
    try:
        db.push(obj)
    except TypeError as e:
        handle_error(e, ERROR_CODE.UNSUPPORTED_DATA_TYPE)
    except Exception as e:
        handle_error(e, ERROR_CODE.NEO4J_PUSH_FAILURE)
    return serialize_objs(user, objs, role)
