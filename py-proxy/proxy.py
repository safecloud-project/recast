"""
A python implementation of playcloud's proxy server
"""
import logging
import logging.config

import os
import uuid

from bottle import request, response, run
import bottle
from grpc.beta import implementations


from playcloud_pb2 import beta_create_EncoderDecoder_stub, DecodeRequest, EncodeRequest, Strip

log_config = os.getenv("LOG_CONFIG", "/usr/local/src/py-proxy/logging.conf")
logging.config.fileConfig(log_config)

logger = logging.getLogger("proxy")

con_log = "Going to connect to {} in {}:{}"
from safestore.providers.dispatcher import Dispatcher

# GRPC setup
DEFAULT_GRPC_TIMEOUT_IN_SECONDS = 540
CODER_HOST = os.getenv("CODER_PORT_1234_TCP_ADDR", "127.0.0.1")
CODER_PORT = int(os.getenv("CODER_PORT_1234_TCP_PORT", 1234))

logger.info(con_log.format("pycoder", CODER_HOST, CODER_PORT))
GRPC_CHANNEL = implementations.insecure_channel(CODER_HOST, CODER_PORT)

CLIENT_STUB = beta_create_EncoderDecoder_stub(GRPC_CHANNEL)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_PORT_6379_TCP_ADDR", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT_6379_TCP_PORT", 6379))

logger.info(con_log.format("redis", REDIS_HOST, REDIS_PORT))

DISPACHER = Dispatcher()

# Bottle webapp configuration
bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 * 1024
APP = bottle.app()


@APP.route("/<key>", method="GET")
def get(key):
    """
    Handles GET requests to retrieve data stored under <key> from playcloud

    key -- Key under which the data should have been stored
    """
    logger.debug("Received get request for key {}".format(key))
    blocks = DISPACHER.get(key)
    if blocks is None:
        response.status = 404
        return ""
    strips = []
    for block in blocks:
        strip = Strip()
        strip.data = block
        strips.append(strip)

    logger.debug("Received blocks from redis")

    decode_request = DecodeRequest()
    decode_request.strips.extend(strips)

    logger.debug("Goin go to do decode request")

    data = CLIENT_STUB.Decode(
        decode_request, DEFAULT_GRPC_TIMEOUT_IN_SECONDS).dec_block
    return data


def store(key=None, data=None):
    """
    Store data into playcloud

    key -- Key under which the data should be stored (default None)
    """
    if key is None:
        key = str(uuid.uuid4())
    encode_request = EncodeRequest()
    encode_request.payload = data
    logger.debug("Going to encode data")
    strips = CLIENT_STUB.Encode(encode_request, DEFAULT_GRPC_TIMEOUT_IN_SECONDS).strips
    blocks = [strip.data for strip in strips]
    DISPACHER.put(key, blocks)
    return key


@APP.route("/<key>", method="PUT")
def put(key):
    """
    Handles PUT requests to store data into playcloud
    """
    logger.debug("Received put request for key {}".format(key))

    return store(key=key, data=request.body.getvalue())


@APP.route("/", method="PUT")
def put_keyless():
    """
    Handle PUT requests for key-less database insertions
    """
    return store(key=None, data=request.body.getvalue())

if __name__ == "__main__":
    run(app=APP, host="0.0.0.0", port=8000)
