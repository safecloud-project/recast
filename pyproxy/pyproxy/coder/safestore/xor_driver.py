"""Driver for xor encryption of String."""
from Crypto import Random

import numpy


class XorDriver:
    """ Class used to encode and decode a string using plain XOR.
        This Encryption only guarantees privacy.
    """

    def __init__(self, n_blocks):
        """ Initialize class to divide a string in n_blocks.
            If n_blocks == 1 then it returns the original string.
        """
        self.n_blocks = n_blocks

    def encode(self, data):
        """
            Receives a string to encode.
            Returns an array of data encoded with XOR.
        """
        res = []
        buf = data
        size = len(data)
        for x in range(1, self.n_blocks):
            rnd = Random.get_random_bytes(size)
            buf = _xor(buf, rnd)
            res.append(rnd)
        res.append(buf)
        return res

    def decode(self, data):
        """
            Receives a list of blocks and returns the original string.
        """
        buf = data[0]
        for i in range(1, len(data)):
            buf = _xor(buf, data[i])
        return buf


def _xor(block_a, block_b):
    """
        'Private' function used to XOR two blocks.
    """
    a = numpy.frombuffer(block_a, dtype='b')
    b = numpy.frombuffer(block_b, dtype='b')
    c = numpy.bitwise_xor(a, b)
    r = c.tostring()
    return r
