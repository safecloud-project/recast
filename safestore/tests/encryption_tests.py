from safestore.encryption.xor_driver import XorDriver
from safestore.encryption.hashed_xor_driver import HashedXorDriver, Hash, IntegrityException
from safestore.encryption.signed_xor_driver import SignedXorDriver
from safestore.encryption.signed_hashed_xor_driver import SignedHashedXorDriver
from safestore.encryption.aes_driver import AESDriver
from safestore.encryption.shamir_driver import ShamirDriver

import ConfigParser

import unittest

from random import randint

from faker import Faker

"""
    REMINDER FOR PAPER:
    We can see the guarantees as a lattice.
    In the lowest case we have privacy.
    At the second level, we have privacy and integraty or privacy
    and non-repudiation.
    At the highest level we have all three.
"""
config = ConfigParser.ConfigParser()
config.read('../configuration/ACCOUNTS.INI')
n_tests = config.getint('MAIN', 'NTESTS')

fake = Faker()


def get_random_number_of_blocks():
    return randint(2, 10)


def random_message():
    return str(fake.text())


class TestXorDriver(unittest.TestCase):

    def setUp(self):
        self.message = random_message()
        self.n_blocks = get_random_number_of_blocks()
        self.driver = XorDriver(self.n_blocks)

    def test_encode(self):
        size = len(self.driver.encode(self.message))
        self.assertEqual(size, self.n_blocks)

    def test_encode_decode(self):

        encoded = self.driver.encode(self.message)
        decoded = self.driver.decode(encoded)
        self.assertEqual(self.message, decoded)


class TestHashedXorDriver(TestXorDriver):

    def setUp(self):
        self.message = random_message()
        self.n_blocks = get_random_number_of_blocks()
        # Just testing sha1
        self.driver = HashedXorDriver(self.n_blocks, Hash.sha1)

    def test_integrity(self):
        encoded = self.driver.encode(self.message)

        invalid_encoded = map(lambda (a, b): ("", b), encoded)

        with self.assertRaises(IntegrityException):
            self.driver.decode(invalid_encoded)


class TestSignedXorDriver(TestXorDriver):

    def setUp(self):
        self.message = random_message()
        self.n_blocks = get_random_number_of_blocks()
        self.driver = SignedXorDriver(self.n_blocks)


class TestSignedHashedXorDriver(TestXorDriver):

    def setUp(self):
        self.message = random_message()
        self.n_blocks = get_random_number_of_blocks()
        self.driver = SignedHashedXorDriver(self.n_blocks, Hash.sha1)


class TestAESDriver(unittest.TestCase):

    def setUp(self):
        self.message = random_message()
        self.driver = AESDriver()

    def test_encode_decode(self):

        encoded = self.driver.encode(self.message)
        decoded = self.driver.decode(encoded)
        self.assertEqual(self.message, decoded)

class TestShamirDriver(unittest.TestCase):

    def setUp(self):
        self.message = random_message()
        self.driver = ShamirDriver(5, 2)

    def test_encode_decode(self):

        encoded = self.driver.encode(self.message)
        decoded = self.driver.decode(encoded)
        self.assertEqual(self.message, decoded)



def suite_xor_driver():
    tests = ['test_encode', 'test_encode_decode']
    return unittest.TestSuite(map(TestXorDriver, tests))


def suite_hashed_xor_driver():
    tests = ['test_encode', 'test_encode_decode', 'test_integrity']
    return unittest.TestSuite(map(TestHashedXorDriver, tests))

def suite_signed_xor_driver():
    tests = ['test_encode', 'test_encode_decode']
    return unittest.TestSuite(map(TestSignedXorDriver, tests))

def suite_signed_hashed_xor_driver():
    tests = ['test_encode', 'test_encode_decode']
    return unittest.TestSuite(map(TestSignedHashedXorDriver, tests))

def suite_aes_driver():
    tests = ['test_encode_decode']
    return unittest.TestSuite(map(TestAESDriver, tests))

def suite_shamir_driver():
    tests = ['test_encode_decode']
    return unittest.TestSuite(map(TestShamirDriver, tests))


if __name__ == '__main__':
    for i in range(0, n_tests):
        suite1 = suite_xor_driver()
        suite2 = suite_hashed_xor_driver()
        suite3 = suite_signed_xor_driver()
        suite4 = suite_signed_hashed_xor_driver()
        suite5 = suite_aes_driver()
        suite6 = suite_shamir_driver()

        all_tests = unittest.TestSuite([suite1, suite2, suite3, suite4, suite5, suite6])
        unittest.TextTestRunner(verbosity=0).run(all_tests)
