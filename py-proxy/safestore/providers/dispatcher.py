"""
A component that distributes blocks for storage keeps track of their location
"""
import datetime
import logging
import logging.config
import os
import uuid

import numpy

from enum import Enum
from dbox import DBox
from gdrive import GDrive
from redis_provider import RedisProvider

logger = logging.getLogger("dispatcher")


class Providers(Enum):
    """
    Enumeration of all the storage providers supported by the Dispatcher
    """
    redis = 0
    gdrive = 1
    dropbox = 2

class ProviderFactory(object):
    """
    Creates storage providers based on configuration
    """
    def __init__(self):
        self.initializers = {
            Providers.dropbox.name: DBox,
            Providers.gdrive.name: GDrive,
            Providers.redis.name: RedisProvider
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
        return initializer(configuration)

class Metadata(object):
    """
    A class describing how a file has been stored in the system
    """

    def __init__(self, path):
        self.path = path
        self.creation_date = datetime.datetime.now()
        self.blocks = {}
        self.entangled_blocks = {}

def xor(block_a, block_b):
    """
    'Private' function used to xor two blocks.
    """
    a = numpy.frombuffer(block_a, dtype='b')
    b = numpy.frombuffer(block_b, dtype='b')
    c = numpy.bitwise_xor(a, b)
    r = c.tostring()
    return r

class Dispatcher(object):
    """
    A class that decices where to store data blocks and keeps track of how to
    retrieve them
    """

    def __init__(self, providers_configuration=[]):
        self.providers = {}
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
        self.files[path] = metadata
        provider_keys = self.providers.keys()
        number_of_providers = len(provider_keys)
        loop_temp = "Going to put block {} with key {} in provider {}"
        index_format_length = len(str(len(blocks)))
        for i, block in enumerate(blocks):
            key = path + "-" + str(i).zfill(index_format_length)
            provider_key = provider_keys[i % number_of_providers]
            provider = self.providers[provider_key]

            logger.debug(loop_temp.format(i, key, provider_key))

            provider.put(block, key)
            stored_blocks = metadata.blocks.get(provider_key, [])
            stored_blocks.append(key)
            metadata.blocks[provider_key] = stored_blocks
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
        provider_keys = [k for k in metadata.blocks.keys()
                          if len(metadata.blocks[k]) > 0]
        data = {}
        for provider_key in provider_keys:
            provider = self.providers[provider_key]
            block_keys = metadata.blocks[provider_key]
            for block_key in block_keys:
                data[block_key] = provider.get(block_key)
        return [data[key] for key in sorted(data.keys())]

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
        block_length = len(original_blocks[0])
        random_block = os.urandom(block_length)
        entangled_blocks = []
        for block in original_blocks:
            entangled_blocks.append(xor(block, random_block))
        return (original_blocks, [], entangled_blocks)
