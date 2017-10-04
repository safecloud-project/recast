"""
Metadata management for the files and blocks stored in playcloud
"""
import datetime
import logging
import json
import random
import time

import enum
import numpy
import redis

LOGGER = logging.getLogger("metadata")

def compute_block_key(path, index, length=2):
    """
    Computes a block key from a file path and an index.
    Args:
        path(str): Path to the file related to the blocloggerk
        index(int): index of the block
        length(int, optional): Length of the index part of the key for zero filling (Defaults to 2)
    Returns:
        str: Block key
    """
    return path + "-" + str(index).zfill(length)

def uniform_random_selection(t, n):
    """
    Args:
        t(int): Number of pointers
        n(int): Number of blocks avaialable
    Returns:
        list(int): A list of indices that can be used for random selection of t
                   elements in a list of n elements
    """
    if t >= n:
        return [index for index in xrange(n)]
    difference = n - t
    if difference < t:
        selected = [index for index in xrange(n)]
        while len(selected) > t:
            selected.pop(random.randint(0, len(selected) - 1))
        return selected
    selected = []
    while len(selected) < t:
        index = random.randint(0, n - 1)
        if index not in selected:
            selected.append(index)
    return selected

def normal_selection(t, n, std=1000):
    """
    Select pointer indices using normal distribution
    Args:
        t(int): Number of pointers
        n(int): Number of blocks
        std(int, optional): Standard deviation (defaults to 1000)
    Returns:
        list(int): A list of unique indices ranging from 0 to (n - 1) selected
                   using normal distribution
    """
    selected = []
    if t >= n:
        return [element for element in xrange(n)]
    std = min(n, std)
    difference = n - t
    if difference < t:
        selected = [index for index in xrange(n)]
        while len(selected) > t:
            index = int(round(numpy.random.normal(len(selected), min(std, len(selected)))))
            if index < 0 or index >= len(selected): # Checking that we are withtin bounds
                continue
            selected.pop(index)
        return selected
    while len(selected) < t:
        index = int(round(numpy.random.normal(n, std)))
        if index < 0 or index >= n: # Checking that we are withtin bounds
            continue
        if index in selected:
            continue
        selected.append(index)
    return selected


class BlockType(enum.Enum):
    """
    Informs on the type of block and its use where DATA blocks are needed for
    decoding while PARITY blocks are needed for reconstruction
    """
    DATA = 0
    PARITY = 1

class MetaBlock(object):
    """
    A class that represents a data block
    """
    def __init__(self, key, providers=None, creation_date=None,
                 block_type=BlockType.DATA, checksum=None, entangled_with=None,
                 size=0):
        """
        MetaBlock constructor
        Args:
            key (str): Key under which the block is stored
            providers (list(str), optional): Ids of the providers
            creation_date (datetime.datetime, optional): Time of creation of the
                                                         block, defaults to
                                                         current time
            block_type (BlockType, optional): Type of the block
            checksum (bytes, optional): SHA256 digest of the data
            entangled_with(list(str), optional): List of documents the block is
                                                 entangled with
        """
        self.key = key
        if providers:
            self.providers = providers
        else:
            self.providers = []
        if creation_date is None:
            self.creation_date = datetime.datetime.now()
        else:
            self.creation_date = creation_date
        self.block_type = block_type
        self.checksum = checksum
        if entangled_with:
            self.entangled_with = entangled_with
        else:
            self.entangled_with = []
        self.size = size

    def __json__(self):
        """
        Returns a representation of a MetaBlock as a serializable dictionary
        Returns:
            dict: Returns a representation of a MetaBlock as a serializable dictionary
        """
        return {
            "key": self.key,
            "providers": [provider for provider in self.providers],
            "creation_date": self.creation_date.isoformat(),
            "block_type": self.block_type.name,
            "checksum": convert_binary_to_hex_digest(self.checksum),
            "entangled_with": self.entangled_with
        }

    def __str__(self):
        """
        Returns a string representation of a Metadata object
        Return:
            str: a string representation of a Metadata object
        """
        return json.dumps(self.__json__())

def convert_binary_to_hex_digest(binary_digest):
    """
    Converts a binary digest from hashlib.sha256.digest
    Args:
        binary_digest(str): Binary digest from hashlib.sha256.digest()
    Returns:
        str: Equivalent of the hexdigest for the same input
    """
    return "".join(["{:02x}".format(ord(c)) for c in binary_digest])

class Metadata(object):
    """
    A class describing how a file has been stored in the system
    """

    def __init__(self, path, original_size=0):
        """
        Constructor for Metadata objects
        Args:
            path(string): Path to the file in the system
            original_size(int): Original size of the file in bytes
        """
        self.path = path
        self.creation_date = datetime.datetime.now()
        self.blocks = []
        self.entangling_blocks = []
        self.original_size = original_size

    def __json__(self):
        """
        Returns a representation of a MetaBlock as a serializable dictionary
        Returns:
            dict: Returns a representation of a MetaBlock as a serializable dictionary
        """
        return {
            "path": self.path,
            "creation_date": self.creation_date.isoformat(),
            "blocks": [block.__json__() for block in self.blocks],
            "entangling_blocks": self.entangling_blocks,
            "original_size": self.original_size
        }

    def __str__(self):
        """
        """
        return json.dumps(self.__json__())

def extract_entanglement_data(block_data):
    """
    Extract and list the entangling information from the blocks header
    Args:
        block_data(str): A data block with an entanglement header
    Returns:
        list((str, int)): A list of the blocks used for entanglement
    """
    header_delimiter = chr(29)
    pos = block_data.find(header_delimiter)
    if pos <= 0:
        return ""
    raw_header = block_data[:pos]
    formatted_header = json.loads(raw_header)
    return formatted_header

class Files(object):
    """
    Represents metadata stored in the cluster
    """
    FILE_PREFIX = "files:"
    BLOCK_PREFIX = "blocks:"

    def __init__(self, host="metadata", port=6379, pointer_selector=normal_selection):
        self.redis = redis.StrictRedis(host=host, port=port)
        self.select_pointers = pointer_selector

    def get(self, path):
        """
        Returns a Metadata object stored under a given path.
        Args:
            path(str): The key the Metadata object was stored under
        Returns:
            Metadata: The Metadata object stored under the key
        Raises:
            ValueError: If path is an empty string
        """
        if not path:
            raise ValueError("path argument must be a valid non-empty string")
        return self.get_files([path])[0]

    def get_files(self, paths):
        """
        Returns a Metadata object stored under a given path.
        Args:
            paths(list(str)): The key the Metadata object was stored under
        Returns:
            Metadata: The Metadata object stored under the key
        Raises:
            ValueError: If the paths argument is an empty list or if one of the
                        paths is an empty string
            KeyError: If one of the paths requested does not exist
        """
        if not paths:
            raise ValueError("path argument must be a valid list of string")

        pipeline = self.redis.pipeline()
        translated_paths = []
        # Pipeline command to check that all paths exist
        for path in paths:
            if not path:
                raise ValueError("path in paths list must be a valid non-empty string")
            file_key = "{:s}{:s}".format(Files.FILE_PREFIX, path)
            translated_paths.append(file_key)
            pipeline.exists(file_key)
        # Check result from pipelined exists requests to make sure that all the
        # paths exist and pipeline command to get file hashes
        for index, in_database in enumerate(pipeline.execute()):
            if not in_database:
                raise KeyError("path {:s} not found".format(paths[index]))
            pipeline.hgetall(translated_paths[index])
        hashes = pipeline.execute()
        metadata = []
        keys = []
        for hsh in hashes:
            mtdt = Files.parse_metadata(hsh)
            keys += hsh.get("blocks").strip().split(",")
            metadata.append(mtdt)
        blocks = self.get_blocks(keys)
        step = len(blocks) / len(metadata)
        for index in xrange(0, len(metadata)):
            metadata[index].blocks = blocks[index * step:(index * step) + step]
        return sorted(metadata, key=lambda mtdt: mtdt.path)

    def get_block(self, key):
        """
        Returns a block from the database
        Returns:
            key(str): The key under which a block is stored
        Returns:
            MetaBlock: The MetaBlock that was retrieved
        """
        return self.get_blocks([key])[0]

    def get_blocks(self, keys):
        """
        Returns multiple blocks from the database
        Args:
            keys(list(str)): A list of keys under witch the blocks to fetch are stored
        Returns:
            list(MetaBlock): The MetaBlocks that were retrieved
        Raises:
            KeyError: If one of the keys does not exist
        """
        pipeline = self.redis.pipeline()
        translated_keys = ["{:s}{:s}".format(Files.BLOCK_PREFIX, key) for key in keys]
        for key in translated_keys:
            pipeline.exists(key)
        for index, is_in_database in enumerate(pipeline.execute()):
            if not is_in_database:
                raise KeyError("key {:s} not found ({:d} = {:s})".format(keys[index], index, translated_keys[index]))
            pipeline.hgetall(translated_keys[index])
        blocks = [Files.parse_metablock(hsh) for hsh in pipeline.execute()]
        return sorted(blocks, key=lambda block: block.key)

    def put(self, path, metadata):
        """
        Stores a Metadata object using the given path as the key
        Args:
            metadata(Metadata): The object to store
        Returns:
            str: The key under which the object was stored
        """
        start = time.clock()
        if not path:
            raise ValueError("path argument must be a valid non-empty string")
        if not metadata:
            raise ValueError("metadata argument must be a valid Metadata object")
        entangling_block_keys = [compute_block_key(eb[0], eb[1]) for eb in metadata.entangling_blocks]
        entangling_blocks = self.get_blocks(entangling_block_keys)

        pipeline = self.redis.pipeline(transaction=True)
        for block in entangling_blocks:
            block.entangled_with.append(path)
            pipeline.hset("{:s}{:s}".format(Files.BLOCK_PREFIX, block.key),
                          "entangled_with",
                          ",".join(sorted(block.entangled_with)))
        meta_hash = {
            "path": metadata.path,
            "creation_date": str(metadata.creation_date),
            "original_size": metadata.original_size,
            "blocks": ",".join([block.key for block in metadata.blocks]),
            "entangling_blocks": json.dumps(metadata.entangling_blocks)
        }
        block_keys = []
        for block in metadata.blocks:
            block_hash = {
                "key": block.key,
                "creation_date": str(block.creation_date),
                "providers": ",".join(sorted(block.providers)),
                "block_type": block.block_type.name,
                "checksum": block.checksum,
                "entangled_with": ",".join(sorted(block.entangled_with)),
                "size": block.size
            }
            metablock_key = "{:s}{:s}".format(Files.BLOCK_PREFIX, block.key)
            timestamp = (block.creation_date - datetime.datetime(1970, 1, 1)).total_seconds()
            block_keys.append(timestamp)
            block_keys.append(block.key)
            pipeline.hmset(metablock_key, block_hash)
        pipeline.zadd("block_index", *block_keys)
        pipeline.hmset("files:{:s}".format(path), meta_hash)
        timestamp = (metadata.creation_date - datetime.datetime(1970, 1, 1)).total_seconds()
        pipeline.zadd("file_index", timestamp, path)
        pipeline.execute()
        end = time.clock()
        elapsed = end - start
        LOGGER.info("Storing metadata for {:s} took {:f} seconds".format(path, elapsed))
        return path

    @staticmethod
    def parse_metablock(record):
        """
        Parses a metablock from an object
        Args:
            record(dict): A dictionary describing the metablock
        Returns:
            MetaBlock: The parsed MetaBlock
        """
        key = record.get("key")
        creation_date = datetime.datetime.strptime(record.get("creation_date"),
                                                   "%Y-%m-%d %H:%M:%S.%f")
        providers = record.get("providers").strip()
        if providers:
            providers = providers.split(",")
        else:
            providers = []

        entangled_with = record.get("entangled_with", "").strip()
        if entangled_with:
            entangled_with = entangled_with.split(",")
        else:
            entangled_with = []

        block_type = BlockType[record.get("block_type")]
        checksum = record.get("checksum")
        size = int(record.get("size", "0"))
        metablock = MetaBlock(key,
                              creation_date=creation_date,
                              providers=providers,
                              block_type=block_type,
                              checksum=checksum,
                              entangled_with=entangled_with,
                              size=size)
        return metablock

    @staticmethod
    def parse_metadata(record):
        """
        Parses metadata information from a record.
        Args:
            record(dict): A dictionary describing the metadata
        Returns:
            Metadata: The parsed Metadata
        """
        path = record.get("path")
        original_size = int(record.get("original_size"))
        creation_date = datetime.datetime.strptime(record.get("creation_date"),
                                                   "%Y-%m-%d %H:%M:%S.%f")
        metadata = Metadata(path, original_size=original_size)
        metadata.creation_date = creation_date
        metadata.entangling_blocks = json.loads(record.get("entangling_blocks"))
        return metadata

    def keys(self):
        """
        Returns a list of all the files stored in the system
        Returns:
            list(str): The list of files in the system
        """
        return self.redis.zrange("file_index", 0, -1)

    def list_blocks(self):
        """
        Returns a list of the blocks in the system
        Returns:
            list(str): A list of all the blocks in the system
        """
        return self.redis.zrange("block_index", 0, -1)

    def values(self):
        """
        Returns all files metadata objects
        Returns:
            list(Metadata): All the metadata object stored in the system
        """
        filenames = self.keys()
        if not filenames:
            return []
        return self.get_files(filenames)

    def select_random_blocks(self, requested):
        """
        Returns up to blocks_desired randomly selected metablocks from the index
        Args:
            requested(int): The number of random blocks to select
        Returns:
            list(MetaBlock): randomly selected blocks
        """
        start = time.clock()
        blocks_desired = requested
        blocks_available = self.redis.zcard("block_index")

        if blocks_available <= blocks_desired:
            block_keys = self.redis.zrange("block_index", 0, blocks_available)
            return [self.get_block(key) for key in block_keys]

        selected_indexes = self.select_pointers(blocks_desired, blocks_available)

        selected_keys = []
        for index in selected_indexes:
            selected_key = self.redis.zrange("block_index", index, index + 1)[0]
            selected_keys.append(selected_key)
        random_blocks = self.get_blocks(selected_keys)
        end = time.clock()
        elapsed = end - start
        LOGGER.info("Took {:f} seconds to select random blocks".format(elapsed))
        return random_blocks

    def get_entanglement_graph(self):
        """
        Scan the database to return the entanglement graph
        Returns:
            dict(str, list): The entanglement graph
        """
        graph = {}
        filenames = self.keys()
        for filename in filenames:
            metadata = self.get(filename)
            creation_date = str(metadata.creation_date)
            entangling_blocks = json.dumps(metadata.entangling_blocks)
            blocks = str([[block.key, block.providers[0]] for block in metadata.blocks])
            graph[filename] = [
                creation_date,
                entangling_blocks,
                blocks
            ]
        return graph

    def has_been_entangled_enough(self, block_key, pointers):
        """
        Tests whether a block can have its replicas deleted due to a high enough
        number of pointers directed at it.
        Returns True if it is entangled with enough documents to have its replicas
        deleted, False otherwise.
        Args:
            block_key(str): Path of the block
            pointers(int): The number of documents that use the block as part of
                           their entanglement
        Returns:
            bool: Whether the replicas of the block can be erased
        Raises:
            ValueError:
                * if path is not of type `str` or empty
                * if pointers is not of type `int` or is lower than 0
        """
        if not block_key or not isinstance(block_key, str):
            raise ValueError("path argument must be a valid non-empty string")
        if not isinstance(pointers, int) or pointers < 0:
            raise ValueError("pointers argument must be a valid integer greater or equal to 0")
        metablock = self.get_block(block_key)
        return len(metablock.entangled_with) >= pointers
