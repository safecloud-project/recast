"""
A python implementation of playcloud's proxy server
"""
import argparse
import json
import logging
import logging.config
import os
import uuid

from bottle import request, response, run
import bottle
import concurrent.futures
import grpc

import playcloud_pb2
import playcloud_pb2_grpc

from pyproxy_globals import get_dispatcher_instance
from playcloud_pb2 import DecodeRequest, EncodeRequest, Strip
from proxy_service import ProxyService

log_config = os.getenv("LOG_CONFIG", "/usr/local/src/pyproxy/logging.conf")
logging.config.fileConfig(log_config)

LOGGER = logging.getLogger("proxy")

con_log = "Going to connect to {} in {}:{}"

# GRPC setup
DEFAULT_GRPC_TIMEOUT_IN_SECONDS = 60
CODER_HOST = os.getenv("CODER_PORT_1234_TCP_ADDR", "coder")
CODER_PORT = int(os.getenv("CODER_PORT_1234_TCP_PORT", 1234))

LOGGER.info(con_log.format("pycoder", CODER_HOST, CODER_PORT))

CODER_ADDRESS = CODER_HOST + ":" + str(CODER_PORT)
GRPC_CHANNEL = grpc.insecure_channel(CODER_ADDRESS)
CLIENT_STUB = playcloud_pb2_grpc.EncoderDecoderStub(GRPC_CHANNEL)

# Loading dispatcher
DISPATCHER = get_dispatcher_instance()

# Bottle webapp configuration
bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 * 1024
APP = bottle.app()

@APP.route("/<key:path>", method="GET")
def get(key):
    """
    Handles GET requests to retrieve data stored under <key> from playcloud

    key -- Key under which the data should have been stored
    """
    LOGGER.debug("Received get request for key {}".format(key))
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

    decode_request = DecodeRequest()
    decode_request.strips.extend(strips)

    LOGGER.debug("Going go to do decode request")

    data = CLIENT_STUB.Decode(
        decode_request, DEFAULT_GRPC_TIMEOUT_IN_SECONDS).dec_block
    return data

def convert_metadata_to_dictionary(meta):
    """
    Converts a Metadata object to a dictionary that can be JSON serialized
    Args:
        meta(Metadata): Metadata object to convert
    Returns:
        (dict): A dictionary with keys matching the Metadata's attributes
    """
    return {
        "path": meta.path,
        "creation_date": meta.creation_date.isoformat(),
        "original_size": meta.original_size
    }

@APP.route("/<key>/__meta", method="GET")
def get_file_metadata(key):
    """
    Returns Metadata about a file stored in the system.
    Args:
        key(string): Key under which the data is supposed to be stored
    Returns:
        (string): A listing of the files serialized as JSON
    """
    meta = DISPATCHER.files.get(key)
    if meta is None:
        response.status = 404
        return ""
    return json.dumps(convert_metadata_to_dictionary(meta))


def store(key=None, data=None):
    """
    Store data into playcloud

    key -- Key under which the data should be stored (default None)
    """
    if key is None:
        key = str(uuid.uuid4())
    encode_request = EncodeRequest()
    encode_request.payload = data
    LOGGER.debug("Going to request data encoding")
    encoded_file = CLIENT_STUB.Encode(encode_request, DEFAULT_GRPC_TIMEOUT_IN_SECONDS).file
    number_of_blocks = len(encoded_file.strips)
    LOGGER.debug("Received {:2d} encoded blocks from data encoding".format(number_of_blocks))
    LOGGER.debug("Going to store {:2d} blocks with key {:s}".format(number_of_blocks, key))
    DISPATCHER.put(key, encoded_file)
    LOGGER.debug("Stored {:2d} blocks with key {:s}".format(number_of_blocks, key))
    return key


@APP.route("/<key:path>", method="PUT")
def put(key):
    """
    Handles PUT requests to store data into playcloud
    """
    LOGGER.debug("Received put request for key {:s}".format(key))

    return store(key=key, data=request.body.getvalue())


@APP.route("/", method="PUT")
def put_keyless():
    """
    Handle PUT requests for key-less database insertions
    """
    return store(key=None, data=request.body.getvalue())

@APP.route("/", method="GET")
def list():
    """
    List the files stored in the system.
    Returns:
        (string): A listing of the files serialized as JSON
    """
    entries = [convert_metadata_to_dictionary(meta) for meta in DISPATCHER.list()]
    return json.dumps({"files": entries})

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
    GRPC_SERVER = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    playcloud_pb2.add_ProxyServicer_to_server(ProxyService(), GRPC_SERVER)
    GRPC_SERVER.add_insecure_port("0.0.0.0:1234")
    GRPC_SERVER.start()
    run(server="paste", app=APP, host="0.0.0.0", port=8000)
