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
        Get the platform root key.
        """
        args = uid_parser.parse_args()
        uid = args['uid']
        return handler.get_platform_root_key(uid)


app_ns = api.namespace('miniapp', description='Mini App level operation namespace.')

app_parser = reqparse.RequestParser()
app_parser.add_argument('uid', type=str, location='cookies')
app_parser.add_argument('PlatformRootKey', required=False, type=str, location='headers')


@app_ns.route('/<string:aid>/')
class MiniAppView(Resource):

    @api.doc('Get MiniApp', parser=app_parser)
    def get(self, aid):
        """
        Get the child TObjects of Current MiniApp
        """
        args = app_parser.parse_args()
        uid = args['uid']
        platform_root_key = args['PlatformRootKey']
        return handler.get_mini_app(uid, aid, platform_root_key)


@app_ns.route('/')
class MiniAppListView(Resource):

    @api.doc('Get All MiniApps', parser=app_parser)
    def get(self):
        """
        Get All MiniApps the user have.
        """
        args = app_parser.parse_args()
        uid = args['uid']
        return handler.get_mini_apps(uid)


obj_ns = api.namespace('tobject', description='TObject level operation namespace. NOTE: the root TObject (MiniApp) has the oid "root".')

obj_get_parser = reqparse.RequestParser()
obj_get_parser.add_argument('uid', type=str, location='cookies')
obj_get_parser.add_argument('key', required=True, type=str, location='headers')


obj_parser = reqparse.RequestParser()
obj_parser.add_argument('uid', type=str, location='cookies')
obj_parser.add_argument('key', required=True, type=str, location='headers')
obj_parser.add_argument('children', type=str, location='form')
obj_parser.add_argument('oid_list', type=str, location='form')

obj_model = api.model('TObject', {
    'oid': fields.String(description='TObject ID.'),
    'properties': fields.String(description='The actual properties (json encoded) in the customer object.'),
    'labels': fields.List(fields.String, description='The all classes of the customer object (Avoid "TObject".'),
    'key': fields.String(description='Secret key of the TObject.'),
    'permission': fields.Integer(description='10:owner, 5:admin, 0:standard')
})


@obj_ns.route('/<string:oid>/')
class TObjectView(Resource):

    @api.doc('Get children of a TObject.', parser=obj_get_parser)
    def get(self, oid):
        """
        Get the child TObjects of Current TObject
        """
        return handler.handle_obj_get(oid, obj_parser)

    @api.doc('Add children to a TObject.', parser=obj_parser)
    def post(self, oid):
        """
        Add child TObjects for current TObject
        children example:
        [{'labels': ['Person'], 'properties': {'age':10, 'name':'owen'}}]
        """
        return handler.handle_obj_post(oid, obj_parser)

    @api.doc('Replace children of a TObject.', parser=obj_parser)
    def put(self, oid):
        """
        Replace all child TObjects for current TObject
        children example:
        [{'labels': ['Person'], 'properties': {'age':10, 'name':'owen'}}]
        oid example:
        de593be7-0ace-4b3e-84f5-d21ece36a6f6,cf15ee45-0e77-43d3-ab1b-0efa2402412a
        """
        return handler.handle_obj_replace(oid, obj_parser)

    @api.doc('Delete children of a TObject.', parser=obj_parser)
    def delete(self, oid):
        """
        Delete all child TObjects for current TObject
        oid example:
        de593be7-0ace-4b3e-84f5-d21ece36a6f6,cf15ee45-0e77-43d3-ab1b-0efa2402412a
        """
        return handler.handle_obj_delete(oid, obj_parser)

    def patch(self, oid):
        """
        Change users access for current TObject
        """
        return 'PATCH'
