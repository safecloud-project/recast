"""Driver for xor encryption of a String with signature and integrity."""


class SignedHashedSplitterDriver:
    """ Class used to encode and decode a string using plain xor.
    This Encryption guarantees privacy, integrity and non
    repudiation-
    """

    def __init__(self, splitter, signer):
        """ Initialize class to divide a string in n_blocks.
            If n_blocks == 1 then it returns the original string.
        """
        self.splitter = splitter
        self.signer = signer

    def encode(self, data):
        """Receives a string to encode.
        Returns a list of blocks
        """
        signature = self.signer.sign(data)
        signed_data = signature + "<-->" + data
        return self.splitter.encode(signed_data)

    def decode(self, data):
        """Receives a list such as [(block, block_digest)].
        Returns the original message if the signature is valid
        and the integrity of the blocks holds.
        """
        message = self.splitter.decode(data)
        splited_message = message.split('<-->')
        signature = splited_message[0]
        message_data = splited_message[1]
        """
         If the verification fails a InvalidSignature exception is
         raised
        """
        self.signer.verify(signature, message_data)
        return message_data
