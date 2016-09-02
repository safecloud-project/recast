#! /usr/bin/env python
"""
A script that tests the sequential insertion of files in playcloud through the
http interface and the fuse mount
"""
import math
import os
import sys
import time
import uuid

import requests

# File sizes that range from 1KB to 8MB progressing as powers of 2
SIZES = [int(math.pow(2, i)) for i in range(10, 24, 1)]

def write_file(size, mountpoint):
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
    print "fuse, ", str(size) + ", " + str(elapsed) + ", " + str(throughput)
    return elapsed, throughput

def upload_file(size, server):
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
    print "http, ", str(size) + ", " + str(elapsed) + ", " + str(throughput)
    return elapsed, throughput


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: " + sys.argv[0] + " <mountpoint> <playcloud server>"
        sys.exit(0)
    REPETITIONS = 15
    MOUNTPOINT = sys.argv[1]
    ADDRESS = sys.argv[2]
    print "#transport, size, response time (s), throughput (B/s)"
    for size in SIZES:
        for i in range(REPETITIONS):
            write_file(size, MOUNTPOINT)
    for size in SIZES:
        for i in range(REPETITIONS):
            upload_file(size, ADDRESS)
