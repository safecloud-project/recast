#! /usr/bin/env python
"""
A script that benchmarks pyeclib libraries reconstruction capabilities by
reconstructing 100 times from 0 to (N - K + 1) missing blocks from a given
number of misisng size.
"""
import random
import os
import sys
import time

from pyeclib.ec_iface import ECDriver

REQUESTS = 100

def print_usage():
    """Prints the usage message"""
    print "Usage:", sys.argv[0], " size"
    print ""
    print "A script that benchmarks pyeclib libraries reconstruction capabilities"
    print ""
    print "Arguments:"
    print "\tsize                        Size of the payload to encode in bytes"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(0)
    SIZE = int(sys.argv[1])
    EC_K = int(os.environ.get("EC_K", 10))
    EC_M = int(os.environ.get("EC_M", 4))
    EC_TYPE = os.environ.get("EC_TYPE", "liberasurecode_rs_vand")

    DRIVER = ECDriver(k=EC_K, m=EC_M, ec_type=EC_TYPE)

    DATA = os.urandom(SIZE)
    STRIPS = DRIVER.encode(DATA)
    LENGTH = EC_K + EC_M
    SUPPORTED_DISTANCE = LENGTH - EC_K + 1
    print "About to reconstruct ", REQUESTS, " times a payload of size ", SIZE, " bytes (", \
    (DRIVER.ec_type if hasattr(DRIVER, "ec_type") else EC_TYPE), ", k =", DRIVER.k, \
    ", m =", DRIVER.m, ") from 0 to", SUPPORTED_DISTANCE, "missing blocks"

    random.seed(0)

    for missing_blocks in range(SUPPORTED_DISTANCE):
        for i in range(REQUESTS):
            missing_indices = range(missing_blocks)
            start = time.clock()
            DRIVER.reconstruct(STRIPS[missing_blocks:], missing_indices)
            end = time.clock()
            elapsed_in_milliseconds = (end - start) * 1000
            print elapsed_in_milliseconds
