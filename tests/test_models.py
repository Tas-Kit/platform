import time
import pytest
from mock import MagicMock, patch
from src.models import TObject, User, MiniApp
from src.constants import ROLE
from werkzeug.exceptions import BadRequest


class TestUser(object):

	def test_get_role():


    @patch('src.utils.encrypt', return_value='app_key')
    @patch('src.models.User.get_message', return_value='message')
    @patch('src.models.User.get_role', return_value=ROLE.ADMIN)
    def test_generate_app_key(self, mock_get_role, mock_get_message, mock_encrypt):
        user = User()
        app = MiniApp()
        assert 'app_key' == user.generate_app_key(app)

    @patch('src.utils.encrypt', return_value='platform_key')
    def test_generate_platform_root_key(self, mock_encrypt):
        assert 'platform_key' == User().generate_platform_root_key()

    @patch('src.utils.decrypt')
    def test_verify_key(self, mock_decrypt):
        data = {
            'uid': 'test_uid',
            'exp': int(time.time()) + 10
        }
        mock_decrypt.return_value = data
        user = User()
        user.uid = 'test_uid'
        assert data == user.verify_key('mykey')
        mock_decrypt.assert_called_once_with('mykey')

    @patch('src.utils.decrypt', side_effect=Exception)
    def test_verify_key_exception(self, mock_decrypt):
        data = {
            'uid': 'test_uid',
            'exp': int(time.time()) + 10
        }
        mock_decrypt.return_value = data
        user = User()
        user.uid = 'test_uid'
        with pytest.raises(BadRequest):
            user.verify_key('mykey')

    @patch('src.utils.decrypt')
    def test_verify_key_user_not_match(self, mock_decrypt):
        data = {
            'uid': 'test_uid',
            'exp': int(time.time()) + 10
        }
        mock_decrypt.return_value = data
        user = User()
        user.uid = 'wrong_uid'
        with pytest.raises(BadRequest):
            user.verify_key('mykey')

    @patch('src.utils.decrypt')
    def test_verify_key_exp(self, mock_decrypt):
        data = {
            'uid': 'test_uid',
            'exp': int(time.time()) - 10
        }
        mock_decrypt.return_value = data
        user = User()
        user.uid = 'test_uid'
        with pytest.raises(BadRequest):
            user.verify_key('mykey')


class TestTObject(object):

    def test_get_all_children(self):
        obj = TObject()
        child1 = MagicMock()
        child2 = MagicMock()
        child1.get_all_children.return_value = ['child1children']
        child2.get_all_children.return_value = ['child2children']
        obj.children = [child1, child2]
        assert ['child1children', 'child2children'] == obj.get_all_children()

    def test_labels(self):
        obj = TObject()
        assert [] == obj.labels

    @patch('src.utils.encrypt')
    def test_serialize(self, mock_encrypt):
        obj = TObject.new(['Person'], {'oid': 'oid', 'age': 18})
        assert obj.oid != 'oid'
        user = MagicMock()
        user.get_message.return_value = 'message'
        mock_encrypt.return_value = 'mykey'
        assert obj.serialize(user, ROLE.ADMIN) == {
            'oid': obj.oid,
            'labels': ['Person'],
            'properties': {'age': 18, 'oid': obj.oid},
            'key': 'mykey',
            'role': ROLE.ADMIN
        }
        mock_encrypt.assert_called_once_with('message')
        user.get_message.assert_called_once_with(obj.oid, ROLE.ADMIN)
