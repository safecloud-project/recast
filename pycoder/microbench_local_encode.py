#! /usr/bin/env python
""" A script that encodes 1000 times a piece of data """
import os
import sys
import time

from coding_servicer import DriverFactory
from ConfigParser import ConfigParser


def print_usage():
    """Prints the usage message"""
    print "Microbenchmark for multiple encoding libraries\n"
    print "Arguments:"
    print "\tsize       Size of the payload to encode in bytes\n"
    print "\trequests   Number of requests executed\n"
    print "\tconfig     Configuration file with the driver properties"


def print_selected_configuration(config):
    selected_driver = config.get("main", "driver")
    print "Configuration file had driver {}".format(selected_driver)
    parameters = dict(config.items(selected_driver))
    print "Parameters are {}".format(parameters)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print_usage()
        sys.exit(0)
    SIZE = int(sys.argv[1])
    DATA = os.urandom(SIZE)
    REQUESTS = int(sys.argv[2])
    CONF_FILE = sys.argv[3]
    req = "Received bench request with Size {}, Requests {}, Conf {}"
    print req.format(SIZE, REQUESTS, CONF_FILE)
    CONFIG = ConfigParser()
    CONFIG.read(CONF_FILE)
    print_selected_configuration()
    factory = DriverFactory(CONFIG)
    DRIVER = factory.get_driver()

    for i in range(REQUESTS):
        start = time.clock()
        DRIVER.encode(DATA)
        end = time.clock()
        elasped = (end - start) * 1000
        print elasped
