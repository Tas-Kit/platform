import base64
import rsa
import json
from . import pubkey, privkey


def verify(message, signature):
    signature = base64.b64decode(signature.encode('utf-8'))
    return rsa.verify(message.encode('utf-8'), signature, pubkey)


def decrypt(code):
    code = base64.b64decode(code.encode('utf-8'))
    return json.loads(rsa.decrypt(code, privkey).decode('utf-8'))


def sign(message):
    signature = rsa.sign(message.encode('utf-8'), privkey, 'SHA-1')
    return base64.b64encode(signature).decode('utf-8')


def encrypt(message):
    code = rsa.encrypt(message.encode('utf-8'), pubkey)
    return base64.b64encode(code).decode('utf-8')


# def create_keys():
#     (pubkey, privkey) = rsa.newkeys(1024, True, 8)
#     with open("id_rsa.pub", "w") as text_file:
#         text_file.write(pubkey.save_pkcs1().decode('ascii'))
#     with open("id_rsa", "w") as text_file:
#         text_file.write(privkey.save_pkcs1().decode('ascii'))
