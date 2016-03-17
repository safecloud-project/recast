"""Driver for xor encryption with a secure hash function."""
from xor_driver import XorDriver

import hashlib

from enum import Enum


class Hash(Enum):
    """Available Hash Functions."""

    md5 = 'MD5'
    sha1 = 'SHA1'
    sha224 = 'SHA224'
    sha256 = 'SHA256'
    sha384 = 'SHA384'
    sha512 = 'SHA512'


class HashedXorDriver:
    """Class used to encrypt and genereate digest of a block.
    This Encryption guarantess privacy and integraty
    """

    def __init__(self, n_blocks, selected_hash):
        """Consctor of a HashedXorDriver.

        keyword arguments:
        n_blocks -- number of blocks to generate
        selected_hash -- hash function used to create a digest of a
        block.
        """
        self.n_blocks = n_blocks
        self.selected_hash = selected_hash
        self.xor_driver = XorDriver(n_blocks)

    def _create_digest(self, block):
        """Private function to create a digest of a block."""
        functions = {Hash.md5: hashlib.md5,
                     Hash.sha1: hashlib.sha1,
                     Hash.sha224: hashlib.sha224,
                     Hash.sha256: hashlib.sha256,
                     Hash.sha384: hashlib.sha384,
                     Hash.sha512: hashlib.sha512}

        hash_function = functions[self.selected_hash]()
        hash_function.update(block)
        return hash_function.digest()

    def encode(self, data):
        """Function used to encode a string and generate a digest.

        Args:
            data (string): String to be encoded

        Returns:
            List of tuples: each tuple has the form of
                (block, block_digest)
        """
        blocks = self.xor_driver.encode(data)
        return map(lambda x: (x, self._create_digest(x)), blocks)

    def decode(self, data):
        """Function used to decode a list of tuples.

        Function used to decode a set of blocks and verify the
        integraty of each block.

        If the integraty of a block fails it throws a
        IntegratyException.

        Args:
            param1 (data): List of tuples. Each tuple has the
                form of (block, block_digest).

        Retuns:
            The original string
        """
        blocks = []
        for i in range(0, len(data)):
            (block, digest) = data[i]

            new_digest = self._create_digest(block)

            if new_digest != digest:
                message = "Integrity Check failed in block {}".format(i)
                raise IntegrityException(message)
            else:
                blocks.append(block)

        return self.xor_driver.decode(blocks)


class IntegrityException(Exception):
    """Exception used when integrity check fails."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.value)
