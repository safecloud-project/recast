"""
A module with entanglement utilities
"""
import json
import logging
import logging.config
import math
import os

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
            for i in xrange(length_diff):
                block_b += '\0'
        elif length_diff < 0:
            block_b = block_b[0:length_diff]

        a = numpy.frombuffer(block_a, dtype='b')
        b = numpy.frombuffer(block_b, dtype='b')
        c = numpy.bitwise_xor(a, b).tostring()
        return c


class EntanglementDriver(object):
    """
    A driver for the playcloud coder that performs entanglement by fetching
    blocks from the proxy and combining them with the given blocks
    """
    # Use the Group Separator from the ASCII table as the delimiter between the
    # entanglement header and the data itself
    # https://www.lammertbies.nl/comm/info/ascii-characters.html
    CUTOFF_SYMBOL = chr(29)

    def __init__(self, block_source, entanglement=Dagster, source_blocks=5):
        """
        Args:
            block_source(object): An entity that can return random blocks
            entanglement(Entangler): A type of entanglement to use (defaults to Dagster)
            source_blocks(int): The number of source blocks to entangle with (defaults to 5)
        """
        self.source = block_source
        self.k = 5
        self.entangler = entanglement()
        self.source_blocks = source_blocks
        local_directory = os.path.dirname(__file__)
        log_config = os.getenv("LOG_CONFIG", os.path.join(local_directory, "logging.conf"))
        logging.config.fileConfig(log_config)
        self.logger = logging.getLogger("EntanglementDriver")


    @staticmethod
    def __split_data(data, k):
        fragment_size = int(math.ceil(float(len(data)) / k))
        fragments = []
        for i in range(k):
            offset = i * fragment_size
            fragments.append(data[offset:offset + fragment_size])
        return fragments

    @staticmethod
    def __merge_data(fragments):
        return "".join(fragments)

    @staticmethod
    def __generate_entanglement_header(blocks):
        header = [(block.key, block.index) for block in blocks]
        return json.dumps(header)

    @staticmethod
    def __read_entanglement_header(header):
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
        if self.source_blocks > 0:
            random_blocks = self.source.get_random_blocks(self.source_blocks)
        block_header = EntanglementDriver.__generate_entanglement_header(random_blocks)
        random_blocks = [block.data for block in random_blocks]
        self.logger.info(block_header)
        encoded_blocks = []
        for block in blocks:
            encoded_block, random_blocks = self.entangler.entangle(block, random_blocks)
            encoded_block = block_header + self.CUTOFF_SYMBOL + encoded_block
            encoded_blocks.append(encoded_block)
        return encoded_blocks

    def decode(self, strips):
        """
        Decodes strip into the original data.
        Args:
            strips(list(bytes)): The encoded data as a list of bytes
        Returns:
            bytes: The decoded data
        """
        random_blocks = []
        if self.source_blocks > 0:
            random_blocks = self.source.get_random_blocks(self.source_blocks)
        block_header = EntanglementDriver.__read_entanglement_header(strips[0].split(self.CUTOFF_SYMBOL)[0])
        strips = [strip.split(self.CUTOFF_SYMBOL)[1] for strip in strips]
        random_blocks = [block.data for block in random_blocks]
        self.logger.info(block_header)
        decoded_blocks = []
        for strip in strips:
            decoded_block, random_blocks = self.entangler.disentangle(strip, random_blocks)
            decoded_blocks.append(decoded_block)
        return self.__merge_data(decoded_blocks)

    def fragments_needed(self, given):
        """
        Returns the ids of the fragments needed to reconstruct the missing fragments
        Args:
            given(list(int)): Indices of the available fragments
        Returns:
            list(int): The indices of the fragments needed for reconstruction
        """
        return [index for index in xrange(self.k) if index not in given]


class DataBlock(object):
    def __init__(self, key, index, data):
        self.key = key
        self.index = index
        self.data = data

class BlockSource(object):
    def __init__(self, block_size):
        self.block_size = block_size

    def get_random_blocks(self, blocks):
        random_blocks = []
        for i in xrange(blocks):
            block = ""
            for j in xrange(self.block_size):
                block += '\0'
            random_blocks.append(DataBlock("myfile", j, block))
        return random_blocks


if __name__ == "__main__":
    with open("entangled_driver.py", "r") as f:
        DATA = f.read()
    BLOCK_SIZE = int(math.ceil(float(len(DATA)) / 5))
    SOURCE = BlockSource(BLOCK_SIZE)
    SOURCE_BLOCKS = 3
    DRIVER = EntanglementDriver(SOURCE, source_blocks=SOURCE_BLOCKS)
    ENCODED = DRIVER.encode(DATA)
    DECODED = DRIVER.decode(ENCODED)
    assert DECODED == DATA
