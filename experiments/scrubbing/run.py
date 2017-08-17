#! /usr/bin/env python
"""
A script that inserts a given number of documents in a playcloud instance,
scrubs the redundant replicas once the desired level of protection has been reached
and measures the difference in storage overhead between each requests
"""
import argparse
import datetime
import json
import os
import subprocess

import requests

PATH_TO_DOCKER_COMPOSE_FILE = os.path.join(os.path.dirname(__file__),
                                           "../../",
                                           "docker-compose.yml")

def put(host="127.0.0.1", port=3000, payload_size_in_bytes=1024):
    """
    Uploads a file to playcloud
    Args:
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

def scrub(pointers=10):
    """
    Scrubs the playcloud instance to remove replicas of blocks that well protected
    enough
    Args:
        pointers(int, optional): The number of documents pointing to a block
                                 that makes it a candidate for its replicas to
                                 be deleted
    Returns:
        int: Return code of the command
    """
    command = "docker-compose --file {:s} exec proxy ./scrub.py --pointers {:d}".format(PATH_TO_DOCKER_COMPOSE_FILE, pointers)
    with open(os.devnull, "wb") as dev_null:
        return subprocess.call(command.split(), stdout=dev_null, stderr=dev_null)

def get_number_of_replicas(host="127.0.0.1", port=3000):
    """
    Counts the number of blocks and replicas in the system
    Args:
        host(str, optional):
        port(int, optional):
        payload_size_in_bytes(optional):
    Returns:
    """
    url = "http://{:s}:{:d}/".format(host.strip(), port)
    files = json.loads(requests.get(url).text)["files"]
    counter = 0
    for file_metadata in files:
        for block in file_metadata["blocks"]:
            counter += len(block["providers"])
    return counter

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(__file__,
                                     description="Runs an experiment to measure the variation in storage overhead of a scrubbed playcloud instance running STeP")
    PARSER.add_argument("--host", type=str, default="127.0.0.1",
                        help="Host of the playcloud server")
    PARSER.add_argument("--port", type=int, default=3000,
                        help="Port number of the playcloud proxy")
    PARSER.add_argument("--documents", type=int, default=1000,
                        help="The number of documents to insert in the playcloud instance")
    PARSER.add_argument("--payload-size", type=int, default=1024,
                        help="Size of the payloads in bytes")
    PARSER.add_argument("--pointers", type=int, default=3,
                        help="The minimum number of documents pointing to a block to declare it \"scrubbable\"")
    ARGS = PARSER.parse_args()
    DOCUMENT_COUNT = 0
    for _ in xrange(ARGS.documents):
        put(host=ARGS.host,
            port=ARGS.port,
            payload_size_in_bytes=ARGS.payload_size)
        DOCUMENT_COUNT += 1
        assert scrub(pointers=ARGS.pointers) == 0
        BLOCK_COUNT = get_number_of_replicas()
        print "{:d},{:d}".format(DOCUMENT_COUNT, BLOCK_COUNT)
