"""Driver for xor encryption of String."""

from assymetric_driver import AssymetricDriver


class SignedSplitterDriver():
    """Class used to sign the message and xor the message.
    This Encryption guarantees privacy and non repudiation
    """

    def __init__(self, splitter, signer):
        self.signer = signer
        self.splitter = splitter



    def encode(self, data):
        """
            Receives a string to encode.
            Returns a list of xor blocks
        """
        signature = self.signer.sign(data)
        signed_data = signature + '<-->'+data
        return self.splitter.encode(signed_data)

    def decode(self, data):
        """Receives a signature and blocks to decode and verify the
        signature.
        """
        message = self.splitter.decode(data)

        sign_size = self.signer.size()
        splited_message = message.split('<-->')
        signature = splited_message[0]
        message_data = splited_message[1]
        """
         If the verification fails a InvalidSignature exception is
         raised
        """
        self.signer.verify(signature, message_data)
        return message_data
