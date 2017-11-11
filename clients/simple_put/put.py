#! /usr/bin/env python
import argparse
import datetime
from functools import partial
import json
from multiprocessing import Pool
import os

import requests


def put(ignored, host="127.0.0.1", port=3000, payload_size_in_bytes=1024):
    """
    Uploads a file to playcloud
    Args:
        ignored(object):
        host(str, optional):
        port(int, optional):
        payload_size_in_bytes(optional):
    Returns:
        dict: A dictionary with the response data
    """
    payload = os.urandom(payload_size_in_bytes)
    url = "http://{:s}:{:d}".format(host.strip(), port)
    start_time = datetime.datetime.now()
    response = requests.put(url, data=payload)
    return  {
        "id": response.text,
        "start_time": start_time.isoformat(),
        "status": response.status_code,
        "response_time": response.elapsed.total_seconds()
    }


if __name__ == "__main__":
    PROGRAM_DESCRIPTION = "A script that uploads random files to a playcloud instance"
    PARSER = argparse.ArgumentParser("put.py", description=PROGRAM_DESCRIPTION)
    PARSER.add_argument("-s", "--host",
                        help="Server hosting the playcloud proxy", default="127.0.0.1")
    PARSER.add_argument("-p", "--port", type=int, default=3000,
                        help="Port number the playcloud instance is listening on")
    PARSER.add_argument("-r", "--requests", type=int, default=1000,
                        help="The total number of requests")
    PARSER.add_argument("-c", "--concurrency", type=int, default=4,
                        help="The number of concurrent requests to playcloud")
    PARSER.add_argument("-b", "--payload-size", type=int, default=1024,
                        help="Size of the payloads in bytes")
    ARGS = PARSER.parse_args()
    CONFIGURED_PUT = partial(put, host=ARGS.host, port=ARGS.port, payload_size_in_bytes=ARGS.payload_size)
    POOL = Pool(ARGS.concurrency)
    IGNORED_ARGUMENTS = [None for _ in xrange(ARGS.requests)]
    RESULTS = POOL.map(CONFIGURED_PUT, IGNORED_ARGUMENTS)
    print json.dumps(RESULTS)
