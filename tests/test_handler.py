import json
from mock import MagicMock, patch
from src import handler
from src.models import User
from src.constants import ROLE


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
@patch('src.handler.get_user')
def test_handle_obj_params(mock_get_user,
                           mock_get_obj_by_id):
    user = MagicMock(spec=User)
    data = {
        'uid': 'test_uid',
        '_id': 'test_oid',
        'role': ROLE.OWNER,
        'exp': 123456
    }
    obj = MagicMock()
    mock_get_user.return_value = user
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
    assert params == {
        'user': user,
        'obj': obj,
        'role': ROLE.OWNER,
        'oid_list': ['oid1', 'oid2'],
        'children': children
    }
