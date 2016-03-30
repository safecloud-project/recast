
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import ConfigParser


config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../configuration/ACCOUNTS.INI'))
KEY_PATH = config.get('MAIN', 'KEY_PATH')
PRIVATE_KEY = config.get('MAIN', 'PRIVATE_KEY')
PUBLIC_KEY = config.get('MAIN', 'PUBLIC_KEY')
PASSW = config.get('MAIN', 'PASSW')


def _load_private_key():
    path = os.path.join(KEY_PATH, PRIVATE_KEY)
    with open(path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=PASSW,
            backend=default_backend()
        )
    return private_key


def _load_public_key():
    path = os.path.join(KEY_PATH, PUBLIC_KEY)
    with open(path, "rb") as key_file:
        private_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return private_key


class AssymetricDriver:

    def __init__(self):
        self.private_key = _load_private_key()
        self.public_key = _load_public_key()

    def _create_signer(self):
        return self.private_key.signer(padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

    def _create_verifier(self, signature):
        return self.public_key.verifier(signature, padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
            hashes.SHA256()
        )

    def sign(self, data):
        signer = self._create_signer()
        signer.update(data)
        return signer.finalize()

    def verify(self, signature, data):
        verifier = self._create_verifier(signature)
        verifier.update(data)
        verifier.verify()
