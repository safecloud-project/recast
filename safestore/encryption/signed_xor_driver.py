"""Driver for xor encryption of String."""

from safestore.encryption.assymetric_driver import AssymetricDriver
from safestore.encryption.xor_driver import XorDriver



class SignedXorDriver():
    """Class used to sign the message and xor the message.
    This Encryption guarantees privacy and non repudiation
    """

    def __init__(self, n_blocks):
        """ Initialize class to divide a string in n_blocks.
        If n_blocks == 1 then it returns the signed string.
        """
        self.assym = AssymetricDriver()
        self.xor_driver = XorDriver(n_blocks)



    def encode(self, data):
        """
            Receives a string to encode.
            Returns a list of xor blocks
        """
        signature = self.assym.sign(data)
        # char '|' is the separator between signture and data
        signed_data = signature + data
        return self.xor_driver.encode(signed_data)

    def decode(self, data):
        """Receives a signature and blocks to decode and verify the
        signature.
        """

        message = self.xor_driver.decode(data)
        """
            Assuming the signature uses 256 bits
        """
        signature = message[:256]
        message_data = message[256:]
        """
         If the verification fails a InvalidSignature exception is
         raised
        """
        self.assym.verify(signature, message_data)
        return message_data
