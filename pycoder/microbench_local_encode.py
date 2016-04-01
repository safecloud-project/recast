#! /usr/bin/env python
""" A script that encodes 1000 times a piece of data """
import os
import sys
import time

from coding_servicer import DriverFactory
from ConfigParser import ConfigParser


def print_usage():
    """Prints the usage message"""
    print "Usage:", sys.argv[0], " size"
    print ""
    print "Benchmark pyeclib erasure coding libraries"
    print ""
    print "Arguments:"
    print "\tsize       Size of the payload to encode in bytes"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(0)
    SIZE = int(sys.argv[1])
    DATA = os.urandom(SIZE)
    REQUESTS = 1000

    CONFIG = ConfigParser()
    CONFIG.read(os.path.join(os.path.dirname(__file__), "pycoder.cfg"))

    factory = DriverFactory(CONFIG)

    DRIVER = factory.get_driver()

    for i in range(REQUESTS):
        start = time.clock()
        DRIVER.encode(DATA)
        end = time.clock()
        elasped = (end - start) * 1000
        print elasped
