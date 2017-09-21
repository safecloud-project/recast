
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

class AESDriver:

    def __init__(self):
        self.backend = default_backend()
        """
            AES 
                128 bits - 16 bytes
                192 bits - 24 bytes
                256 bits - 32 bytes

        """
        self.key = os.urandom(32)
        self.iv = os.urandom(16)
        self.cipher = Cipher(algorithms.AES(
            self.key), modes.CBC(self.iv), backend=default_backend())

    def encode(self, data):
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data)
        padded_data += padder.finalize()
        encryptor = self.cipher.encryptor()
        secret = encryptor.update(padded_data) + encryptor.finalize()
        return [secret]

    def decode(self, data):
        data = data[0]
        decryptor = self.cipher.decryptor()
        dec = decryptor.update(data) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(dec) + unpadder.finalize()
