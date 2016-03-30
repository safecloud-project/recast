
from coding_servicer import DriverFactory

import ConfigParser

import os
import unittest

from faker import Faker

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'pycoder.cfg'))
n_tests = config.getint('main', 'ntests')

fake = Faker()


def random_message():
    return str(fake.text())


class TestDriverFactory(unittest.TestCase):

    def __init__(self, testname, config_file):
        super(TestDriverFactory, self).__init__(testname)
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        self.message = random_message()
        self.factory = DriverFactory(config)
        self.driver = self.factory.get_driver()

    def test_encode_decode(self):

        encoded = self.driver.encode(self.message)
        decoded = self.driver.decode(encoded)
        self.assertEqual(self.message, decoded)


def suite_driver_factory():
    tests = ['test_encode_decode']
    test_files = os.path.join(os.path.dirname(__file__), "test_files/")
    config_files = ['xor_driver.cfg',
                    'hashed_xor_driver.cfg',
                    'signed_hashed_xor_driver.cfg',
                    'signed_xor_driver.cfg',
                    'erasure_driver.cfg',
                    'aes_driver.cfg',
                    'shamir.cfg']

    suite = unittest.TestSuite()

    for file in config_files:
        for test in tests:
            suite.addTest(TestDriverFactory(test, os.path.join(test_files, file)))

    return suite


if __name__ == '__main__':
    for i in range(0, n_tests):

        suite = suite_driver_factory()
        all_tests = unittest.TestSuite([suite])
        unittest.TextTestRunner(verbosity=2).run(all_tests)
