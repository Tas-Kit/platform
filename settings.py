import os


ENV = os.getenv('ENV', 'dev')
DEBUG = ENV != 'prod'

PLATFORM_DB = {
    'host': os.getenv('PLATFORM_DB_HOST', 'localhost'),
    'port': int(os.getenv('PLATFORM_DB_PORT', 8024)),
    'user': os.getenv('PLATFORM_DB_USERNAME', 'neo4j'),
    'password': os.getenv('PLATFORM_DB_PASSWORD', 'neo4jpass'),
    'scheme': os.getenv('PLATFORM_DB_SCHEME', 'bolt'),
}

BLOWFISH_SECRET = os.getenv('BLOWFISH_SECRET', '6$b66bg4%f1x0*td)1toqh3uvh^m2)ca-u1hl&82oqsds1nyx0')

SIGNATURE_DURATION = int(os.getenv('SIGNATURE_DURATION', 12 * 60 * 60))  # In minutes
