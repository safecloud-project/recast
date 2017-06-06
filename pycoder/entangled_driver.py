"""
A module with entanglement utilities
"""
import json
import math
import re

from pyeclib.ec_iface import ECDriver
from pyeclib.ec_iface import ECDriverError

import numpy

class Entangler(object):
    """
    An abstraction representing the expected interface of an Entangler
    implementation
    """
    def __init__(self, data_source):
        """
        Args:
            data_source(object): A data source that can be used to fetch blocks
        """
        self.data_source = data_source

    def entangle(self, data):
        """
        Entangles data with blocks from the data source
        Args:
            data(list(str)): Data to entangle
        Returns:
            dict: A dictionary with the entangled data blocks and the ids of the
                  blocks used for the entanglement
        """
        raise NotImplementedError()

    def disentangle(self, data, blocks):
        """
        Disentangles data
        Args:
            data(list(str)): Entangled data
            blocks(list(str)): Id of the blocks used for the original entanglement
        Returns:
            list(str): data
        """
        raise NotImplementedError()



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
    length_diff = length - len(data)
    if not length_diff:
        return data
    if length_diff > 0:
        for _ in xrange(length_diff):
            data += '\0'
        return data
    return data[0:length_diff]

class StepEntangler(object):
    #FIXME Determining original fragment size fails if the number of source blocks is lower or equal to  the number of pointer blocks (s<=t)
    def __init__(self, s, t, p):
        self.s = s
        self.t = t
        self.p = p
        self.k = s + t
        self.driver = ECDriver(k=self.k, m=self.p, ec_type="liberasurecode_rs_vand")

    def entangle(self, data):
        fragment_size = int(math.ceil(len(data) / float(self.s)))
        #TODO get blocks from the source
        blocks = [pad("", fragment_size) for _ in xrange(self.t)]
        data += "".join(blocks)
        return self.driver.encode(data)

    def disentangle(self, encoded):
        decoded = self.driver.decode(encoded)
        actual_fragment_size = len(decoded) /  float(self.k)
        bytes_to_recover = int(actual_fragment_size * self.s)
        return decoded[:bytes_to_recover]

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

    def __init__(self, block_source, k=5, entanglement=Dagster, pointers=5, replicas=3):
        """
        Args:
            block_source(object): An entity that can return random blocks
            k(int): The number of blocks to split the data in (defaults to 5)
            entanglement(Entangler): A type of entanglement to use (defaults to Dagster)
            pointers(int): The number of old blocks to entangle with (defaults to 5)
            replicas(int): The number of replicas of the entangled blocks (defaults to 3)
        """
        self.source = block_source
        self.k = k
        self.entangler = entanglement()
        self.pointers = pointers
        self.replicas = replicas

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

    @staticmethod
    def make_replicas(blocks, replicas):
        """
        Copy blocks to make replicas
        f([data_0  , data_1  , ..., data_n ], r) ->
          [data_0_1, data_1_1, ..., data_n_1,
           ...,
           data_0_r, data_1_r, ..., data_n_r]
        Args:
            blocks(list(bytes)): Original blocks of data
            replicas(int): The number of replicas to return
        """
        copies = []
        for _ in xrange(replicas):
            for block in blocks:
                copy = block[:]
                copies.append(copy)
        return copies

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
        # Create replicas
        return self.make_replicas(encoded_blocks, self.replicas)


    @staticmethod
    def __get_header_from_strip(strip):
        """
        Returns the header part of the bytes strip
        Args:
            strip(bytes): The bytes containing the header and the data
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
        Returns the ids of the fragments needed to reconstruct the missing fragments
        Args:
            missing_fragment_indexes(list(int)): Indices of the missing fragments
        Returns:
            list(int): The indices of the fragments needed for reconstruction
        """
        data_indexes = [index for index in xrange(self.k) if index not in missing_fragment_indexes]
        reconstruction_indexes = []
        blocks = self.k * self.replicas
        missing_data_indexes = [index for index in missing_fragment_indexes if index < self.k]
        for missing_index in missing_data_indexes:
            copies = []
            for replica_index in xrange(missing_index + self.k, blocks, self.k):
                if replica_index not in missing_fragment_indexes:
                    copies.append(replica_index)
            if not copies:
                raise ECDriverError("Cannot find available replica for block " + str(missing_index))
            reconstruction_indexes.append(copies[0])
        return sorted(data_indexes + reconstruction_indexes, key=lambda index: (index % self.k))

    @staticmethod
    def reconstruct(available_fragment_payloads, missing_fragment_indexes):
        """
        Returns copies of the original blocks from the replicas
        Args:
            available_fragment_payloads(list(bytes)): Available blocks of data
            missing_data_indexes(list(int)): Indexes of the missing blocks
        Returns:
            list(bytes): The reconstructed blocks
        """
        reconstructed_blocks = []
        for i in missing_fragment_indexes:
            reconstructed_blocks.append(available_fragment_payloads[i])
        return reconstructed_blocks
