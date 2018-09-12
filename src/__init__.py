from flask import Flask
from py2neo.database import Graph
from settings import PLATFORM_DB, BLOWFISH_SECRET
from Crypto.Cipher import Blowfish

db = Graph(**PLATFORM_DB)
blowfish = Blowfish.new(BLOWFISH_SECRET)


def create_app():
    app = Flask('Platform')
    # Load common settings
    app.config.from_object('settings')

    # Register blueprints
    from .views import register_blueprints
    register_blueprints(app)

    @app.route('/healthcheck', methods=['GET'])
    def healthcheck():
        return 'HEALTHY'

    return app
