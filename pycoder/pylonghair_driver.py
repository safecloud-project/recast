"""
A wrapper for pylonghair to be used in a similar fashion to the pyeclib
drivers.
"""

import math

from pylonghair import fec_encode, fec_decode

def split_and_number(strips, missing_indices):
    """
    Number contiguous elements in an array with the information of the missing
    indices.
    """
    remapped_strips = []
    j = 0
    missing_indices.sort()
    for i in range(len(strips)):
        if j in missing_indices:
            while j in missing_indices:
                j += 1
        remapped_strips.append((j, strips[i]))
        j += 1
    return remapped_strips

def fill_missing(strips, missing_indices):
    blocks = split_and_number(strips, missing_indices)
    block_size = len(strips[0])
    for index in missing_indices:
        blocks.append((index, bytearray(block_size)))
    return blocks

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
            block_data = strips[row]
            blocks.append((row, block_data))

        print "len(blocks):", len(blocks)
        for block in blocks:
            print "\tblock[0]:", block[0]
        fec_decode(self.k, self.m, block_size, blocks)
        return "".join(map(lambda x: x[1], blocks))

    def reconstruct(self, strips, missing_indices):
        print "self.k =", self.k
        block_size = len(strips[0])
        length_of_available_data = self.k - len(missing_indices)
        blocks = split_and_number(strips[:length_of_available_data], missing_indices)
        for i in range(len(missing_indices)):
            blocks.append((self.k + i, blocks[self.k + i]))
        fec_decode(self.k, self.m, block_size, blocks)
        reconstructed = []
        reconstructed_indices = sorted(missing_indices)
        for i in range(len(reconstructed_indices)):
            actual_index = reconstructed_indices[i]
            reconstructed_block = blocks[length_of_available_data + i]
            reconstructed.append((actual_index, reconstructed_block))
        return reconstructed
