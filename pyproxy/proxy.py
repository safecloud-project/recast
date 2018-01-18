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

from pyproxy.metadata import extract_entanglement_data, Files
from pyproxy.playcloud_pb2 import Strip
import pyproxy.coder_client
import pyproxy.proxy_service
import pyproxy.pyproxy_globals
import pyproxy.utils


log_config = os.getenv("LOG_CONFIG", os.path.join(os.path.dirname(__file__), "logging.conf"))
logging.config.fileConfig(log_config)

LOGGER = logging.getLogger("proxy")


# GRPC setup
DEFAULT_GRPC_TIMEOUT_IN_SECONDS = 60
GRPC_MESSAGE_SIZE = (2 * 1024 * 1024 * 1024) - 1 # 2^31 - 1
GRPC_OPTIONS = [
    ("grpc.max_receive_message_length", GRPC_MESSAGE_SIZE),
    ("grpc.max_send_message_length", GRPC_MESSAGE_SIZE)
]
CODER_CLIENT = pyproxy.coder_client.LocalCoderClient()

# Loading dispatcher
DISPATCHER = pyproxy.pyproxy_globals.get_dispatcher_instance()

# Loading the Files metadata structure
FILES = Files()

# Bottle webapp configuration
bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 * 1024
APP = bottle.app()

# Setup kazoo
KAZOO = None
HOSTNAME = os.uname()[1]


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
    start = time.clock()
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

        metadata.entangling_blocks = extract_entanglement_data(encoded_file.strips[0].data)

        FILES.put(key, metadata)
        end = time.clock()
        elapsed = end - start
        LOGGER.debug("Store request for {:s} took {:f} seconds".format(key, elapsed))
        return key


@APP.route("/<key:path>", method="PUT")
def put(key):
    """
    Handles PUT requests to store data into playcloud
    """
    start = time.clock()
    LOGGER.debug("Received put request for key {:s}".format(key))
    # Check if the PUT request actually carries any data in its body to avoid
    # storing empty blocks under a key.
    data = request.body.getvalue()
    if not data:
        return abort(400, "The request body must contain data to store")
    key = store(key=key, data=request.body.getvalue())
    end = time.clock()
    elapsed = end - start
    LOGGER.debug("put request for {:s} took {:f} seconds".format(key, elapsed))
    return key


@APP.route("/", method="PUT")
def put_keyless():
    """
    Handle PUT requests for key-less database insertions
    """
    # Check if the PUT request actually carries any data in its body to avoid
    # storing empty blocks under a key.
    start = time.clock()
    data = request.body.getvalue()
    if not data:
        return abort(400, "The request body must contain data to store")    
    key = store(key=None, data=request.body.getvalue())
    end = time.clock()
    elapsed = end - start
    LOGGER.debug("put_keyless request took {:f} seconds".format(elapsed))
    return key

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

@APP.route("/R3Knge0dnlDxZcHXH6iip9DZ+greFpvIKYpSTuhyHWLHybrc6Kmt1H84NkI71wjI", method="GET")
def dummy_route():
    """
    Dummy route to test that the server is alive and get a fast response
    """
    return "OK"

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
    playcloud_pb2.add_ProxyServicer_to_server(pyproxy.proxy_service.ProxyService(), GRPC_SERVER)
    GRPC_SERVER.add_insecure_port("0.0.0.0:1234")
    GRPC_SERVER.start()
    KAZOO = pyproxy.utils.init_zookeeper_client()
    run(server="bjoern", app=APP, host="0.0.0.0", port=3000, debug=False, quiet=True)
    KAZOO.stop()
