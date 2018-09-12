# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

from flask import Blueprint
from flask_restplus import Api, Resource, reqparse, fields
from . import handler

main_blueprint = Blueprint('main', __name__)


def register_blueprints(app):
    app.register_blueprint(main_blueprint, url_prefix='/api/v1/platform')

api = Api(main_blueprint, version='1.0', title='Platform API',
          description='Platform API')

internal_ns = api.namespace('internal', description='Internal namespace')
uid_parser = reqparse.RequestParser()
uid_parser.add_argument('uid', type=str, location='cookies')


@internal_ns.route('/')
class InternalView(Resource):

    @api.doc('Get Platform root key', parser=uid_parser)
    def get(self):
        """
        Get the child TObjects of Current TObject
        If it is the mini app root, pass 'root' for oid
        """
        args = uid_parser.parse_args()
        uid = args['uid']
        return handler.get_platform_root_key(uid)


app_ns = api.namespace('miniapp', description='Mini App level operation namespace.')

app_parser = reqparse.RequestParser()
app_parser.add_argument('uid', type=str, location='cookies')
app_parser.add_argument('PlatformRootKey', required=True, type=str, location='headers')


@app_ns.route('/<string:aid>/')
class MiniAppView(Resource):

    @api.doc('Get MiniApp key', parser=app_parser)
    def get(self, aid):
        """
        Get the child TObjects of Current TObject
        """
        args = app_parser.parse_args()
        uid = args['uid']
        platform_root_key = args['PlatformRootKey']
        return handler.get_mini_app_key(uid, aid, platform_root_key)


obj_ns = api.namespace('tobject', description='TObject level operation namespace.')

obj_parser = reqparse.RequestParser()
obj_parser.add_argument('uid', type=str, location='cookies')
obj_parser.add_argument('MiniAppKey', required=True, type=str, location='headers')
obj_parser.add_argument('children', type=str, location='form')
obj_parser.add_argument('labels', type=list, location='form')

obj_model = api.model('TObject', {
    'oid': fields.String(description='TObject ID.'),
    'properties': fields.String(description='The actual properties (json encoded) in the customer object.'),
    'labels': fields.List(fields.String, description='The all classes of the customer object (Avoid "TObject".'),
    'key': fields.String(description='Secret key of the TObject.'),
    'permission': fields.Integer(description='10:owner, 5:admin, 0:standard')
})


@obj_ns.route('/<string:oid>/')
class TObjectView(Resource):

    @api.doc('Get TObject children.', parser=obj_parser)
    @api.marshal_list_with(obj_model, envelope='obj_list')
    def get(self, oid):
        """
        Get the child TObjects of Current TObject
        """
        obj = handler.get_obj(oid, obj_parser)
        return handler.handle_obj_get(obj)

    def post(self, oid):
        """
        Add child TObjects for current TObject
        """
        return 'POST'

    def put(self, oid):
        """
        Replace all child TObjects for current TObject
        """
        return 'PUT'

    def delete(self, oid):
        """
        Delete all child TObjects for current TObject
        """
        return 'DELETE'

    def patch(self, oid):
        """
        Change users access for current TObject
        """
        return 'PATCH'
