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

def compute_block_size(data_length, k):
    """
    Returns a block_size that is appropriate for block size for longhair.
    In order to use longhair the BLOCK SIZE MUST BE A MULTIPLE OF 8.
    """
    assert k > 0
    block_size = (data_length + 0.0) / k
    if (block_size % 8) == 0:
        return int(block_size)
    if block_size < 8:
        return 8
    return int(math.ceil(block_size / 8)) * 8

class PylonghairDriver(object):
    """
    An erasure coding driver for pylonghair
    """
    def __init__(self, k, m, ec_type="longhair", hd=None):
        self.k = k
        self.m = m
        self.ec_type = ec_type

    def encode(self, data):
        """
        Encodes data using Cauchy Reed Solomon codes
        """
        block_size = compute_block_size(len(data), self.k)
        parity = bytearray(self.m * block_size)
        assert fec_encode(self.k, self.m, block_size, data, parity) == 0
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
        block_size = len(strips[len(strips) - 1])
        blocks = []
        number_of_data_blocks = len(strips) - self.m
        data_blocks = strips[:number_of_data_blocks]
        for row, data in enumerate(data_blocks):
            blocks.append((row, data))
        assert fec_decode(number_of_data_blocks, self.m, block_size, blocks) == 0
        return "".join([strip[1] for strip in blocks])
