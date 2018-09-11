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

PRIVATE_KEY_PATH = os.getenv('PRIVATE_KEY_PATH', 'secret/id_rsa')
PUBLIC_KEY_PATH = os.getenv('PUBLIC_KEY_PATH', 'secret/id_rsa.pub')

SIGNATURE_DURATION = int(os.getenv('SIGNATURE_DURATION', 12 * 60 * 60))  # In minutes
