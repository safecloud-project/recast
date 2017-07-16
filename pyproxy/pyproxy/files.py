"""
Metadata for the plaucloud files
"""
import datetime

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

class Files(object):
    """
    Represents metadata stored in the cluster
    """
    def __init__(self, host="127.0.0.1", port=6379):
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
        for key in block_keys:
            mb_record = self.redis.hgetall(key)
            metablock = Files.parse_metablock(mb_record)
            metadata.blocks.append(metablock)
        return metadata

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
            "blocks": ",".join([block.key for block in metadata.blocks])
        }
        blocks = {}
        for block in metadata.blocks:
            block_hash = {
                "key": block.key,
                "creation_date": str(block.creation_date),
                "providers": ",".join(sorted(block.providers)),
                "block_type": block.block_type.name,
                "checksum": block.checksum
            }
            blocks[block.key] = block_hash
        self.redis.hmset("files:{:s}".format(path), meta_hash)
        for key, block_hash in blocks.iteritems():
            self.redis.hmset(key, block_hash)
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
        return metadata

    def keys(self):
        """
        Returns a list of all the files stored in the system
        Returns:
            list(str): The list of files in the system
        """
        keys = [key.replace(r"files:", "") for key in self.redis.keys("files:*")]
        return keys

    def values(self):
        """
        Returns all files metadata objects
        Returns:
            list(Metadata): All the metadata object stored in the system
        """
        filenames = self.keys()
        records = self.redis.mget(filenames)
        values = [Files.parse_metadata(record) for record in records]
        return values
