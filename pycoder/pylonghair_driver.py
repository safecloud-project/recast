"""
A wrapper for pylonghair to be used in a similar fashion to the pyeclib
drivers.
"""

import math

from pylonghair import fec_encode, fec_decode


class PylonghairDriver(object):
    """
    An erasure coding driver for pylonghair
    """
    def __init__(self, k, m, ec_type="longhair"):
        self.k = k
        self.m = m
        self.ec_type = ec_type

    def encode(self, data):
        """
        Encodes data using Cauchy Reed Solomon codes
        """
        block_size = int(math.ceil((0.0 + len(data)) / self.k))
        parity = bytearray(self.m * block_size)
        fec_encode(self.k, self.m, block_size, data, parity)
        strips = []
        for i in range(0, len(data), block_size):
            strips.append(data[i: i + block_size])
        for i in range(0, len(parity), block_size):
            strips.append(parity[i: i + block_size])
        return strips

    def decode(self, strips):
        """
        Decodes strips of data encoded using the PylonghairDriver's encode
        method
        """
        block_size = len(strips[0])
        blocks = []
        for row in range(self.k):
            offset = row * block_size
            block_data = strips[row]
            blocks.append((row, block_data))
        fec_decode(self.k, self.m, block_size, blocks)
        return "".join(map(lambda x: x[1], blocks))
