
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, dsa, rsa
from enum import Enum

import ConfigParser


config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../ACCOUNTS.INI'))
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

    def __init__(self, cypher, keysize, hash):
        ciphers = {
            'dsa': self.generate_dsa_keys,
            'rsa': self.generate_rsa_keys
        }
        hashopt = {
            'SHA224': hashes.SHA224,
            'SHA256': hashes.SHA256,
            'SHA384': hashes.SHA384,
            'SHA512': hashes.SHA512
        }
        self.cypher = cypher
        keys = ciphers[cypher]
        self.hash = hashopt[hash]
        self.private_key = keys(keysize)

    def generate_dsa_keys(self, keysize):
        private_key = dsa.generate_private_key(key_size=keysize,
                                               backend=default_backend())
        return private_key

    def generate_rsa_keys(self, keysize):
        private_key = rsa.generate_private_key(public_exponent=65537,
                                                key_size=keysize,
                                               backend=default_backend())
        return private_key

    def _create_rsa_signer(self):
        return self.private_key.signer(
            padding.PSS(
                mgf=padding.MGF1(self.hash()),
                salt_length=padding.PSS.MAX_LENGTH
                ), self.hash())

    def _create_dsa_signer(self):
        return self.private_key.signer(self.hash())


    def _create_rsa_verifier(self, signature):
        return self.private_key.public_key().verifier(signature, 
            padding.PSS(
                mgf=padding.MGF1(self.hash()),
                salt_length=padding.PSS.MAX_LENGTH),
                self.hash())

    def _create_dsa_verifier(self, signature):
        return self.private_key.public_key().verifier(signature, self.hash())

    def sign(self, data):
        if self.cypher == 'dsa':
            signer = self._create_dsa_signer()
        else:
            signer = self._create_rsa_signer()
        signer.update(data)
        return signer.finalize()

    def verify(self, signature, data):
        if self.cypher == 'dsa':
            verifier = self._create_dsa_verifier(signature)
        else:
            verifier = self._create_rsa_verifier(signature)

        verifier.update(data)
        verifier.verify()


    def size(self):
        return self.hash.digest_size