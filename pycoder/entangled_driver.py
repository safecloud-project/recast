"""
A module with entanglement utilities
"""
import json
import math
import re
import struct

from pyeclib.ec_iface import ECDriver
from pyeclib.ec_iface import ECDriverError

import numpy

class Dagster(object):
    """
    An implementation of entanglement based on Dagster
    """

    @staticmethod
    def entangle(data, blocks):
        """
        Args:
            data (bytes): The original data
            blocks (list(bytes)): A list of bytes to xor together
        Returns:
            bytes, list(bytes): The entangled block and the blocks used to entangled it
        """
        entangled = data
        for block in blocks:
            entangled = Dagster.xor(entangled, block)
        return entangled, blocks

    @staticmethod
    def disentangle(entangled, blocks):
        """
        Args:
            entangled(bytes)    : Entangled block of data
            blocks (list(bytes)): A list of blocks the data was entangled with
        Returns:
            bytes, list(bytes): The disentangled block and the blocks used to disentangle it
        """
        data = entangled
        for block in blocks:
            data = Dagster.xor(data, block)
        return data, blocks

    @staticmethod
    def xor(block_a, block_b):
        """
        function used to XOR two blocks.
        """
        length_diff = len(block_a) - len(block_b)
        if length_diff > 0:
            for _ in xrange(length_diff):
                block_b += '\0'
        elif length_diff < 0:
            block_b = block_b[0:length_diff]

        entangled = numpy.frombuffer(block_a, dtype='b')
        entanglee = numpy.frombuffer(block_b, dtype='b')
        return numpy.bitwise_xor(entangled, entanglee).tostring()

def pad(data, length):
    """
    Trims or zero-fills a sequence of bytes to match a given length
    Args:
        data(bytes): The data to adapt
    Returns:
        (bytes): The adapted sequence of bytes
    """
    length_diff = length - len(data)
    if not length_diff:
        return data
    if length_diff > 0:
        for _ in xrange(length_diff):
            data += '\0'
        return data
    return data[0:length_diff]

class FragmentHeader(object):
    """
    Native python representation of a fragment_header_t struct used by liberasurecode
    """
    HEADER_FORMAT = "=IIIxxxxxxxxx"
    def __init__(self, blob):
        self.metadata = FragmentMetadata(blob[:59])
        extracted = struct.unpack(FragmentHeader.HEADER_FORMAT, blob[59:])
        self.magic = extracted[0]
        self.libec_version = extracted[1]
        self.metadata_checksum = extracted[2]

    def pack(self):
        """
        Returns a binary representation of the fragment header
        Return:
            bytes: A representation of the fragment header
        """
        blob = self.metadata.pack()
        blob += struct.pack(FragmentHeader.HEADER_FORMAT,
                            self.magic,
                            self.libec_version,
                            self.metadata_checksum)
        return blob

    def __repr__(self):
        return "FragmentHeader(" +\
        "metadata=" + str(self.metadata) +\
        ", magic=" + str(self.magic) +\
        ", libec_version=" + str(self.libec_version) +\
        ", metadata_checksum=" + str(self.metadata_checksum) +\
        ")"

    def __eq__(self, other):
        return isinstance(other, FragmentHeader) and \
               self.metadata == other.metadata and \
               self.magic == other.magic and \
               self.libec_version == other.libec_version and \
               self.metadata_checksum == other.metadata_checksum

class FragmentMetadata(object):
    """
    Native python representation of a fragment_metadata_t struct used by liberasurecode
    """
    METADATA_FORMAT = "=IIIQBIIIIIIIIBBI"
    def __init__(self, blob):
        extracted = struct.unpack(FragmentMetadata.METADATA_FORMAT, blob)
        self.index = extracted[0]
        self.size = extracted[1]
        self.fragment_backend_metadata_size = extracted[2]
        self.orig_data_size = extracted[3]
        self.checksum_type = extracted[4]
        self.checksum = [extracted[i] for i in xrange(5, 13, 1)]
        self.checksum_mismatch = extracted[13]
        self.backend_id = extracted[14]
        self.backend_version = extracted[15]

    def pack(self):
        """
        Returns a binary representation of the fragment metadata
        Return:
            bytes: A representation of the fragment metadata
        """
        return struct.pack(FragmentMetadata.METADATA_FORMAT,
                           self.index,
                           self.size,
                           self.fragment_backend_metadata_size,
                           self.orig_data_size,
                           self.checksum_type,
                           self.checksum[0],
                           self.checksum[1],
                           self.checksum[2],
                           self.checksum[3],
                           self.checksum[4],
                           self.checksum[5],
                           self.checksum[6],
                           self.checksum[7],
                           self.checksum_mismatch,
                           self.backend_id,
                           self.backend_version)

    def __repr__(self):
        return "FragmentMetadata(" + \
        "index=" + str(self.index) + \
        ", size=" + str(self.size) + \
        ", fbmds=" + str(self.fragment_backend_metadata_size) +\
        ", orig_data_size=" + str(self.orig_data_size) + \
        ", checksum_type=" + str(self.checksum_type) + \
        ", checksum=" + str(len(self.checksum)) + \
        ", checksum_mismatch=" + str(self.checksum_mismatch) + \
        ", backend_id=" + str(self.backend_id) + \
        ", backend_version=" + str(self.backend_version) + \
        ")"

    def __eq__(self, other):
        """
        Checks the equality of two FragmentMetadata objects
        """
        return isinstance(other, FragmentMetadata) and \
               self.index == other.index and \
               self.size == other.size and \
               self.fragment_backend_metadata_size == other.fragment_backend_metadata_size and \
               self.orig_data_size == other.orig_data_size and \
               self.checksum_type == other.checksum_type and \
               self.checksum_mismatch == other.checksum_mismatch and \
               self.backend_id == other.backend_id and \
               self.backend_version == other.backend_version

class StepEntangler(object):
    """
    Basic implementation of STeP based entanglement
    """
    # TODO: Refactor decode and reconstruct methods to use the same reconstruction
    #       code
    # TODO: Parallelize block fetching from the proxy
    # Use the Group Separator from the ASCII table as the delimiter between the
    # entanglement header and the data itself
    # https://www.lammertbies.nl/comm/info/ascii-characters.html
    HEADER_DELIMITER = chr(29)

    def __init__(self, source, s, t, p, ec_type="isa_l_rs_vand"):
        """
        StepEntangler constructor
        Args:
            source(Source): Block source implementing the get_random_blocks and
                            get_block primitives
            s(int): Number of source blocks or the number of chunks to make from
                    the original data
            t(int): Number of old blocks to entangle with
            p(int): Number of parity blocks to produce using Reed-Solomon
        """
        if not source or \
           not callable(getattr(source, "get_block", None)) or \
           not callable(getattr(source, "get_random_blocks", None)):
            raise ValueError("source argument must implement a get_random_blocks and a get_block method")
        if s <= 0:
            raise ValueError("s({:d}) must be greater or equal to 1".format(s))
        if t < 0:
            raise ValueError("t({:d}) must be greater or equal to 0".format(t))
        if p < s:
            raise ValueError("p({:d}) must be greater or equal to s({:d})".format(p, s))
        self.s = s
        self.t = t
        self.p = p
        self.e = self.p - self.s
        self.k = s + t

        self.source = source
        self.driver = ECDriver(k=self.k, m=self.p, ec_type=ec_type)

    @staticmethod
    def __serialize_entanglement_header(strips):
        path_pattern = re.compile(r"^(.+)\-\d+$")
        index_pattern = re.compile(r"\-(\d+)$")
        header = []
        for strip in strips:
            path = path_pattern.findall(strip.id)[0]
            index = int(index_pattern.findall(strip.id)[0])
            header.append((path, index))
        return json.dumps(header)

    @staticmethod
    def __parse_entanglement_header(header):
        return json.loads(header)

    @staticmethod
    def __get_header_from_strip(strip):
        """
        Returns the header part of the bytes strip
        Args:
            strip(bytes): The bytes containing the header, size and data
        Returns:
            bytes: The header part of the strip
        """
        pos = strip.find(EntanglementDriver.HEADER_DELIMITER)
        return strip[:pos]

    @staticmethod
    def __get_original_size_from_strip(strip):
        """
        Returns the size of the original data located
        Args:
            strip(bytes): The bytes containing the header, size and data
        Returns:
            int: The size of the original data
        """
        start = strip.find(EntanglementDriver.HEADER_DELIMITER) +\
                len(EntanglementDriver.HEADER_DELIMITER)
        end = strip.find(EntanglementDriver.HEADER_DELIMITER, start)
        return int(strip[start:end])

    @staticmethod
    def __get_data_from_strip(strip):
        """
        Returns the data part of the bytes strip
        Args:
            strip(bytes): The bytes containing the header and the data
        Returns:
            bytes: The data part of the strip
        """
        first_pos = strip.find(EntanglementDriver.HEADER_DELIMITER) +\
                    len(EntanglementDriver.HEADER_DELIMITER)
        pos = strip.find(EntanglementDriver.HEADER_DELIMITER, first_pos) +\
              len(EntanglementDriver.HEADER_DELIMITER)
        return strip[pos:]

    def encode(self, data):
        """
        Encodes data using combining entanglemend and Reed-Solomon(n, k)
        where k = s + t and n = k + p.
        Args:
            data(bytes): The original data to encode
        Returns:
            list(bytes): The encoded bytes to store
        """
        pointer_blocks = []
        if self.t > 0:
            pointer_blocks = self.source.get_random_blocks(self.t)
        block_header = self.__serialize_entanglement_header(pointer_blocks)
        size = len(data)
        fragment_size = int(math.ceil(size / float(self.s)))
        if (fragment_size % 2) == 1:
            fragment_size += 1
        padded_size = fragment_size * self.s
        padded_data = pad(data, padded_size)
        pointer_blocks = [pad(self.__get_data_from_strip(block.data)[80:], fragment_size) for block in pointer_blocks]
        encoded = self.entangle(padded_data, pointer_blocks)
        parity_blocks = [block_header + self.HEADER_DELIMITER + str(size) + self.HEADER_DELIMITER + parity_block for parity_block in encoded[self.k:]]
        return parity_blocks

    def entangle(self, data, blocks):
        """
        Performs entanglement combining the data and the extra blocks using
        Reed-Solomon.
        Args:
            data(bytes): The original piece of data
            blocks(list(bytes)): The pointer blocks
        Returns:
            list(bytes): The parity blocks produced by combining the data and
                         pointer blocks and running them through Reed-Solomon
                         encoding
        """
        return self.driver.encode(data + "".join(blocks))

    def fetch_and_prep_pointer_blocks(self, pointers, fragment_size, original_data_size):
        """
        Fetches the pointer blocks and rewrites their liberasurecode header so
        that they can be reused for reconstruction or decoding
        Args:
            pointer_blocks(list(list)): A list of 2 elements lists namely the
                                        filename and the index of each pointer
                                        block
            fragment_size(int): Size of each fragment
            original_data_size(int): Size of the original piece of data
        Returns:
            list(bytes): A list of cleaned up liberasurecode fragments formatted
                         and padded to fit the code
        Raises:
            ValueError: If the pointers argument is not of type list,
                        The fragment_size argument is not an int or is lower or
                        equal to 0,
                        The original_data_size argument is not an int or is lower
                        or equal to 0
        """
        if not isinstance(pointers, list):
            raise ValueError("pointers argument must be of type list")
        if not isinstance(fragment_size, int) or fragment_size <= 0:
            raise ValueError("fragment_size argument must be an integer greater than 0")
        if not isinstance(original_data_size, int) or original_data_size <= 0:
            raise ValueError("original_data_size argument must be an integer greater than 0")
        if original_data_size < fragment_size:
            raise ValueError("original_data_size must be greater or equal to fragment_size")
        original_pointer_blocks = [self.source.get_block(b[0], b[1], reconstruct_if_missing=False).data for b in pointers]
        prepared_pointer_blocks = []
        for index, block in enumerate(original_pointer_blocks):
            if not block:
                prepared_pointer_blocks.append(None)
                continue
            pointer_block = self.__get_data_from_strip(block)
            fragment_header = FragmentHeader(pointer_block[:80])
            fragment_header.metadata.index = self.s + index
            fragment_header.metadata.size = fragment_size
            fragment_header.metadata.orig_data_size = original_data_size
            modified_block = fragment_header.pack() + pad(pointer_block[80:],
                                                          fragment_size)
            prepared_pointer_blocks.append(modified_block)
        return prepared_pointer_blocks

    def decode(self, strips):
        """
        Decodes data using the entangled blocks and Reed-Solomon.
        Args:
            strips(list(bytes)): The encoded strips of data
        Returns:
            bytes: The decoded data
        """
        model_fragment_header = FragmentHeader(self.__get_data_from_strip(strips[0])[:80])
        fragment_size = model_fragment_header.metadata.size
        orig_data_size = model_fragment_header.metadata.orig_data_size
        modified_pointer_blocks = []
        if self.t > 0:
            block_header_text = self.__get_header_from_strip(strips[0])
            block_header = self.__parse_entanglement_header(block_header_text)
            modified_pointer_blocks = self.fetch_and_prep_pointer_blocks(block_header,
                                                                         fragment_size,
                                                                         orig_data_size)

        original_data_size = self.__get_original_size_from_strip(strips[0])
        strips = [self.__get_data_from_strip(strip) for strip in strips]
        decoded = self.disentangle(strips, modified_pointer_blocks)
        return decoded[:original_data_size]

    def disentangle(self, parity_blocks, pointer_blocks):
        """
        Performs disentanglement in order to reconstruct and decode the original
        data.
        Args:
            parity_blocks(bytes): The parity blocks produced from the original encoding
            pointer_blocks(bytes): The blocks used in the original entanglement adjusted to the right size
        Returns:
            bytes: The data is it was originally mixed with the pointer blocks before encoding
        """
        available_blocks = pointer_blocks + parity_blocks
        missing_indexes = [index for index in xrange(self.s)]
        source_blocks = self.driver.reconstruct(available_blocks, missing_indexes)
        data_blocks = source_blocks + pointer_blocks
        return self.driver.decode(data_blocks)

    def fragments_needed(self, missing_fragment_indexes):
        """
        Returns the list of fragments necessary for decoding/reconstruction of data
        Args:
            missing_fragment_indexes(list(int)): The list of missing fragments
        Returns:
            list(int): The list of fragments required for decoding/reconstruction
        """
        if not missing_fragment_indexes:
            return [index for index in xrange(self.s)]
        if self.e == 0:
            raise ECDriverError("Configuration of Step (s={}, t={}, e={}, p={}) does not allow for reconstruction".format(self.s, self.t, self.e, self.p))
        if self.e < len(missing_fragment_indexes):
            raise ECDriverError("Configuration of Step (s={}, t={}, e={}, p={}) does not allow for reconstruction of {} missing blocks".format(self.s, self.t, self.e, self.p, len(missing_fragment_indexes)))

        required_indices = [index for index in xrange(self.s) if index not in missing_fragment_indexes]
        required_indices += [self.s + index for index in xrange(len(missing_fragment_indexes))]
        return required_indices

    def reconstruct(self, available_fragment_payloads, missing_fragment_indexes):
        """
        Reconstruct the missing fragements
        Args:
            list(bytes): Avalaible fragments
            list(int): Indices of the missing fragments
        Returns:
            list(bytes): The list of reconstructed blocks
        """
        header_text = self.__get_header_from_strip(available_fragment_payloads[0])
        list_of_pointer_blocks = self.__parse_entanglement_header(header_text)

        parity_header = FragmentHeader(self.__get_data_from_strip(available_fragment_payloads[0])[:80])
        data_size = self.__get_original_size_from_strip(available_fragment_payloads[0])

        parity_blocks = [self.__get_data_from_strip(block) for block in available_fragment_payloads]

        modified_pointer_blocks = self.fetch_and_prep_pointer_blocks(list_of_pointer_blocks,
                                                                     parity_header.metadata.size,
                                                                     parity_header.metadata.orig_data_size)


        missing_fragment_indexes = [index + self.s + self.t for index in missing_fragment_indexes]
        reconstructed = self.driver.reconstruct(modified_pointer_blocks + parity_blocks,
                                                missing_fragment_indexes)

        requested_blocks = []
        for index, block in enumerate(reconstructed):
            requested_block = header_text + self.HEADER_DELIMITER + str(data_size) + self.HEADER_DELIMITER + block
            requested_blocks.append(requested_block)

        return requested_blocks

    def __repr__(self):
        return "StepEntangler(s=" + str(self.s) + ", t=" + str(self.t) + ", p=" + str(self.p) + ")"

class EntanglementDriver(object):
    """
    A driver for the playcloud coder that performs entanglement by fetching
    blocks from the proxy and combining them with the given blocks
    """
    # Use the Group Separator from the ASCII table as the delimiter between the
    # entanglement header and the data itself
    # https://www.lammertbies.nl/comm/info/ascii-characters.html
    HEADER_DELIMITER = chr(29)

    def __init__(self, block_source, k=5, entanglement=Dagster, pointers=5):
        """
        Args:
            block_source(object): An entity that can return random blocks
            k(int): The number of blocks to split the data in (defaults to 5)
            entanglement(Entangler): A type of entanglement to use (defaults to Dagster)
            pointers(int): The number of old blocks to entangle with (defaults to 5)
        """
        self.source = block_source
        self.k = k
        self.entangler = entanglement()
        self.pointers = pointers

    @staticmethod
    def __split_data(data, k):
        fragment_size = int(math.ceil(float(len(data)) / k))
        fragments = []
        for i in range(k):
            offset = i * fragment_size
            fragment = data[offset:offset + fragment_size]
            fragments.append(fragment)
        return fragments

    @staticmethod
    def __merge_data(fragments):
        return "".join(fragments)

    @staticmethod
    def __serialize_entanglement_header(strips):
        path_pattern = re.compile(r"^(.+)\-\d+$")
        index_pattern = re.compile(r"\-(\d+)$")
        header = []
        for strip in strips:
            path = path_pattern.findall(strip.id)[0]
            index = int(index_pattern.findall(strip.id)[0])
            header.append((path, index))
        return json.dumps(header)

    @staticmethod
    def __parse_entanglement_header(header):
        return json.loads(header)

    def encode(self, data):
        """
        Encodes data into a series of strips after entangling them
        Args:
            data(bytes): The encoded data
        Returns:
            list(bytes): The encoded data as a list of bytes
        """
        blocks = self.__split_data(data, self.k)
        random_blocks = []
        if self.pointers > 0:
            random_blocks = self.source.get_random_blocks(self.pointers)
        block_header = self.__serialize_entanglement_header(random_blocks)
        random_blocks = [block.data for block in random_blocks]
        encoded_blocks = []
        for block in blocks:
            encoded_block, random_blocks = self.entangler.entangle(block, random_blocks)
            encoded_block = block_header + self.HEADER_DELIMITER + encoded_block
            encoded_blocks.append(encoded_block)
        return encoded_blocks


    @staticmethod
    def __get_header_from_strip(strip):
        """
        Returns the header part of the bytes strip
        Args:
            strip(bytes): The bytes containing the header, size and data
        Returns:
            bytes: The header part of the strip
        """
        pos = strip.find(EntanglementDriver.HEADER_DELIMITER)
        return strip[:pos]

    @staticmethod
    def __get_data_from_strip(strip):
        """
        Returns the data part of the bytes strip
        Args:
            strip(bytes): The bytes containing the header and the data
        Returns:
            bytes: The data part of the strip
        """
        pos = strip.find(EntanglementDriver.HEADER_DELIMITER) + \
              len(EntanglementDriver.HEADER_DELIMITER)
        return strip[pos:]

    def decode(self, strips):
        """
        Decodes strip into the original data.
        Args:
            strips(list(bytes)): The encoded data as a list of bytes
        Returns:
            bytes: The decoded data
        """
        block_header_text = EntanglementDriver.__get_header_from_strip(strips[0])
        block_header = EntanglementDriver.__parse_entanglement_header(block_header_text)
        strips = [self.__get_data_from_strip(strip) for strip in strips]

        random_blocks = []
        if self.pointers > 0:
            random_blocks = [self.source.get_block(block[0], block[1]).data for block in block_header]

        decoded_blocks = []
        for strip in strips:
            decoded_block, random_blocks = self.entangler.disentangle(strip, random_blocks)
            decoded_blocks.append(decoded_block)
        return self.__merge_data(decoded_blocks)

    def fragments_needed(self, missing_fragment_indexes):
        """
        Returns the ids of the fragments needed to decode the document
        Args:
            missing_fragment_indexes(list(int)): Indices of the missing fragments
        Returns:
            list(int): The indices of the fragments needed for reconstruction
        """
        if missing_fragment_indexes:
            raise ECDriverError("Cannot reconstruct using Dagster")
        return [index for index in xrange(self.k)]


    @staticmethod
    def reconstruct(available_fragment_payloads, missing_fragment_indexes):
        """
        Raises an ECDriverError because a lost block produced by Dagster can only
        be reconstructed from a copy of the original block (handled by the proxy).
        """
        raise ECDriverError("Cannot reconstruct using Dagster")
