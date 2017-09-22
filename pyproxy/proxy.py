"""
A python implementation of playcloud's proxy server
"""
import argparse
import json
import logging
import logging.config
import os
import time
import uuid

from bottle import abort, request, response, run
import bottle
import concurrent.futures
import grpc
from kazoo.client import KazooClient
from kazoo.handlers.threading import KazooTimeoutError

import pyproxy.playcloud_pb2 as playcloud_pb2
import pyproxy.playcloud_pb2_grpc as playcloud_pb2_grpc

from pyproxy.coder_client import CoderClient
from pyproxy.files import extract_entanglement_data, Files
from pyproxy.pyproxy_globals import get_dispatcher_instance
from pyproxy.playcloud_pb2 import DecodeRequest, EncodeRequest, Strip
from pyproxy.proxy_service import ProxyService


log_config = os.getenv("LOG_CONFIG", "/usr/local/src/pyproxy/logging.conf")
logging.config.fileConfig(log_config)

LOGGER = logging.getLogger("proxy")


# GRPC setup
DEFAULT_GRPC_TIMEOUT_IN_SECONDS = 60
GRPC_MESSAGE_SIZE = (2 * 1024 * 1024 * 1024) - 1 # 2^31 - 1
GRPC_OPTIONS = [
    ("grpc.max_receive_message_length", GRPC_MESSAGE_SIZE),
    ("grpc.max_send_message_length", GRPC_MESSAGE_SIZE)
]
CODER_CLIENT = CoderClient()

# Loading dispatcher
DISPATCHER = get_dispatcher_instance()

# Loading the Files metadata structure
FILES = Files()

# Bottle webapp configuration
bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 * 1024
APP = bottle.app()

# Setup kazoo
KAZOO = None
HOSTNAME = os.uname()[1]

# Inizialize the dictionary for keeping track of blocks used in encoding
HEADER_DICTIONARY = {}

@APP.route("/<key:path>/__meta", method="GET")
def get_file_metadata(key):
    """
    Returns Metadata about a file stored in the system.
    Args:
        key(string): Key under which the data is supposed to be stored
    Returns:
        (string): A listing of the files serialized as JSON
    """
    try:
        meta = FILES.get(key)
    except KeyError as e:
        LOGGER.warn(e)
        response.status = 404
        return ""
    return json.dumps(meta.__json__())

@APP.route("/<key:path>", method="GET")
def get(key):
    """
    Handles GET requests to retrieve data stored under <key> from playcloud

    key -- Key under which the data should have been stored
    """
    LOGGER.debug("Received get request for key {:s}".format(key))
    key = unicode(key, errors="ignore").encode("utf-8")
    lock = KAZOO.ReadLock(os.path.join("/", key), HOSTNAME)
    with lock:
        blocks = DISPATCHER.get(key)
        if blocks is None:
            response.status = 404
            return ""
        strips = []
        for block in blocks:
            strip = Strip()
            strip.data = block
            strips.append(strip)

        LOGGER.debug("Received blocks from redis")

        LOGGER.debug("Going go to do decode request")

        data = CODER_CLIENT.decode(key, strips)
        return data

def store(key=None, data=None):
    """
    Store data into playcloud

    key -- Key under which the data should be stored (default None)
    """
    if key is None:
        key = str(uuid.uuid4())
    key = unicode(key, errors="ignore").encode("utf-8")
    lock = KAZOO.WriteLock(os.path.join("/", key), HOSTNAME)
    with lock:
        LOGGER.debug("Going to request data encoding")
        encoded_file = CODER_CLIENT.encode(key, data)

        number_of_blocks = len(encoded_file.strips)
        LOGGER.debug("Received {:2d} encoded blocks from data encoding".format(number_of_blocks))
        LOGGER.debug("Going to store {:2d} blocks with key {:s}".format(number_of_blocks, key))
        metadata = DISPATCHER.put(key, encoded_file)
        LOGGER.debug("Stored {:2d} blocks with key {:s}".format(number_of_blocks, key))

        creation_date = str(metadata.creation_date)
        metadata.entangling_blocks = extract_entanglement_data(encoded_file.strips[0].data)
        formatted_entangling_blocks = json.dumps(metadata.entangling_blocks)
        keys_and_providers = str([[b.key, b.providers[0]] for b in metadata.blocks])
        HEADER_DICTIONARY[key] = [creation_date, formatted_entangling_blocks, keys_and_providers]

        FILES.put(key, metadata)

        return key


@APP.route("/<key:path>", method="PUT")
def put(key):
    """
    Handles PUT requests to store data into playcloud
    """
    LOGGER.debug("Received put request for key {:s}".format(key))
    # Check if the PUT request actually carries any data in its body to avoid
    # storing empty blocks under a key.
    data = request.body.getvalue()
    if not data:
        return abort(400, "The request body must contain data to store")
    return store(key=key, data=request.body.getvalue())


@APP.route("/", method="PUT")
def put_keyless():
    """
    Handle PUT requests for key-less database insertions
    """
    # Check if the PUT request actually carries any data in its body to avoid
    # storing empty blocks under a key.
    data = request.body.getvalue()
    if not data:
        return abort(400, "The request body must contain data to store")
    return store(key=None, data=request.body.getvalue())

@APP.route("/", method="GET")
def list_files():
    """
    List the files stored in the system.
    Returns:
        (string): A listing of the files serialized as JSON
    """
    entries = [meta.__json__() for meta in FILES.values()]
    return json.dumps({"files": entries})

@APP.route("/dict", method="GET")
def dictionary():
    """
    Show the dictionary used by the proxy to the trace blocks used in encoding.
    """
    return json.dumps(FILES.get_entanglement_graph(), indent=4, separators=(',', ': '))

def init_zookeeper_client(host="zoo1", port=2181, max_retries=5):
    """
    Tries to initialize the connection to zookeeper.
    Args:
        host(str, optional): zookeeper host
        port(int, optional): zookeeper port
        max_retries(int, optional): How many times should the connection
                                    establishment be retried
    Returns:
        kazoo.client.KazooClient: An initialized zookeeper client
    Raises:
        EnvironmentError: If the client cannot connect to zookeeper
    """
    zk_logger = logging.getLogger("zookeeper")
    zk_logger.info("initializing connection to zookeeper")
    hosts = "{:s}:{:d}".format(host, port)
    client = KazooClient(hosts=hosts)
    backoff_in_seconds = 1
    tries = 0
    while tries < max_retries:
        try:
            zk_logger.info("Trying to connect to {:s}".format(hosts))
            client.start()
            if client.connected:
                zk_logger.info("Connected to zookeeper")
                return client
        except KazooTimeoutError:
            tries += 1
            backoff_in_seconds *= 2
            zk_logger.warn("Failed to connect to {:s}".format(hosts))
            zk_logger.warn("Waiting {:d} seconds to reconnect to {:s}"
                           .format(backoff_in_seconds, hosts))
            time.sleep(backoff_in_seconds)
    zk_logger.error("Could not connect to {:s}".format(hosts))
    raise EnvironmentError("Could not connect to {:s}".format(hosts))

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(prog="proxy",
                                     description="A python implementation of playcloud's proxy server")
    PARSER.add_argument("--debug", action="store_true", help="Show debug logs")
    ARGS = PARSER.parse_args()
    if ARGS.debug or os.environ.has_key("DEBUG") or os.environ.has_key("debug"):
        LOGGER.setLevel(logging.DEBUG)
        logging.getLogger("dispatcher").setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.INFO)
        logging.getLogger("dispatcher").setLevel(logging.INFO)
    GRPC_SERVER = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10),
                              options=GRPC_OPTIONS)
    playcloud_pb2.add_ProxyServicer_to_server(ProxyService(), GRPC_SERVER)
    GRPC_SERVER.add_insecure_port("0.0.0.0:1234")
    GRPC_SERVER.start()
    KAZOO = init_zookeeper_client()
    run(server="paste", app=APP, host="0.0.0.0", port=8000)
    KAZOO.stop()
