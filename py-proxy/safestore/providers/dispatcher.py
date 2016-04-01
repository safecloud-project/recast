import datetime

import logging
import logging.config

from enum import Enum
from dbox import DBox
from gdrive import GDrive
from redis_provider import RedisProvider

logger = logging.getLogger("dispatcher")


class Providers(Enum):
    redis = 0
    gdrive = 1
    dropbox = 2


class Metadata(object):
    """
    A class describing how a file has been stored in the system
    """

    def __init__(self, path):
        self.path = path
        self.creation_date = datetime.datetime.now()
        self.blocks = {}
        for provider in Providers:
            self.blocks[provider] = []


class Dispatcher(object):
    """
    A class that decices where to store data blocks and keeps track of how to
    retrieve them
    """

    def __init__(self):
        self.providers = {
            # Providers.dropbox: DBox(),
            # Providers.gdrive: GDrive(),
            Providers.redis: RedisProvider()
        }
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
        for i, block in enumerate(blocks):
            key = path + "-" + str(i).zfill(len(str(len(blocks))))
            provider_key = provider_keys[i % number_of_providers]
            provider = self.providers[provider_key]

            logger.debug(loop_temp.format(i, key, provider_key))

            provider.put(block, key)
            metadata.blocks[provider_key].append(key)
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
        provider_names = [k for k in metadata.blocks.keys()
                          if len(metadata.blocks[k]) > 0]
        data = {}
        for name in provider_names:
            provider = self.providers[name]
            block_keys = metadata.blocks[name]
            for block_key in block_keys:
                data[block_key] = provider.get(block_key)
        return [data[key] for key in sorted(data.keys())]
