#! /usr/bin/env python

import os
import sys
import time

from ConfigParser import ConfigParser
from pyeclib.ec_iface import ECDriver

def print_usage():
    print "Usage:", sys.argv[0], " size"
    print ""
    print "Benchmark pyeclib erasure coding libraries"
    print ""
    print "Arguments:"
    print "\tsize       Size of the payload to encode in bytes"

def gen_random_data(size):
    return os.urandom(size)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(0)
    size = int(sys.argv[1])
    data = gen_random_data(size)
    config = ConfigParser()
    requests = 1000

    # Load driver
    config.read("pycoder.cfg")
    ec_k = int(os.environ.get("EC_K", config.get("ec", "k")))
    ec_m = int(os.environ.get("EC_M", config.get("ec", "m")))
    ec_type = os.environ.get("EC_TYPE", config.get("ec", "type"))
    driver = ECDriver(k=ec_k, m=ec_m, ec_type=ec_type)

    # Start benchmark
    print "About to encode ", requests, " payloads of size ", size, " bytes (", ec_type, ", k =",ec_k, ", m =", ec_m, ")"
    for i in range(requests):
        start = time.clock()
        driver.encode(data)
        end = time.clock()
        elasped = (end - start) * 1000
        print elasped
