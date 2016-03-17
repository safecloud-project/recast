"""Driver for xor encryption of a String with signature and integraty."""
from safestore.encryption.assymetric_driver import AssymetricDriver
from safestore.encryption.hashed_xor_driver import HashedXorDriver


class SignedHashedXorDriver:
    """ Class used to encode and decode a string using plain xor.
    This Encryption guarentees privacy, integraty and non
    repudiation-
    """

    def __init__(self, n_blocks, integraty_hash):
        """ Initialize class to divide a string in n_blocks.
            If n_blocks == 1 then it retuns the original string.
        """
        self.n_blocks = n_blocks
        self.hashed_xor_driver = HashedXorDriver(n_blocks, integraty_hash)
        self.assym = AssymetricDriver()

    def encode(self, data):
        """Receives a string to encode.
        Returns a list such that:
        [(block, block_digest)]
        """
        signature = self.assym.sign(data)
        signed_data = signature + data
        return self.hashed_xor_driver.encode(signed_data)

    def decode(self, data):
        """Receives a list such as [(block, block_digest)].
        Returns the original message if the signature is valid
        and the integrati of the blocks holds.
        """
        message = self.hashed_xor_driver.decode(data)
        signature = message[:256]
        message_data = message[256:]
        """
         If the verification fails a InvalidSignature exception is
         raised
        """
        self.assym.verify(signature, message_data)
        return body[1]
