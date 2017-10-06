"""
A component that distributes blocks for storage keeps track of their location
"""
import hashlib
import logging
import random
import re
import threading
import time
from multiprocessing import Manager

from enum import Enum
from redis import ConnectionError

import pyproxy.coder_client
from pyproxy.metadata import BlockType, compute_block_key, Files, MetaBlock, Metadata
from pyproxy.safestore.providers.dbox import DBox
from pyproxy.safestore.providers.disk import Disk
from pyproxy.safestore.providers.gdrive import GDrive
from pyproxy.safestore.providers.one import ODrive
from pyproxy.safestore.providers.redis_provider import RedisProvider
from pyproxy.safestore.providers.s3 import S3Provider
from pyproxy.playcloud_pb2 import Strip

logger = logging.getLogger("dispatcher")


class Providers(Enum):
    """
    Enumeration of all the storage providers supported by the Dispatcher
    """
    redis = 0
    gdrive = 1
    dropbox = 2
    onedrive = 3
    disk = 4
    s3 = 5


class ProviderFactory(object):
    """
    Creates storage providers based on configuration
    """
    def __init__(self):
        self.initializers = {
            Providers.dropbox.name: DBox,
            Providers.gdrive.name: GDrive,
            Providers.redis.name: RedisProvider,
            Providers.onedrive.name: ODrive,
            Providers.disk.name: Disk,
            Providers.s3.name: S3Provider
        }

    def get_provider(self, configuration=None):
        """
        Return a storage provider based on the values in a dictionary
        Args:
            configuration -- A dictionary with the parameters to initialize the
                        storage provider
        Retruns:
            A storage provider
        Raises:
            Exception -- If the configuration dictionary does not have a type
                key or the value under key is not supported by the factory
        """
        configuration = configuration or None
        provider_type = configuration.get("type", None)
        if provider_type is None:
            raise Exception("configuration parameter must have a type key-value pair")
        initializer = self.initializers.get(provider_type)
        if initializer is None:
            message = "configuration type '{:s}' is not supported by the factory".format(provider_type)
            raise Exception(message)
        if provider_type == Providers.redis.name:
            return initializer(configuration)
        if provider_type == Providers.disk.name:
            return initializer(folder=configuration.get("folder", "/data"))
        return initializer()


def extract_path_from_key(key):
    """
    Extracts the path from a block key.
    Args:
        key(str): Block key
    Returns:
        path: Path of the file the block belongs to
    """
    path_pattern = re.compile(r"^(.+)\-\d+$")
    return path_pattern.findall(key)[0]


def extract_index_from_key(key):
    """
    Extracts the index from a block key.
    Args:
        key(str): Block key
    Returns:
        int: Index of the block
    """
    index_pattern = re.compile(r"\-\d+$")
    return int(index_pattern.findall(key)[0].replace("-", ""))


class CouldNotPushException(Exception):
    def __init__(self, provider, key):
        """
        Args:
            provider(str): Name of the provider
            path(str): key
        """
        super(Exception, self).__init__()
        self.provider = provider
        self.key = key


class BlockPusher(threading.Thread):
    """
    Threaded code to push blocks using a given provider
    """

    def __init__(self, provider, blocks, queue):
        """
        Initialize the BlockPusher by providing blocks to store in a provider
        the queue to push the metablocks produced by the insertion
        Args:
            provider(Provider) -- The provider that will store the data
            blocks(dict(MetaBlock, bytes) -- The list of blocks that constitutes the file
            queue(dict) --  Queue where the metablocks should be stored once the block are stored
        """
        super(BlockPusher, self).__init__()
        self.provider = provider
        self.blocks = blocks
        self.queue = queue

    def run(self):
        """
        Loop through self.blocks, selecting those stored at indices
        listed in self.indices and feeding them to self.provider for storage
        """
        loop_temp = "Going to put block with key {:s} in provider {:s}"
        for metablock, data in self.blocks.iteritems():
            logger.debug(loop_temp.format(metablock.key, str(type(self.provider))))
            try:
                self.provider.put(data, metablock.key)
                index = extract_index_from_key(metablock.key)
                self.queue[index] = metablock
            except ConnectionError:
                index = extract_index_from_key(metablock.key)
                self.queue[index] = CouldNotPushException(self.provider, metablock.key)


class ProviderUnreachableException(Exception):
    """
    An exception raised when a provider cannot be connected to
    """
    pass


class BlockNotFoundException(Exception):
    """
    An exception raised when a block cannot be found at certain provider
    """
    pass


class CorruptedBlockException(Exception):
    """
    An exception raised when a block does not match its related checksum
    """
    pass


class NoReplicaException(Exception):
    """
    An exception raised when no valid replica could be found for a given block
    """
    pass


def place(elements, providers, replication_factor):
    """
    Arrange elements over a set of providers using round-robin selecting the
    first provider randomly.
    Args:
        elements(int): Number of elements to arrange
        providers(list(str)): Name of the providers
        replication_factor(int): Replication factor
    Returns:
        dict(str, set(int)): The arrangement of the elements over the providers
    """
    if not isinstance(elements, int) or elements < 0:
        raise ValueError("elements argument must be an integer greater or equal to 0")
    if not isinstance(providers, list):
        raise ValueError("providers argument must be a list of strings")
    if not isinstance(replication_factor, int) or replication_factor < 0:
        raise ValueError("replication_factor argument must be an integer greater or equal to 0")
    number_of_providers = len(providers)
    if elements == 0 or number_of_providers == 0 or replication_factor == 0:
        return {provider: set() for provider in providers}
    placement = {}
    if number_of_providers <= replication_factor:
        indices = set([index for index in xrange(elements)])
        for provider in providers:
            placement[provider] = indices
        return placement
    index = random.randint(0, number_of_providers - 1)
    for _ in xrange(replication_factor):
        for element in xrange(elements):
            provider_name = providers[index]
            provider = placement.get(provider_name, set())
            provider.add(element)
            placement[provider_name] = provider
            index = (index + 1) % number_of_providers
    return placement


def get_block(providers, metablock, queue):
    """
    Fetches a single block, randomly choosing a replica to return.
    If the replica cannot be found, it moves on to the next one and so on until a replica is found and added to the queue or no replica can be found and a NoReplicaException is added to the queue.
    Args:
        providers(dict(str, Provider)): List of providers that host a copy of the block
        metablock(MetaBlock): The metablock describing the block to fetch
        queue(dict(str, bytes)): The dictionary where the data should be pushed under the block's key
    """
    #TODO Push the errors (connection, integrity, not found, ...) into a proper
    # to apply the required fix
    key = metablock.key
    replica_providers = metablock.providers[:]
    random.shuffle(replica_providers)
    for provider_key in replica_providers:
        provider = providers[provider_key]
        logger.debug("About to fetch block {:s} from {:s}".format(key, provider_key))
        try:
            data = provider.get(key)
        except ConnectionError:
            message = "Received a connection error from provider {:s} trying to get block {:s}".format(provider_key, key)
            logger.error(message)
            continue
        if data is None:
            message = "Replica of block {:s} cannot be found in {:s}".format(key, provider_key)
            logger.error(message)
            continue
        logger.debug("Checking block {:s}'s integrity".format(key))
        computed_checksum = hashlib.sha256(data).digest()
        if metablock.checksum != computed_checksum:
            message = "Block {:s} does not match its checksum".format(key)
            logger.error(message)
            continue
        logger.debug("Storing block {:s} in synchronization queue".format(key))
        queue[key] = data
        return
    queue[key] = NoReplicaException("Could not found any (valid) replica of block {:s}".format(key))


class BlockFetcher(threading.Thread):
    """
    Fetches a block from the data nodes going through the provider where the blocks
    are available
    """
    def __init__(self, providers, metablock, queue):
        super(BlockFetcher, self).__init__()
        self.providers = providers
        self.metablock = metablock
        self.queue = queue

    def run(self):
        get_block(self.providers, self.metablock, self.queue)


class Dispatcher(object):
    """
    A class that decices where to store data blocks and keeps track of how to
    retrieve them
    """

    def __init__(self, configuration=None):
        """
        Dispatcher constructor
        Args:
            configuration (dict, optional): A dictionary with the configuration
                values of the dispatcher
        """
        if configuration is None:
            configuration = {}
        self.providers = {}
        providers_configuration = configuration.get("providers", {})
        factory = ProviderFactory()
        for name, config in providers_configuration.items():
            self.providers[name] = factory.get_provider(config)
        self.files = Files(host="metadata", port=6379)
        self.replication_factor = configuration.get("replication_factor", 3)

    def list(self):
        """
        Returns a list of the files stored in the system.
        Returns:
            list(Metadata): A list of Metadata objects representing the files
                            stored in the system
        """
        return self.files.values()

    def put(self, path, encoded_file):
        """
        Distribute blocks of a file among different providers.
        Args:
            path (str): Key under which the data is stored
            encoded_file (File): A File object with blocks to store
        Returns:
            A metadata object describing how the blocks have been stored
        """
        start = time.clock()
        metadata = Metadata(path, original_size=long(encoded_file.original_size))
        provider_keys = self.providers.keys()
        blocks = [strip.data for strip in encoded_file.strips]
        arrangement = place(len(blocks), provider_keys, self.replication_factor)
        metablock_queue = {}
        pushers = []
        metablocks = {}
        for provider_key in arrangement:
            provider = self.providers[provider_key]
            blocks_for_provider = {}
            for index in arrangement[provider_key]:
                index = index % len(encoded_file.strips)
                strip = encoded_file.strips[index]
                key = compute_block_key(path, index)
                block_type = BlockType.PARITY
                if strip.type == Strip.DATA:
                    block_type = BlockType.DATA
                metablock = metablocks.get(index,
                                           MetaBlock(key,
                                                     providers=[],
                                                     checksum=strip.checksum,
                                                     block_type=block_type,
                                                     size=len(strip.data)))
                metablock.providers.append(provider_key)
                metablocks[index] = metablock
                blocks_for_provider[metablock] = strip.data
            pusher = BlockPusher(provider, blocks_for_provider, metablock_queue)
            pusher.start()
            pushers.append(pusher)
        for pusher in pushers:
            pusher.join()
        for index in metablocks:
            metablock = metablocks[index]
            if isinstance(metablock, CouldNotPushException):
                error_message = "Could not push block {:d} to provider {}".format(index, metablock.provider)
                raise RuntimeError(error_message)
        for index, metablock in metablocks.items():
            metadata.blocks.append(metablock)
        end = time.clock()
        elapsed = end - start
        logger.info("Storing blocks for {:s} was done in {:f} s".format(path, elapsed))
        return metadata

    def __get_blocks(self, metablocks):
        """
        Args:
            metablocks(list): The list of metablocks describing the blocks to get
                              from the data stores
        Returns:
            dict(metablock, bytes): The blocks fetched from the data stores
        """
        manager = Manager()
        blocks = manager.dict()
        fetchers = []
        for metablock in metablocks:
            possible_providers = {key: self.providers[key] for key in metablock.providers}
            fetcher = BlockFetcher(possible_providers, metablock, blocks)
            fetcher.start()
            fetchers.append(fetcher)
        for fetcher in fetchers:
            fetcher.join()
        return blocks

    def get_block(self, path, index, reconstruct_if_missing=True):
        """
        Returns a single block for the data store.
        Args:
            path(str): Key under which the file is stored
            index(int): Index of the block
            reconstruct_if_missing(bool, optional): If the dispatcher should try
                                                    to reconstruct the block if
                                                    it cannot be fetched from
                                                    the storage nodes. Defaults
                                                    to True
        Returns:
            str: A block of data
        Raises:
            ValueError: if the path is empty or the index is negative
            LookupError: if the path does not match any file or the index does not
                         match an existing block
        """
        path = path.strip()
        if not path:
            raise ValueError("argument path cannot be empty")
        if index < 0:
            raise ValueError("argument index cannot be negative")
        metadata = self.files.get(path)
        if metadata is None:
            raise LookupError("could not find a file for path {:s}".format(path))
        if index >= len(metadata.blocks):
            raise LookupError("could not find block for index {:d}".format(index))

        metablock = metadata.blocks[index]
        data = self.__get_blocks([metablock])[metablock.key]
        if isinstance(data, NoReplicaException) and reconstruct_if_missing:
            coder_client = pyproxy.coder_client.CoderClient()
            data = coder_client.reconstruct(path, [index])[index].data
        return data

    def get(self, path):
        """
        Recovers and orders blocks stored among the providers
        Args:
            path: Key under which the data is stored
        Returns:
            A list of blocks if the file was stored in the system, None otherwise
        """
        try:
            metadata = self.files.get(path)
        except KeyError:
            return None
        metablocks = [b for b in metadata.blocks if b.block_type == BlockType.DATA]

        block_queue = self.__get_blocks(metablocks)
        missing_indices = []
        for key in sorted(block_queue.keys()):
            block = block_queue[key]
            if isinstance(block, NoReplicaException):
                missing_index = extract_index_from_key(key)
                missing_indices.append(missing_index)
                del block_queue[key]
                continue

        while len(block_queue) < len(metablocks):
            coder = pyproxy.coder_client.CoderClient()
            indices_needed = coder.fragments_needed(missing_indices)
            indices_secured = [extract_index_from_key(m) for m in block_queue.keys()]
            indices_to_compensate = list(set(indices_needed).difference(set(indices_secured)))
            metablocks_to_compensate = [m for m in metadata.blocks if extract_index_from_key(m.key) in indices_to_compensate]
            blocks_to_compensate = self.__get_blocks(metablocks_to_compensate)
            for key in sorted(blocks_to_compensate.keys()):
                block = blocks_to_compensate[key]
                index = extract_index_from_key(key)
                if isinstance(block, NoReplicaException):
                    missing_indices.append(index)
                    continue
                if index in missing_indices:
                    missing_indices.remove(index)
                block_queue[key] = block
            missing_indices = list(set(missing_indices))

        return [block_queue[key] for key in sorted(block_queue.keys())]

    def get_random_blocks(self, blocks_desired):
        """
        Tries to randomly select a number blocks from the storage providers.
        It may return between 0 and "blocks_desired" numbers depending on the
        number of blocks already present in the system.
        Args:
            blocks_desired -- The number of random blocks to select (int)
        Returns:
            A list of tuples where the first element is a metablock and the
            second one is the block data itself
        """
        full_start = time.clock()
        start = time.clock()
        random_metablocks = self.files.select_random_blocks(blocks_desired)
        block_queue = self.__get_blocks(random_metablocks)
        end = time.clock()
        logger.info("Took {:f} seconds to fetch {:d} random blocks".format(end - start, len(block_queue)))
        start = time.clock()
        random_blocks = []
        for key in block_queue.keys():
            block = block_queue.get(key)
            if  isinstance(block, NoReplicaException):
                continue
            random_blocks.append((key, block))
        end = time.clock()
        logger.info("Took {:f} seconds to filter and sort {:d} random blocks".format(end - start, len(random_blocks)))
        logger.info("Took {:f} seconds to fetch and order {:d} random blocks".format(end - full_start, len(random_blocks)))
        return random_blocks
