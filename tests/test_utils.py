from src import utils


def test_encrypt_and_decrypt():
    msg = 'my very secret message'
    code = utils.encrypt(msg)
    assert type(code) is str
    assert msg == utils.decrypt(code)
