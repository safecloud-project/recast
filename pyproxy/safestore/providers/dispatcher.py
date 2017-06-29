"""
A component that distributes blocks for storage keeps track of their location
"""
import datetime
import hashlib
import logging
import logging.config
import random
import re
import threading

from redis import ConnectionError

from coder_client import CoderClient
from enum import Enum
from dbox import DBox
from gdrive import GDrive
from one import ODrive
from playcloud_pb2 import Strip
from redis_provider import RedisProvider

logger = logging.getLogger("dispatcher")


class Providers(Enum):
    """
    Enumeration of all the storage providers supported by the Dispatcher
    """
    redis = 0
    gdrive = 1
    dropbox = 2
    onedrive = 3

class ProviderFactory(object):
    """
    Creates storage providers based on configuration
    """
    def __init__(self):
        self.initializers = {
            Providers.dropbox.name: DBox,
            Providers.gdrive.name: GDrive,
            Providers.redis.name: RedisProvider,
            Providers.onedrive.name: ODrive
        }

    def get_provider(self, configuration={}):
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
        provider_type = configuration.get("type", None)
        if provider_type is None:
            raise Exception("configuration parameter must have a type key-value pair")
        initializer = self.initializers.get(provider_type)
        if initializer is None:
            raise Exception("configuration type is not supported by the factory")
        if provider_type == Providers.redis.name:
            return initializer(configuration)
        return initializer()

class BlockType(Enum):
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
    def __init__(self, key, provider=None, creation_date=None, block_type=BlockType.DATA, checksum=None):
        """
        MetaBlock constructor
        Args:
            key (str): Key under which the block is stored
            provider (str, optional): Id of the provider
            creation_date (datetime.datetime, optional): Time of creation of the
                block, defaults to current time
            block_type (BlockType, optional): Type of the block
            checksum (str, optional): SHA256 digest of the data
        """
        self.key = key
        self.provider = provider
        if creation_date is None:
            self.creation_date = datetime.datetime.now()
        else:
            self.creation_date = creation_date
        self.block_type = block_type
        self.checksum = checksum

def compute_block_key(path, index, length=2):
    """
    Computes a block key from a file path and an index.
    Args:
        path(str): Path to the file related to the block
        index(int): index of the block
        length(int, optional): Length of the index part of the key for zero filling (Defaults to 2)
    Returns:
        str: Block key
    """
    return path + "-" + str(index).zfill(length)

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
        loop_temp = "Going to put block with key {} in provider {}"
        for metablock, data in self.blocks.iteritems():
            logger.debug(loop_temp.format(metablock.key, str(type(self.provider))))
            self.provider.put(data, metablock.key)
            index = extract_index_from_key(metablock.key)
            self.queue[index] = metablock

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

class BlockFetcher(threading.Thread):
    """
    Threaded code to fetch blocks from a storage provider
    """

    def __init__(self, provider, metablocks, queue):
        """
        Initializes the block fetcher
        Args:
            provider -- The provider that will store the data (Provider)
            metablocks -- The list of block keys that constitutes the file (list(MetaBlock))
            queue --  Dictionary where the recoveded data will be pushed  (dict)
        """
        super(BlockFetcher, self).__init__()
        self.logger = logging.getLogger("BlockFetcher")
        self.provider = provider
        self.metablocks = metablocks
        self.queue = queue

    def run(self):
        """
        Fetches a series of blocks and pushes them the queue
        """
        for metablock in self.metablocks:
            key = metablock.key
            self.logger.debug("About to fetch block " + key + " from the datastore")
            try:
                data = self.provider.get(key)
                if data is None:
                    message = "Block " + key + " cannot be found in the datastore"
                    raise BlockNotFoundException(message)
                self.logger.debug("Checking block " + key + "'s integrity")
                computed_checksum = hashlib.sha256(data).digest()
                if metablock.checksum != computed_checksum:
                    message = "Block " + key + " does not match its checksum"
                    raise CorruptedBlockException(message)
                self.logger.debug("Storing block " + key + " in synchronization queue")
                self.queue[key] = data
            except ConnectionError as exception:
                message = "Provider for block " + key + " cannot be accessed"
                exception = ProviderUnreachableException(message)
                self.logger.error(exception)
                self.queue[key] = exception
            except (BlockNotFoundException, \
                    CorruptedBlockException, \
                    ProviderUnreachableException) as exception:
                self.logger.error(exception)
                self.queue[key] = exception

def arrange_elements(elements, bins):
    """
    Propose elements arrangement among a number of bins
    Args:
        elements -- Number of elements to arrange (int)
        bins -- Number of bins to store the elements (int)
    Retunrs:
        A list of index lists describing how the elements can be spread among
        the bins
    """
    if elements < 0:
        raise ValueError("")
    if elements == 0 or bins == 0:
        return []
    start = random.randint(0, bins - 1)
    dispatching = []
    for i in range(bins):
        dispatching.append([])
    for i in range(elements):
        index = (start + i) % bins
        dispatching[index].append(i)
    return dispatching

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
        providers_configuration = configuration.get('providers', {})
        factory = ProviderFactory()
        for name, configuration in providers_configuration.items():
            self.providers[name] = factory.get_provider(configuration)
        self.files = {}

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
        metadata = Metadata(path, original_size=long(encoded_file.original_size))
        provider_keys = self.providers.keys()
        blocks = [s.data for s in encoded_file.strips]
        blocks_to_store = blocks
        arrangement = arrange_elements(len(blocks_to_store), len(provider_keys))
        metablock_queue = {}
        block_pushers = []
        index_format_length = len(str(len(blocks)))
        for i, provider_key in enumerate(provider_keys):
            provider = self.providers[provider_key]
            blocks_for_provider = {}
            for index in arrangement[i]:
                strip = encoded_file.strips[index]
                key = compute_block_key(path, index, index_format_length)
                block_type = None
                if  strip.type == Strip.DATA:
                    block_type = BlockType.DATA
                else:
                    block_type = BlockType.PARITY
                metablock = MetaBlock(key,
                                      provider=provider_key,
                                      checksum=strip.checksum,
                                      block_type=block_type)
                blocks_for_provider[metablock] = strip.data
            pusher = BlockPusher(provider, blocks_for_provider, metablock_queue)
            pusher.start()
            block_pushers.append(pusher)
        for pusher in block_pushers:
            pusher.join()
        for index in sorted(metablock_queue.keys()):
            metadata.blocks.append(metablock_queue[index])
        self.files[path] = metadata
        return metadata

    def get_block(self, path, index):
        """
        Returns a single block for the data store.
        Args:
            path(str): Key under which the file is stored
            index(int): Index of the block
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
            raise LookupError("could not find a file for path " + path)
        if index >= len(metadata.blocks):
            raise LookupError("could not find block for index " + str(index))

        #TODO get block using self.__get_blocks
        block = metadata.blocks[index]
        provider = self.providers[block.provider]
        data = provider.get(block.key)
        if data is None:
            coder_client = CoderClient()
            data = coder_client.reconstruct(path, [index])[index].data
        return data

    def __get_blocks(self, metablocks):
        """
        Args:
            metablocks(list): The list of metablocks describing the blocks to get
                              from the data stores
        Returns:
            dict(metablock, bytes): The blocks fetched from the data stores
        """
        blocks_per_provider = {}
        for metablock in metablocks:
            blocks_to_fetch = blocks_per_provider.get(metablock.provider, [])
            blocks_to_fetch.append(metablock)
            blocks_per_provider[metablock.provider] = blocks_to_fetch
        fetchers = []
        blocks = {}
        for provider_key in blocks_per_provider:
            provider = self.providers[provider_key]
            blocks_to_fetch = blocks_per_provider[provider_key]
            fetcher = BlockFetcher(provider, blocks_to_fetch, blocks)
            fetcher.start()
            fetchers.append(fetcher)
        for fetcher in fetchers:
            fetcher.join()
        return blocks

    def get(self, path):
        """
        Recovers and orders blocks stored among the providers
        Args:
            path: Key under which the data is stored
        Returns:
            A list of blocks if the file was stored in the system, None otherwise
        """
        metadata = self.files.get(path)
        if metadata is None:
            return None
        metablocks = [b for b in metadata.blocks if b.block_type == BlockType.DATA]

        block_queue = self.__get_blocks(metablocks)

        blocks_to_reconstruct = []
        for key in sorted(block_queue.keys()):
            block = block_queue[key]
            if isinstance(block, (ProviderUnreachableException, \
                                   BlockNotFoundException, \
                                   CorruptedBlockException)):
                missing_index = extract_index_from_key(key)
                del block_queue[key]
                blocks_to_reconstruct.append(missing_index)

        if blocks_to_reconstruct:
            coder = CoderClient()
            reconstructed_blocks = coder.reconstruct(path, blocks_to_reconstruct)
            index_format_length = len(str(len(metablocks)))
            for index in sorted(reconstructed_blocks.keys()):
                key = compute_block_key(path, index, index_format_length)
                strip = reconstructed_blocks[index]
                block_queue[key] = strip.data
        data_blocks = [block_queue[key] for key in sorted(block_queue.keys())]
        return data_blocks

    def __get_flat_list_of_data_metablocks(self):
        """
        Returns a flat list of the metablocks pointing to data type blocks
        Returns:
            list(MetaBlock): A list of all the metablocks in the system
        """
        data_metablocks = []
        for filename in self.files:
            for block in self.files[filename].blocks:
                if block.block_type == BlockType.DATA:
                    data_metablocks.append(block)
        return data_metablocks

    @staticmethod
    def __select_randomly(k, elements):
        """
        Returns up to k items from elements.
        Args:
            k(int): The number of elements to select
            elements(list): A list of elements
        Returns:
            list: The list of elements to select
        """
        k_needed = min(k, len(elements))
        if k_needed == len(elements):
            return elements[:]
        selected = []
        while len(selected) < k_needed:
            chosen = random.choice(elements)
            if chosen not in selected:
                selected.append(chosen)
        return selected

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
        all_metablocks = self.__get_flat_list_of_data_metablocks()
        random_metablocks = self.__select_randomly(blocks_desired, all_metablocks)

        block_queue = self.__get_blocks(random_metablocks)

        random_blocks = []
        for key, block in block_queue.iteritems():
            if  isinstance(block, (BlockNotFoundException, \
                                   ProviderUnreachableException, \
                                   CorruptedBlockException)):
                continue
            random_blocks.append((key, block))
        return random_blocks
