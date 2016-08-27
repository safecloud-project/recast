"""
A python implementation of playcloud's proxy server
"""
import json
import logging
import logging.config
import os
import uuid

from bottle import request, response, run
import bottle
from grpc.beta import implementations


from pyproxy_globals import get_dispatcher_instance
from playcloud_pb2 import beta_create_EncoderDecoder_stub, DecodeRequest, EncodeRequest, Strip, beta_create_Proxy_server
from proxy_service import ProxyService

log_config = os.getenv("LOG_CONFIG", "/usr/local/src/pyproxy/logging.conf")
logging.config.fileConfig(log_config)

logger = logging.getLogger("proxy")

con_log = "Going to connect to {} in {}:{}"

# GRPC setup
DEFAULT_GRPC_TIMEOUT_IN_SECONDS = 60
CODER_HOST = os.getenv("CODER_PORT_1234_TCP_ADDR", "coder")
CODER_PORT = int(os.getenv("CODER_PORT_1234_TCP_PORT", 1234))

logger.info(con_log.format("pycoder", CODER_HOST, CODER_PORT))
GRPC_CHANNEL = implementations.insecure_channel(CODER_HOST, CODER_PORT)

CLIENT_STUB = beta_create_EncoderDecoder_stub(GRPC_CHANNEL)

# Loading dispatcher
DISPATCHER = get_dispatcher_instance()

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
    blocks = DISPATCHER.get(key)
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
    logger.info("Going to request data encoding")
    strips = CLIENT_STUB.Encode(encode_request, DEFAULT_GRPC_TIMEOUT_IN_SECONDS).strips
    blocks = [strip.data for strip in strips]
    logger.info("Received {} encoded blocks".format(len(blocks)))
    logger.info("Going to store blocks with key {}".format(key))
    DISPATCHER.put(key, blocks)
    return key


@APP.route("/<key>", method="PUT")
def put(key):
    """
    Handles PUT requests to store data into playcloud
    """
    logger.info("Received put request for key {}".format(key))

    return store(key=key, data=request.body.getvalue())


@APP.route("/", method="PUT")
def put_keyless():
    """
    Handle PUT requests for key-less database insertions
    """
    return store(key=None, data=request.body.getvalue())

@APP.route("/", method="GET")
def list():
    return json.dumps({"files": DISPATCHER.list()})

if __name__ == "__main__":
    GRPC_SERVER = beta_create_Proxy_server(ProxyService())
    GRPC_SERVER.add_insecure_port("0.0.0.0:1234")
    GRPC_SERVER.start()
    run(server="paste", app=APP, host="0.0.0.0", port=8000)
