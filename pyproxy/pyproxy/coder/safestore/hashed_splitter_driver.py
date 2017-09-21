"""Driver for xor encryption with a secure hash function."""
import hashlib

from enum import Enum

class HashedSplitterDriver:
    """Class used to encrypt and genereate digest of a block.
    This Encryption guarantess privacy and integraty
    """

    def __init__(self, splitter, selected_hash):
        """Consctor of a HashedXorDriver.

        keyword arguments:
        n_blocks -- number of blocks to generate
        selected_hash -- hash function used to create a digest of a
        block.
        """
        functions = {'MD5': hashlib.md5,
                     'SHA1': hashlib.sha1,
                     'SHA224': hashlib.sha224,
                     'SHA256': hashlib.sha256,
                     'SHA384': hashlib.sha384,
                     'SHA512': hashlib.sha512}

        self.hash_function = functions[selected_hash]
        self.splitter = splitter

    def _create_digest(self, block):
        """Private function to create a digest of a block."""


        hash_function = self.hash_function()
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
        digest = self._create_digest(data)
        data = digest+data
        blocks = self.splitter.encode(data)
        return blocks

    def decode(self, data):
        """Function used to decode a list of tuples.

        Function used to decode a set of blocks and verify the
        integrity of each block.

        If the integrity of a block fails it throws a
        IntegratyException.

        Returns:
            The original string
        """
        decoded = self.splitter.decode(data)
        digest_size = self.hash_function().digest_size
        sig = decoded[:digest_size]
        dec = decoded[digest_size:]

        new_digest = self._create_digest(dec)

        if sig != new_digest:
            message = "Integrity Check failed in block {}".format(i)
            raise IntegrityException(message)

        return dec


class IntegrityException(Exception):
    """Exception used when integrity check fails."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.value)
