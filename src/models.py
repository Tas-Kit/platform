from py2neo.ogm import GraphObject, Property, RelatedFrom, RelatedTo
import time
import uuid
from src import utils
from settings import SIGNATURE_DURATION
from .constants import ERROR_CODE


class TObject(GraphObject):
    __primarykey__ = "oid"
    oid = Property()
    children = RelatedTo("TObject", "Has")
    parents = RelatedFrom("TObject", "Has")
    users = RelatedFrom("User", "Share")
    apps = RelatedFrom("MiniApp", "Has")

    def get_all_children(self):
        all_children = []
        for child in list(self.children):
            all_children += child.get_all_children()
        return all_children

    @staticmethod
    def new(labels, properties):
        """
        Construct new TObject with labels and properties
        Args:
            labels (list(str)): list of strings
            properties (dict): dict of properties
        """
        obj = TObject()
        obj.oid = str(uuid.uuid4())
        obj.__node__._labels.update(labels)
        if 'oid' in properties.keys():
            del properties['oid']
        for key, value in properties.items():
            obj.__node__[key] = value
        return obj

    @property
    def labels(self):
        labels = list(self.__node__.labels)
        labels.remove('TObject')
        return labels

    def serialize(self, user, role):
        message = user.get_message(self.oid, role)
        key = utils.encrypt(message)
        return {
            'oid': self.oid,
            'labels': self.labels,
            'properties': dict(self.__node__),
            'key': key,
            'role': role
        }


class MiniApp(GraphObject):
    __primarykey__ = "aid"
    aid = Property()
    name = Property()
    app = Property()
    users = RelatedFrom("User", "HasApp")
    children = RelatedTo(TObject, "Has")

    def serialize(self, user=None):
        return {
            'aid': self.aid,
            'name': self.name,
            'app': self.app,
            'key': None if user is None else user.generate_app_key(self)
        }


class User(GraphObject):
    __primarykey__ = "uid"
    uid = Property()
    apps = RelatedTo(MiniApp, "HasApp")
    share = RelatedTo(TObject, "Share")

    def verify_key(self, key):
        try:
            data = utils.decrypt(key)
        except Exception as e:
            utils.handle_error(e, ERROR_CODE.UNABLE_TO_DECRYPT)
        if self.uid != data['uid']:
            utils.handle_error("User does not match the platform root key.", ERROR_CODE.USER_NOT_MATCH)
        if int(time.time()) > data['exp']:
            utils.handle_error("Key expired.", ERROR_CODE.KEY_EXPIRED)
        return data

    def generate_platform_root_key(self):
        data = {
            'uid': self.uid,
            'exp': int(time.time()) + SIGNATURE_DURATION
        }
        return utils.encrypt(data)

    def generate_app_key(self, app):
        role = self.get_role(app)
        message = self.get_message(app.aid, role)
        app_key = utils.encrypt(message)
        return app_key

    def get_role(self, app):
        role = self.apps.get(app, 'role')
        if role is None:
            utils.handle_error('Unable to find app for current user.', ERROR_CODE.NOT_HAVE_APP)
        return role

    def get_message(self, _id, role):
        return {
            'uid': self.uid,
            '_id': _id,
            'role': role,
            'exp': int(time.time()) + SIGNATURE_DURATION
        }
