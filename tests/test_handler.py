import json
import uuid
import pytest
from mock import MagicMock, patch
from src import handler, db
from src.models import User, MiniApp, TObject
from src.constants import ROLE
from werkzeug.exceptions import BadRequest


@patch('src.db.push', side_effect=Exception)
def test_execute_obj_post_exception(mock_push):
    children = [{
        'labels': ['Person', 'Worker'],
        'properties': {'age': 10, 'name': 'Owen'}
    }, {
        'labels': ['Car', 'Tesla'],
        'properties': {'age': 3, 'model': 'S'}
    }]
    user = MagicMock()
    obj = MagicMock()
    with pytest.raises(Exception):
        handler.execute_obj_post(user, obj, ROLE.OWNER, children)


@patch('src.db.push', side_effect=TypeError)
def test_execute_obj_post_error(mock_push):
    children = [{
        'labels': ['Person', 'Worker'],
        'properties': {'age': 10, 'name': 'Owen'}
    }, {
        'labels': ['Car', 'Tesla'],
        'properties': {'age': 3, 'model': 'S'}
    }]
    user = MagicMock()
    obj = MagicMock()
    with pytest.raises(BadRequest):
        handler.execute_obj_post(user, obj, ROLE.OWNER, children)


@patch('src.handler.serialize_objs')
@patch('src.db.push')
def test_execute_obj_post_success(mock_push, mock_serialize_objs):
    children = [{
        'labels': ['Person', 'Worker'],
        'properties': {'age': 10, 'name': 'Owen'}
    }, {
        'labels': ['Car', 'Tesla'],
        'properties': {'age': 3, 'model': 'S'}
    }]
    user = MagicMock()
    obj = MagicMock()
    mock_serialize_objs.return_value = 'result'
    assert 'result' == handler.execute_obj_post(user, obj, ROLE.OWNER, children)
    mock_serialize_objs.assert_called_once()
    args = mock_serialize_objs.call_args_list[0][0]
    assert args[0] == user
    person = args[1][0]
    person_labels = list(person.__node__.labels)
    person_labels.remove('TObject')
    person_properties = dict(person.__node__)
    del person_properties['oid']
    assert sorted(person_labels) == sorted(['Person', 'Worker'])
    assert person_properties == {'age': 10, 'name': 'Owen'}
    car = args[1][1]
    car_labels = list(car.__node__.labels)
    car_labels.remove('TObject')
    car_properties = dict(car.__node__)
    del car_properties['oid']
    assert sorted(car_labels) == sorted(['Car', 'Tesla'])
    assert car_properties == {'age': 3, 'model': 'S'}
    assert args[2] == ROLE.OWNER


def test_execute_obj_post_no_permission():
    with pytest.raises(BadRequest):
        handler.execute_obj_post(MagicMock(), MagicMock(), ROLE.STANDARD, MagicMock())


@patch('src.db.pull')
@patch('src.handler.execute_obj_post')
@patch('src.handler.execute_obj_delete')
def test_execute_obj_replace(mock_execute_obj_delete, mock_execute_obj_post, mock_pull):
    user = MagicMock()
    obj = MagicMock()
    role = ROLE.ADMIN
    oid_list = MagicMock()
    children = MagicMock()
    result = MagicMock()
    mock_execute_obj_post.return_value = result
    assert result == handler.execute_obj_replace(user, obj, role, oid_list, children)
    mock_execute_obj_delete.assert_called_once_with(obj, role, oid_list)
    mock_execute_obj_post.assert_called_once_with(user, obj, role, children)


@patch('src.handler.Subgraph')
@patch('src.db.delete', side_effect=Exception)
def test_execute_obj_delete_error(mock_delete, mock_subgraph):
    obj = MagicMock()
    child1 = MagicMock()
    child2 = MagicMock()
    child3 = MagicMock()
    child1.oid = 'oid1'
    child2.oid = 'oid2'
    child3.oid = 'oid3'
    child1.__node__ = 'child1'
    child2.__node__ = 'child2'
    child3.__node__ = 'child3'
    node1 = MagicMock()
    node2 = MagicMock()
    node3 = MagicMock()
    node4 = MagicMock()
    node5 = MagicMock()
    node6 = MagicMock()
    node1.__node__ = 'node1'
    node2.__node__ = 'node2'
    node3.__node__ = 'node3'
    node4.__node__ = 'node4'
    node5.__node__ = 'node5'
    node6.__node__ = 'node6'
    child1.get_all_children.return_value = [node1, node2]
    child2.get_all_children.return_value = [node3, node4]
    child3.get_all_children.return_value = [node5, node6]
    obj.children = [child1, child2, child3]
    oid_list = ['oid0', 'oid1', 'oid3', 'oid4']
    subgraph = MagicMock()
    mock_subgraph.return_value = subgraph
    with pytest.raises(BadRequest):
        handler.execute_obj_delete(obj, ROLE.ADMIN, oid_list)


@patch('src.handler.Subgraph')
@patch('src.db.delete')
def test_execute_obj_delete_success(mock_delete, mock_subgraph):
    obj = MagicMock()
    child1 = MagicMock()
    child2 = MagicMock()
    child3 = MagicMock()
    child1.oid = 'oid1'
    child2.oid = 'oid2'
    child3.oid = 'oid3'
    child1.__node__ = 'child1'
    child2.__node__ = 'child2'
    child3.__node__ = 'child3'
    node1 = MagicMock()
    node2 = MagicMock()
    node3 = MagicMock()
    node4 = MagicMock()
    node5 = MagicMock()
    node6 = MagicMock()
    node1.__node__ = 'node1'
    node2.__node__ = 'node2'
    node3.__node__ = 'node3'
    node4.__node__ = 'node4'
    node5.__node__ = 'node5'
    node6.__node__ = 'node6'
    child1.get_all_children.return_value = [node1, node2]
    child2.get_all_children.return_value = [node3, node4]
    child3.get_all_children.return_value = [node5, node6]
    obj.children = [child1, child2, child3]
    oid_list = ['oid0', 'oid1', 'oid3', 'oid4']
    subgraph = MagicMock()
    mock_subgraph.return_value = subgraph
    assert 'SUCCESS' == handler.execute_obj_delete(obj, ROLE.ADMIN, oid_list)
    mock_delete.assert_called_once_with(subgraph)
    mock_subgraph.assert_called_once_with(['node1', 'node2', 'node5', 'node6', 'child1', 'child3'])


def test_execute_obj_delete_no_permission():
    obj = MagicMock()
    oid_list = []
    with pytest.raises(BadRequest):
        handler.execute_obj_delete(obj, ROLE.STANDARD, oid_list)


def test_serialize_objs():
    obj1 = MagicMock()
    obj2 = MagicMock()
    obj1.serialize.return_value = 'obj1'
    obj2.serialize.return_value = 'obj2'
    objs = [obj1, obj2]
    user = MagicMock()
    assert ['obj1', 'obj2'] == handler.serialize_objs(user, objs, ROLE.ADMIN)
    obj1.serialize.assert_called_once_with(user, ROLE.ADMIN)
    obj2.serialize.assert_called_once_with(user, ROLE.ADMIN)


@patch('src.handler.get_graph_obj')
def test_get_obj_by_id_get_wrong_obj(mock_get_graph_obj):
    obj = MagicMock()
    mock_get_graph_obj.return_value = obj
    data = {
        '_id': 'test_id'
    }
    with pytest.raises(BadRequest):
        handler.get_obj_by_id('wrong_id', data)


@patch('src.handler.get_graph_obj')
def test_get_obj_by_id_get_obj(mock_get_graph_obj):
    obj = MagicMock()
    mock_get_graph_obj.return_value = obj
    data = {
        '_id': 'test_id'
    }
    assert obj == handler.get_obj_by_id('test_id', data)
    mock_get_graph_obj.assert_called_once_with('test_id', TObject)


@patch('src.handler.get_graph_obj')
def test_get_obj_by_id_get_app(mock_get_graph_obj):
    obj = MagicMock()
    mock_get_graph_obj.return_value = obj
    data = {
        '_id': 'test_id'
    }
    assert obj == handler.get_obj_by_id('root', data)
    mock_get_graph_obj.assert_called_once_with('test_id', MiniApp)


@patch('src.handler.get_graph_obj')
def test_get_mini_apps(mock_get_graph_obj):
    user = MagicMock()
    app1 = MagicMock()
    app2 = MagicMock()
    app1.serialize.return_value = 'app1'
    app2.serialize.return_value = 'app2'
    user.apps = [app1, app2]
    mock_get_graph_obj.return_value = user
    assert handler.get_mini_apps('test_uid', 'test_platform_root_key') == {
        'mini_apps': ['app1', 'app2']
    }
    user.verify_key.assert_called_once_with('test_platform_root_key')
    mock_get_graph_obj.assert_called_once_with('test_uid', User)


@patch('src.handler.get_graph_obj')
def test_get_mini_app(mock_get_graph_obj):
    user = MagicMock()
    app = MagicMock()
    app.serialize.return_value = 'mock_app'
    mock_get_graph_obj.side_effect = [user, app]
    assert handler.get_mini_app('test_uid', 'test_aid', 'test_platform_root_key') == {
        'mini_app': 'mock_app'
    }
    assert mock_get_graph_obj.call_count == 2
    user.verify_key.assert_called_once_with('test_platform_root_key')


@patch('src.handler.get_graph_obj')
def test_get_platform_root_key(mock_get_graph_obj):
    user = MagicMock()
    mock_get_graph_obj.return_value = user
    user.generate_platform_root_key.return_value = 'platform_root_key'
    assert handler.get_platform_root_key('test_uid') == {
        'platform_root_key': 'platform_root_key'
    }
    mock_get_graph_obj.assert_called_once_with('test_uid', User)


def test_get_graph_obj_not_exist():
    with pytest.raises(BadRequest):
        handler.get_graph_obj('none existing uid', User)


def test_get_graph_obj_exist():
    u = User()
    uid = str(uuid.uuid4())
    u.uid = uid
    db.push(u)
    db.pull(u)
    assert u == handler.get_graph_obj(uid, User)
    db.delete(u)


@patch('src.handler.serialize_objs', return_value='serialize_results')
@patch('src.handler.handle_obj_params')
def test_handle_obj_get(mock_handle_obj_params, mock_serialize_objs):
    parser = MagicMock()
    user = MagicMock()
    obj = MagicMock()
    obj.children = ['test1', 'test2']
    mock_handle_obj_params.return_value = {
        'user': user,
        'obj': obj,
        'role': ROLE.ADMIN
    }
    assert {'result': 'serialize_results'} == handler.handle_obj_get('test_oid', parser)
    mock_handle_obj_params.assert_called_once_with('test_oid', parser)
    mock_serialize_objs.assert_called_once_with(user, obj.children, ROLE.ADMIN)


def test_decorator():
    def dec(func):
        def wrapper(a, b):
            return func(a + b)
        return wrapper

    @dec
    def main(foo):
        return foo
    assert 6 == main(5, 1)


def test_extra_params():
    params = {
        'user': 'u',
        'app': 'a'
    }

    def func(user, **kwargs):
        return user
    assert 'u' == func(**params)


@patch('src.handler.get_obj_by_id')
@patch('src.handler.get_graph_obj')
def test_handle_obj_params(mock_get_graph_obj,
                           mock_get_obj_by_id):
    user = MagicMock(spec=User)
    data = {
        'uid': 'test_uid',
        '_id': 'test_oid',
        'role': ROLE.OWNER,
        'exp': 123456
    }
    obj = MagicMock()
    mock_get_graph_obj.return_value = user
    user.verify_key.return_value = data
    mock_get_obj_by_id.return_value = obj

    oid_list = 'oid1,oid2'
    children = [
        {
            'labels': ['People', 'Worker'],
            'properties': {
                'name': 'Owen',
                'age': '22'
            }
        }
    ]
    parser = MagicMock()
    parser.parse_args.return_value = {
        'uid': 'test_uid',
        'key': 'test_key',
        'oid_list': oid_list,
        'children': json.dumps(children)
    }
    params = handler.handle_obj_params('test_oid', parser)
    mock_get_graph_obj.assert_called_once_with('test_uid', User)
    assert params == {
        'user': user,
        'obj': obj,
        'role': ROLE.OWNER,
        'oid_list': ['oid1', 'oid2'],
        'children': children
    }
