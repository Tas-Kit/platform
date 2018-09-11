from py2neo.ogm import GraphObject, Property, RelatedFrom, RelatedTo
import json
import time
from . import rsa_helper
from .utils import handle_error
from settings import SIGNATURE_DURATION
from .constants import ERROR_CODE


class TObject(GraphObject):
    __primarykey__ = "oid"
    oid = Property()
    child = RelatedTo("TObject", "HasTObject")
    parent = RelatedFrom("TObject", "HasTObject")
    user = RelatedFrom("User", "ShareTObject")
    app = RelatedFrom("MiniApp", "Includes")


class MiniApp(GraphObject):
    __primarykey__ = "aid"
    aid = Property()
    name = Property()
    app = Property()
    user = RelatedFrom("User", "HasApp")
    has = RelatedTo(TObject, "Includes")


class User(GraphObject):
    __primarykey__ = "uid"
    uid = Property()
    has = RelatedTo(MiniApp, "HasApp")
    share = RelatedTo(TObject, "ShareTObject")

    def generate_platform_root_key(self):
        data = {
            'uid': self.uid,
            'exp': int(time.time()) + SIGNATURE_DURATION
        }
        message = json.dumps(data)
        return rsa_helper.encrypt(message)

    def generate_app_key(self, app):
        role = self.get_role(app)
        message = self.get_message(app.aid, role)
        app_key = rsa_helper.encrypt(message)
        return app_key

    def get_role(self, app):
        role = self.has.get(app, 'role')
        if role is None:
            handle_error('Unable to find app for current user', ERROR_CODE.NOT_HAVE_APP)
        return role

    def get_message(self, _id, role):
        data = {
            'uid': self.uid,
            '_id': _id,
            'r': role,
            'exp': int(time.time()) + SIGNATURE_DURATION
        }
        return json.dumps(data).replace(' ', '')

    def verify(self, _id, role, signature):
        message = self.get_message(_id, role)
        return rsa_helper.verify(message, signature)

    def sign(self, _id, role):
        message = self.get_message(_id, role)
        return rsa_helper.sign(message)
