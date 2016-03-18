from safestore.encryption.xor_driver import XorDriver
from safestore.encryption.signed_xor_driver import SignedXorDriver
from safestore.providers.providers_store import ProviderStore
from safestore.providers.providers_store import Providers
from safestore.providers.providers_store import ProviderBlocks
from safestore.providers.providers_store import DestBlock
import math
import ConfigParser

import unittest

from random import randint

from faker import Faker

config = ConfigParser.ConfigParser()
config.read('../configuration/ACCOUNTS.INI')
n_tests = config.getint('MAIN', 'NTESTS')

fake = Faker()


def get_random_number_of_blocks():
    return randint(2, 10)


def random_message():
    return str(fake.text())


class TestXorDriverProvider(unittest.TestCase):

    def setUp(self):
        self.message = random_message()
        self.n_blocks = 3
        self.driver = XorDriver(self.n_blocks)
        self.provider_store = ProviderStore()

    def test_different_providers(self):
        blocks = self.driver.encode(self.message)
        self.provider_store.put(Providers.dropbox, blocks[0],
                                "block1.txt")
        self.provider_store.put(Providers.onedrive, blocks[1],
                                "block2.txt")
        self.provider_store.put(Providers.gdrive, blocks[2],
                                "block3.txt")

        firstBlock = self.provider_store.get(Providers.dropbox,
                                             "block1.txt")
        secondBlock = self.provider_store.get(Providers.onedrive,
                                              "block2.txt")
        thirdBlock = self.provider_store.get(Providers.gdrive,
                                             "block3.txt")
        get_blocks = [firstBlock, secondBlock, thirdBlock]

        decoded_message = self.driver.decode(get_blocks)
        self.assertEqual(self.message, decoded_message)

    def test_multiple_blocks_to_dropbox(self):
        blocks = self.driver.encode(self.message)
        path = "block"
        destBlocks = []
        paths = []
        for i in range(0, len(blocks)):
            pathi = path + str(i) + ".txt"
            paths.append(pathi)
            destBlock = DestBlock(blocks[i], pathi)
            destBlocks.append(destBlock)

        pBlocks = ProviderBlocks(Providers.dropbox, destBlocks)

        self.provider_store.send_all_blocks(pBlocks)

        received_blocks = self.provider_store.get_blocks(
            Providers.dropbox, paths)
        decoded_message = self.driver.decode(received_blocks)
        self.assertEqual(self.message, decoded_message)


class TestMultipleBlocksMultipleProviders(unittest.TestCase):

    def setUp(self):
        self.message = random_message()
        self.n_blocks = get_random_number_of_blocks()
        self.driver = SignedXorDriver(self.n_blocks)
        self.provider_store = ProviderStore()

    def test_send_receive(self):

        blocks = self.driver.encode(self.message)

        dropbox_blocks = []
        gdrive_blocks = []
        onedrive_blocks = []
        path = "block"

        for i in range(0, int(math.floor(len(blocks) / 2))):
            pathi = path + str(i) + ".txt"
            dest_block = DestBlock(blocks[i], pathi)
            if i % 2 == 0:
                dropbox_blocks.append(dest_block)
            else:
                gdrive_blocks.append(dest_block)

        for i in range(int(math.floor(len(blocks) / 2)), len(blocks)):
            pathi = path + str(i) + ".txt"
            dest_block = DestBlock(blocks[i], pathi)
            onedrive_blocks.append(dest_block)

        send_to_dropbox = ProviderBlocks(Providers.dropbox,
                                         dropbox_blocks)

        send_to_gdrive = ProviderBlocks(Providers.gdrive,
                                        gdrive_blocks)

        send_to_onedrive = ProviderBlocks(Providers.onedrive,
                                          onedrive_blocks)
        to_send = [send_to_dropbox, send_to_gdrive, send_to_onedrive]

        self.provider_store.put_blocks(to_send)

        def get_files(provider, dest_blocks):
            files = []
            for i in dest_blocks:
                files.append(i.path)
            print(files)
            return self.provider_store.get_blocks(provider, files)

        dropbox_files = get_files(Providers.dropbox, dropbox_blocks)
        gdrive_files = get_files(Providers.gdrive, gdrive_blocks)
        onedrive_files = get_files(Providers.onedrive, onedrive_blocks)
        received_blocks = dropbox_files + gdrive_files + onedrive_files

        self.assertEqual(len(blocks), len(received_blocks))
        decoded_message = self.driver.decode(received_blocks)
        self.assertEqual(self.message, decoded_message)


def suite_xor_driver_provider():
    #tests = ['test_different_providers']
    tests = ['test_multiple_blocks_to_dropbox']
    return unittest.TestSuite(map(TestXorDriverProvider, tests))


def suite_multiple_blocks_multiple_providers():
    #tests = ['test_different_providers']
    tests = ['test_send_receive']
    return unittest.TestSuite(map(TestMultipleBlocksMultipleProviders, tests))


if __name__ == '__main__':
    for i in range(0, n_tests):
        suite1 = suite_xor_driver_provider()
        suite2 = suite_multiple_blocks_multiple_providers()

        all_tests = unittest.TestSuite([suite2])
        unittest.TextTestRunner(verbosity=0).run(all_tests)
