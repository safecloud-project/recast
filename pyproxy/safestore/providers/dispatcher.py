"""
A component that distributes blocks for storage keeps track of their location
"""
import datetime
import logging
import logging.config
import Queue
import random
import threading
import uuid

import numpy

from enum import Enum
from dbox import DBox
from gdrive import GDrive
from one import ODrive
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

class MetaBlock(object):
    """
    A class that represents a data block
    """
    def __init__(self, key, provider, creation_date=datetime.datetime.now()):
        self.key = key
        self.provider = provider
        self.creation_date = creation_date

class Metadata(object):
    """
    A class describing how a file has been stored in the system
    """

    def __init__(self, path):
        self.path = path
        self.creation_date = datetime.datetime.now()
        self.blocks = []
        self.entangling_blocks = []

class BlockPusher(threading.Thread):
    """
    Threaded code to push blocks using a given provider
    """

    def __init__(self, provider, provider_key, path, blocks, indices, queue):
        """
        Initialize the BlockPusher by providing blocks to store in a provider
        the queue to push the metablocks produced by the insertion
        Args:
            provider -- The provider that will store the data (Provider)
            provider_key -- Key under which the provider is stored in the Dispatcher (str)
            path -- Path under which the file should be stored (str)
            blocks -- The list of blocks that constitutes the file (list)
            indices -- A list of the indinces that should be stored by the provider (list)
            queue --  Queue where the metablocks should be stored once the block are stored (queue.Queue)
        """
        super(BlockPusher, self).__init__()
        self.provider = provider
        self.provider_key = provider_key
        self.path = path
        self.blocks = blocks
        self.indices = indices
        self.queue = queue

    def run(self):
        """
        Loop through self.blocks, selecting those stored at indices
        listed in self.indices and feeding them to self.provider for storage
        """
        index_format_length = len(str(len(self.blocks)))
        loop_temp = "Going to put block {} with key {} in provider {}"
        for index in self.indices:
            block_key = self.path + "-" + str(index).zfill(index_format_length)
            block_data = self.blocks[index]
            logger.debug(loop_temp.format(index, block_key, str(type(self.provider))))
            metablock = MetaBlock(block_key, self.provider_key)
            self.provider.put(block_data, block_key)
            self.queue.put(metablock)

class BlockFetcher(threading.Thread):
    """
    Threaded code to fetch blocks from a storage provider
    """

    def __init__(self, provider, block_keys, queue):
        """
        Initializes the block fetcher
        Args:
            provider -- The provider that will store the data (Provider)
            block_keys -- The list of block keys that constitutes the file (list)
            queue --  Queue where the recoveded data will be pushed  (queue.Queue)
        """
        super(BlockFetcher, self).__init__()
        self.logger = logging.getLogger("BlockFetcher")
        self.provider = provider
        self.block_keys = block_keys
        self.queue = queue

    def run(self):
        """
        Fetches a series of blocks and pushes them the queue
        """
        for key in self.block_keys:
            self.logger.debug("About to fetch block " + key + " from the datastore")
            data = self.provider.get(key)
            self.logger.debug("Storing block " + key + " in synchronization queue")
            self.queue.put((key, data))

def xor(block_a, block_b):
    """
    'Private' function used to xor two blocks.
    """
    # If a is longer than b, pad b
    if len(block_a) > len(block_b):
        for i in range(0, (len(block_a) - len(block_b))):
            block_b = block_b + '\x00'
    elif len(block_a) < len(block_b):
        block_b = block_b[:len(block_a)]
    a = numpy.frombuffer(block_a, dtype='b')
    b = numpy.frombuffer(block_b, dtype='b')
    c = numpy.bitwise_xor(a, b)
    r = c.tostring()
    return r

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

DEFAULT_ENTANGNLEMENT_P = 5

class Dispatcher(object):
    """
    A class that decices where to store data blocks and keeps track of how to
    retrieve them
    """

    def __init__(self, configuration={}):
        self.entanglement = False
        if configuration.has_key("entanglement") and configuration.get("entanglement").has_key("enabled") and configuration.get("entanglement").get("enabled"):
            self.entanglement = True
            self.entanglement_p = int(configuration.get("entanglement").get("p", DEFAULT_ENTANGNLEMENT_P))
            logger.info("entanglement enabled with "  + str(self.entanglement_p) + " blocks")
        self.providers = {}
        providers_configuration = configuration.get('providers', [])
        factory = ProviderFactory()
        for configuration in providers_configuration:
            provider = factory.get_provider(configuration)
            self.providers[str(uuid.uuid4())] = provider
        self.files = {}

    def put(self, path, blocks):
        """
        Distribute blocks among different providers and a data struct
        Args:
            path: Key under which the data is stored
            blocks: A list of byte sequences
        Returns:
            A metadata object describing how the blocks have been stored
        """
        metadata = Metadata(path)
        provider_keys = self.providers.keys()
        blocks_to_store = []
        if self.entanglement:
            blocks, entangling_blocks, blocks_to_store = self.entangle(blocks)
            metadata.entangling_blocks = entangling_blocks
        else:
            blocks_to_store = blocks
        arrangement = arrange_elements(len(blocks_to_store), len(provider_keys))
        metablock_queue = Queue.Queue(len(blocks_to_store))
        block_pushers = []
        for i, provider_key in enumerate(provider_keys):
            provider = self.providers[provider_key]
            block_pusher = BlockPusher(provider, provider_key, path, blocks, arrangement[i], metablock_queue)
            block_pusher.start()
            block_pushers.append(block_pusher)
        for pusher in block_pushers:
            pusher.join()
        while not metablock_queue.empty():
            metadata.blocks.append(metablock_queue.get())
        self.files[path] = metadata
        return metadata

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
        data = {}
        blocks_per_provider = {}
        for metablock in metadata.blocks:
            blocks_to_fetch = blocks_per_provider.get(metablock.provider, [])
            blocks_to_fetch.append(metablock.key)
            blocks_per_provider[metablock.provider] = blocks_to_fetch
        fetchers = []
        block_queue = Queue.Queue()
        for provider_key in blocks_per_provider:
            provider = self.providers[provider_key]
            blocks_to_fetch = blocks_per_provider[provider_key]
            fetcher = BlockFetcher(provider, blocks_to_fetch, block_queue)
            fetcher.start()
            fetchers.append(fetcher)
        for fetcher in fetchers:
            fetcher.join()
        recovered_blocks = []
        while not block_queue.empty():
            recovered_blocks.append(block_queue.get())
        recovered_blocks.sort(key=lambda tup: tup[0])
        data_blocks = [x[1] for x in recovered_blocks]
        if self.entanglement:
            return self.disentangle(data_blocks, metadata.entangling_blocks)
        return data_blocks

    def entangle(self, original_blocks):
        """
        Entangles a list of blocks with a chosen list of blocks
        Args:
            original_blocks -- A list of blocks to entangle
        Returns:
            A tuple with the original blocks, the metadata of the blocks used to
            encode and the list of modified blocks
        """
        if len(original_blocks) == 0:
            return ([], [], [])
        random_blocks = self.get_random_blocks(self.entanglement_p)
        if len(random_blocks) == 0:
            return (original_blocks, [], original_blocks)
        metablocks = [tup[0] for tup in random_blocks]
        datablocks = [tup[1] for tup in random_blocks]
        entangled_blocks = []
        for block in original_blocks:
            for random_block in datablocks:
                entangled_block = xor(block, random_block)
            entangled_blocks.append(entangled_block)
        return (original_blocks, metablocks, entangled_blocks)

    def disentangle(self, entangled_blocks, entangling_metablocks):
        """
        Disentangle a list of blocks
        Args:
            entangled_blocks -- A list of entangled blocks
            entangling_metablocks --  A list of metablocks used to disentangle the
                entangled blocks
        Returns:
            A list of disentangled blocks
        """
        entangling_blocks = []
        for metablock in entangling_metablocks:
            provider = self.providers[metablock.provider]
            entangling_blocks.append(provider.get(metablock.key))
        disentangled_blocks = []
        for entangled_block in entangled_blocks:
            for entangling_block in entangling_blocks:
                entangled_block = xor(entangled_block, entangling_block)
            disentangled_blocks.append(entangled_block)
        return disentangled_blocks

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
        all_metablocks = [block for filename in self.files.keys() for block in self.files.get(filename).blocks]
        number_of_blocks_to_fetch = min(len(all_metablocks), blocks_desired)
        random.shuffle(all_metablocks)
        random_metablocks = all_metablocks[:number_of_blocks_to_fetch]
        fetchers = []
        block_queue = Queue.Queue(number_of_blocks_to_fetch)
        metablocks = {}
        providers_to_use = set([metablock.provider for metablock in random_metablocks])
        for provider_key in providers_to_use:
            blocks_stored_at_provider = [metablock for metablock in random_metablocks if metablock.provider == provider_key]
            provider = self.providers[provider_key]
            block_keys = []
            for metablock in blocks_stored_at_provider:
                block_key = metablock.key
                block_keys.append(block_key)
                metablocks[block_key] = metablock
            fetcher = BlockFetcher(provider, block_keys, block_queue)
            fetcher.start()
            fetchers.append(fetcher)
        for fetcher in fetchers:
            fetcher.join()
        random_blocks = []
        while not block_queue.empty():
            block_key, block_data = block_queue.get()
            metablock = metablocks[block_key]
            random_blocks.append((metablock, block_data))
        return random_blocks
