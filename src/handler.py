import json
from py2neo import Subgraph
from . import db
from .utils import handle_error, assert_admin, assert_higher_permission
from .models import User, MiniApp, TObject
from .constants import ERROR_CODE, ROLE

graph_obj_map = {
    User: {
        'model_name': 'User',
        'id_name': 'uid',
        'error_code': ERROR_CODE.USER_NOT_FIND
    },
    TObject: {
        'model_name': 'TObject',
        'id_name': 'oid',
        'error_code': ERROR_CODE.TOBJECT_NOT_FIND
    },
    MiniApp: {
        'model_name': 'MiniApp',
        'id_name': 'aid',
        'error_code': ERROR_CODE.APP_NOT_FIND
    },
}


def get_graph_obj(_id, model):
    try:
        obj_map = graph_obj_map[model]
        obj = model.match(db).where("_.{id_name} = '{_id}'"
                                    .format(_id=_id, **obj_map)).first()
        if obj is None:
            if model == User:
                obj = User()
                obj.uid = _id
                db.push(obj)
            else:
                handle_error('Unable to find {model_name} with given {id_name} "{_id}"'
                             .format(_id=_id, **obj_map), obj_map['error_code'])
        return obj
    except Exception as e:
        handle_error(e, ERROR_CODE.NEO4J_DATABASE_ERROR)


def get_platform_root_key(uid):
    user = get_graph_obj(uid, User)
    return {
        'platform_root_key': user.generate_platform_root_key()
    }


def get_mini_app(uid, aid, platform_root_key):
    user = get_graph_obj(uid, User)
    user.verify_key(platform_root_key)
    app = get_graph_obj(aid, MiniApp)
    return {
        'mini_app': app.serialize(user)
    }


def get_mini_apps(uid):
    user = get_graph_obj(uid, User)
    return {
        'mini_apps': [app.serialize() for app in list(user.apps)]
    }


def get_obj_by_id(oid, data):
    if oid == 'root':
        obj = get_graph_obj(data['_id'], MiniApp)
    elif oid != data['_id']:
        handle_error('Object ID does not match', ERROR_CODE.ID_NOT_MATCH)
    else:
        obj = get_graph_obj(data['_id'], TObject)
    return obj


def handle_obj_params(oid, obj_parser):
    args = obj_parser.parse_args()
    uid = args['uid']
    key = args['key']
    user = get_graph_obj(uid, User)
    data = user.verify_key(key)
    obj = get_obj_by_id(oid, data)
    params = {
        'user': user,
        'obj': obj,
        'role': data['role'],
        'children': [],
        'oid_list': []
    }
    if 'oid_list' in args and args['oid_list'] is not None:
        params['oid_list'] = args['oid_list']
    if 'children' in args and args['children'] is not None:
        params['children'] = args['children']
    return params


def process_obj_params(func):
    def wrapper(oid, obj_parser):
        params = handle_obj_params(oid, obj_parser)
        return {
            'result': func(**params)
        }
    return wrapper


def serialize_objs(user, objs, role):
    return {obj.oid: obj.serialize(user, role) for obj in objs}


@process_obj_params
def handle_obj_get(user, obj, role, **kwargs):
    return serialize_objs(user, list(obj.children), role)


def execute_obj_delete(obj, role, oid_list):
    assert_admin(role)
    children = [child for child in list(obj.children) if child.oid in set(oid_list)]
    all_children = []
    for child in children:
        all_children += child.get_all_children()
    all_children += children
    subgraph = Subgraph([child.__node__ for child in all_children])
    try:
        db.delete(subgraph)
    except Exception as e:
        handle_error(e, ERROR_CODE.NEO4J_PUSH_FAILURE)
    return 'SUCCESS'


@process_obj_params
def handle_obj_delete(obj, role, oid_list, **kwargs):
    return execute_obj_delete(obj, role, oid_list)


def execute_obj_replace(user, obj, role, oid_list, children):
    execute_obj_delete(obj, role, oid_list)
    db.pull(obj)
    return execute_obj_post(user, obj, role, children)


@process_obj_params
def handle_obj_replace(user, obj, role, oid_list, children, **kwargs):
    return execute_obj_replace(user, obj, role, oid_list, children)


def execute_obj_post(user, obj, role, children):
    """
    Children example:
    [{"labels": ["Person"], "properties": {"age":10, "name":"owen"}}]
    """
    assert_admin(role)
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


@process_obj_params
def handle_obj_post(user, obj, role, children, **kwargs):
    return execute_obj_post(user, obj, role, children)


def execute_obj_patch(obj, role, target_user, target_role):
    """
    Grant target user with target role
    """
    assert_admin(role)
    assert_higher_permission(role, target_role)
    obj_role = target_user.share.get(obj, 'role')
    if obj_role is not None:
        assert_higher_permission(role, obj_role)
    if target_role < ROLE.STANDARD:
        target_user.share.remove(obj)
    else:
        target_user.share.update(obj, role=target_role)
    db.push(target_user)
    return 'SUCCESS'

def handle_obj_patch(oid, obj_parser):
    if oid == 'root':
        handle_error('Unable to share app.', ERROR_CODE.UNABLE_TO_SHARE_APP)
    args = obj_parser.parse_args()
    uid = args['uid']
    key = args['key']
    user = get_graph_obj(uid, User)
    data = user.verify_key(key)
    obj = get_obj_by_id(oid, data)
    params = {
        'obj': obj,
        'role': data['role'],
        'target_user': get_graph_obj(args['target_uid'], User),
        'target_role': args['target_role']
    }
    return {
        'result': execute_obj_patch(**params)
    }
