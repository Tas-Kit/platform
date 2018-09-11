from flask import Flask
from py2neo.database import Graph
from settings import PLATFORM_DB, PRIVATE_KEY_PATH, PUBLIC_KEY_PATH
import os
import rsa


def load_priv_key(path):
    path = os.path.join(os.path.dirname(__file__), path)
    with open(path, mode='rb') as privatefile:
        keydata = privatefile.read()
    return rsa.PrivateKey.load_pkcs1(keydata)


def load_pub_key(path):
    path = os.path.join(os.path.dirname(__file__), path)
    with open(path, mode='rb') as pubfile:
        keydata = pubfile.read()
    return rsa.PublicKey.load_pkcs1(keydata)

db = Graph(**PLATFORM_DB)
privkey = load_priv_key(PRIVATE_KEY_PATH)
pubkey = load_pub_key(PUBLIC_KEY_PATH)


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
