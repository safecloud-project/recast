"""
Metadata management for the files and blocks stored in playcloud
"""
import datetime
import json
import random

import enum
import redis

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
                 block_type=BlockType.DATA, checksum=None):
        """
        MetaBlock constructor
        Args:
            key (str): Key under which the block is stored
            providers (list(str), optional): Ids of the providers
            creation_date (datetime.datetime, optional): Time of creation of the
                block, defaults to current time
            block_type (BlockType, optional): Type of the block
            checksum (str, optional): SHA256 digest of the data
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
            "checksum": convert_binary_to_hex_digest(self.checksum)
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

    def __init__(self, host="metadata", port=6379):
        #TODO replace file_index and block_index lists with ordered sets
        self.redis = redis.StrictRedis(host=host, port=port)

    def get(self, path):
        """
        Returns a Metadata object stored under a given path.
        Args:
            path(str): The key the Metadata object was stored under
        Returns:
            Metadata: The Metadata object stored under the key
        """
        if not path:
            raise ValueError("path argument must be a valid non-empty string")
        record = self.redis.hgetall("files:{:s}".format(path))
        if not record:
            raise KeyError("path {} not found".format(path))
        metadata = Files.parse_metadata(record)
        block_keys = record.get("blocks").strip().split(",")
        metadata.blocks = self.get_blocks(block_keys)
        return metadata

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
        """
        pipeline = self.redis.pipeline()
        for key in keys:
            block_key = "{:s}{:s}".format(Files.BLOCK_PREFIX, key)
            pipeline.hgetall(block_key)
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
        if not path:
            raise ValueError("path argument must be a valid non-empty string")
        if not metadata:
            raise ValueError("metadata argument must be a valid Metadata object")
        meta_hash = {
            "path": metadata.path,
            "creation_date": str(metadata.creation_date),
            "original_size": metadata.original_size,
            "blocks": ",".join([block.key for block in metadata.blocks]),
            "entangling_blocks": json.dumps(metadata.entangling_blocks)
        }
        pipeline = self.redis.pipeline(transaction=True)
        block_keys = []
        for block in metadata.blocks:
            block_hash = {
                "key": block.key,
                "creation_date": str(block.creation_date),
                "providers": ",".join(sorted(block.providers)),
                "block_type": block.block_type.name,
                "checksum": block.checksum
            }
            metablock_key = "{:s}{:s}".format(Files.BLOCK_PREFIX, block.key)
            block_keys.append(block.key)
            pipeline.hmset(metablock_key, block_hash)
        pipeline.rpush("block_index", *block_keys)
        pipeline.hmset("files:{:s}".format(path), meta_hash)
        pipeline.rpush("file_index", *[path])
        pipeline.execute()
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
        block_type = BlockType[record.get("block_type")]
        checksum = record.get("checksum")
        metablock = MetaBlock(key,
                              creation_date=creation_date,
                              providers=providers,
                              block_type=block_type,
                              checksum=checksum)
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
        return self.redis.lrange("file_index", 0, -1)

    def values(self):
        """
        Returns all files metadata objects
        Returns:
            list(Metadata): All the metadata object stored in the system
        """
        filenames = self.keys()
        if not filenames:
            return []
        return [self.get(f) for f in filenames]

    def select_random_blocks(self, requested):
        """
        Returns up to blocks_desired randomly selected metablocks from the index
        Args:
            requested(int): The number of random blocks to select
        Returns:
            list(MetaBlock): randomly selected blocks
        """
        blocks_desired = requested
        blocks_available = self.redis.llen("block_index")

        if blocks_available <= blocks_desired:
            block_keys = self.redis.lrange("block_index", 0, blocks_available)
            return [self.get_block(key) for key in block_keys]

        selected_indexes = []
        while len(selected_indexes) < blocks_desired:
            chosen_index = random.randint(0, blocks_available - 1)
            if chosen_index not in selected_indexes:
                selected_indexes.append(chosen_index)

        selected_keys = []
        for index in selected_indexes:
            selected_key = self.redis.lrange("block_index", index, index + 1)[0]
            selected_keys.append(selected_key)
        return self.get_blocks(selected_keys)

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
