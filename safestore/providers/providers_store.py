

import logging

from enum import Enum

import safestore.handler.defines as defines

import safestore.providers.dbox as dbox
import safestore.providers.gdrive as gdrive
import safestore.providers.one as one


class Providers(Enum):
    dropbox = 0
    onedrive = 1
    gdrive = 2


class DestBlock():

    def __init__(self, block, path):
        self.block = block
        self.path = path

"""
    Class that holds a provider and a list of DestBlock
"""


class ProviderBlocks():

    def __init__(self, provider, dest_blocks):
        self.provider = provider
        self.dest_blocks = dest_blocks


class ProviderStore():

    def __init__(self):
        self.logger = logging.getLogger()
        filename = "safecloud.log"
        log_format = "[%(filename)s(line %(lineno)s)] - %(message)s"
        logging.basicConfig(format=log_format, filename=filename,
                            filemode="w", level=logging.DEBUG)
        defines.DB_PATH = "data.db"

        self.providers = {Providers.gdrive: gdrive.GDrive(),
                          Providers.onedrive: one.ODrive(),
                          Providers.dropbox: dbox.DBox()}

    def put_blocks(self, list_provider_blocks):

        try:
            for i in range(0, len(list_provider_blocks)):
                provider_blocks = list_provider_blocks[i]
                self.send_all_blocks(provider_blocks)

        except Exception as e:
            self.logger.error("Magic Exception: " + str(e))

    def get_blocks(self, provider, file_names):

        try:
            return map(lambda x: self.get(provider, x), file_names)
        except Exception:
            self.logger.exception("Magic Exception")

    def send_all_blocks(self, provider_blocks):
        provider = self.providers[provider_blocks.provider]
        put = provider.put

        for i in range(0, len(provider_blocks.dest_blocks)):
            block = provider_blocks.dest_blocks[i].block
            path = provider_blocks.dest_blocks[i].path
            put(block, path)

    def put(self, provider, block, path):
        driver = self.providers[provider]
        driver.put(block, path)

    def get(self, provider, file_path):
        """
        Receives a provider  and string with the path of
        the block and returns a future
        """
        driver = self.providers[provider]
        return driver.get(file_path)
