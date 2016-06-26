"""
Custom drivers for the playcloud project
"""
import math

from pylonghair import fec_encode, fec_decode

class ECStripingDriver(object):
    """
    A driver that splits data into strips and reassemble strips to the original data
    """

    def __init__(self, k, m, hd, ec_type=None, chksum_type=None,
                 validate=False):
        """Stripe an arbitrary-sized string into k fragments
        :param k: the number of data fragments to stripe
        :param m: the number of parity fragments to stripe
        :raises: ECDriverError if there is an error during encoding
        """
        self.k = k

        if m != 0:
            raise ECDriverError("This driver only supports m=0")

        self.m = m
        self.hd = hd

    def encode(self, data_bytes):
        """Stripe an arbitrary-sized string into k fragments
        :param data_bytes: the buffer to encode
        :returns: a list of k buffers (data only)
        :raises: ECDriverError if there is an error during encoding
        """
        # Main fragment size
        fragment_size = int(math.ceil(len(data_bytes) / float(self.k)))

        # Size of last fragment
        last_fragment_size = len(data_bytes) - (fragment_size * self.k - 1)

        fragments = []
        offset = 0
        for i in range(self.k):
            fragments.append(data_bytes[offset:offset + fragment_size])
            offset += fragment_size
        return fragments

    def decode(self, fragment_payloads, ranges=None,
               force_metadata_checks=False):
        """Convert a k-fragment data stripe into a string
        :param fragment_payloads: fragments (in order) to convert into a string
        :param ranges (unsupported): range decode
        :param force_metadata_checks (unsupported): verify fragment metadata
        :returns: a string containing original data
        :raises: ECDriverError if there is an error during decoding
        """
        if ranges is not None:
            raise ECDriverError("Decode does not support range requests in the"
                                " striping driver.")
        if force_metadata_checks is not False:
            raise ECDriverError(
                "Decode does not support metadata integrity checks in the "
                " striping driver.")
        if len(fragment_payloads) != self.k:
            raise ECInsufficientFragments(
                "Decode requires %d fragments, %d fragments were given" %
                (len(fragment_payloads), self.k))

        ret_string = ''

        for fragment in fragment_payloads:
            ret_string += fragment

        return ret_string

    def reconstruct(self, available_fragment_payloads,
                    missing_fragment_indexes):
        """We cannot reconstruct a fragment using other fragments.  This means
        that reconstruction means all fragments must be specified, otherwise we
        cannot reconstruct and must raise an error.
        :param available_fragment_payloads: available fragments (in order)
        :param missing_fragment_indexes: indexes of missing fragments
        :returns: a string containing the original data
        :raises: ECDriverError if there is an error during reconstruction
        """
        if len(available_fragment_payloads) != self.k:
            raise ECDriverError(
                "Reconstruction requires %d fragments, %d fragments given" %
                (len(available_fragment_payloads), self.k))

        return available_fragment_payloads

    def fragments_needed(self, missing_fragment_indexes):
        """By definition, all missing fragment indexes are needed to
        reconstruct, so just return the list handed to this function.
        :param missing_fragment_indexes: indexes of missing fragments
        :returns: missing_fragment_indexes
        """
        return missing_fragment_indexes

    def min_parity_fragments_needed(self):
        pass

    def get_metadata(self, fragment, formatted=0):
        """This driver does not include fragment metadata, so return empty
        string
        :param fragment: a fragment
        :returns: empty string
        """
        return ''

    def verify_stripe_metadata(self, fragment_metadata_list):
        """This driver does not include fragment metadata, so return true
        :param fragment_metadata_list: a list of fragments
        :returns: True
        """
        return True

    def get_segment_info(self, data_len, segment_size):
        pass

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
    def __init__(self, k, m, ec_type="longhair"):
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
