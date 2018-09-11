# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

from flask import Blueprint
from flask_restplus import Api, Resource, reqparse
from .models import User, MiniApp, TObject
from . import db, utils, handler

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

    @internal_ns.doc('Get Platform root key', parser=uid_parser)
    def get(self):
        """
        Get the child TObjects of Current TObject
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

    @app_ns.doc('Get MiniApp key', parser=app_parser)
    def get(self, aid):
        """
        Get the child TObjects of Current TObject
        """
        args = app_parser.parse_args()
        uid = args['uid']
        platform_root_key = args['PlatformRootKey']
        return handler.get_mini_app_key(uid, aid, platform_root_key)


obj_ns = api.namespace('tobject', description='TObject level operation namespace.')

parser = reqparse.RequestParser()


@obj_ns.route('/<string:oid>/')
class TObjectView(Resource):

    def get(self, oid):
        """
        Get the child TObjects of Current TObject
        """
        return 'GET'

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
