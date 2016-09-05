#! /usr/bin/env python
"""
A script that tests the sequential insertion of files in playcloud through the
http interface and the fuse mount
"""
import argparse
import logging
import math
import os
import sys
import time
import uuid

import numpy
import requests

# Prepare logger
LOGGER = logging.getLogger(__name__)
CONSOLE = logging.StreamHandler()
FORMATTER = logging.Formatter("%(asctime) - %(levelname) : %(message)")
CONSOLE.setFormatter(FORMATTER)
LOGGER.addHandler(CONSOLE)
LOGGER.setLevel(logging.INFO)


# File sizes that range from 1KB to 8MB progressing as powers of 2
SIZES = [int(math.pow(2, i)) for i in range(10, 24, 1)]

def write_file(size, mountpoint):
    """
    Writes a file of a given size to a given mount point.
    Args:
        size(int): Size of the input to generate
        mountpoint(str): Mount point used by the fuse client
    Returns:
        (float, float): A tuple with the response time (in secs) and the throughput (in B/sec)
    """
    data = os.urandom(size)
    filename = str(uuid.uuid4())
    filepath = os.path.join(mountpoint, filename)
    start = time.time()
    with open(filepath, "w") as file_handler:
        file_handler.write(data)
        file_handler.flush()
    end = time.time()
    elapsed = end - start
    throughput = size / elapsed
    LOGGER.debug("fuse, " + str(size) + ", " + str(elapsed) + ", " + str(throughput))
    return elapsed, throughput

def upload_file(size, server):
    """
    Uploads a file to a given instance of a playcloud server.
    Args:
        size(int): Size of the input to generate
        server(str): path of the server to contact
    Returns:
        (float, float): A tuple with the response time (in secs) and the throughput (in B/sec)
    """
    data = os.urandom(size)
    filename = str(uuid.uuid4())
    url = server + "/" + filename
    start = time.time()
    response = requests.put(url, data=data)
    end = time.time()
    assert response.text == filename
    assert response.status_code == 200
    elapsed = end - start
    throughput = size / elapsed
    LOGGER.debug("http, " + str(size) + ", " + str(elapsed) + ", " + str(throughput))
    return elapsed, throughput

TRANSPORT_HANDLERS = {
    "fuse": write_file,
    "http": upload_file
}

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        prog="benchmark.py",
        description="""
        A script that tests the sequential insertion of files in playcloud through the http interface and the fuse mount
        """
    )
    PARSER.add_argument("path", nargs=1, type=str,
                        help="The URL or directory path to use for the benchmark")
    PARSER.add_argument("-t", "--transport", nargs=1, type=str,
                        help="The transport to use for the tests http or fuse", required=True)
    PARSER.add_argument("-r", "--repetitions", nargs="?", type=int, default=10,
                        help="The number of requests to run for each of the input sizes")
    ARGS = PARSER.parse_args()
    # Check transport and transport handler
    TRANSPORT = ARGS.transport[0]
    if TRANSPORT not in TRANSPORT_HANDLERS.keys():
        PARSER.print_help()
        sys.exit(1)
    HANDLER = TRANSPORT_HANDLERS[TRANSPORT]
    # Set the path
    PATH = ARGS.path[0]
    # Set repetitions
    REPETITIONS = ARGS.repetitions
    # Run the benchmark
    for data_size in SIZES:
        records = []
        for i in range(REPETITIONS):
            records.append(HANDLER(data_size, PATH))
        mean_throughput = numpy.mean([r[1] for r in records])
        std_throughput = numpy.std([r[1] for r in records])
        print TRANSPORT + ", " + str(data_size) + ", " + str(mean_throughput) + ", " +\
                str(std_throughput)
