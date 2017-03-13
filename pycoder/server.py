"""Main pycoder module that launches the GRPC server."""

import os
import time

from ConfigParser import ConfigParser

import concurrent.futures
import grpc

import playcloud_pb2
from coding_servicer import CodingService

if __name__ == "__main__":
    CONFIG = ConfigParser()
    CONFIG.read(os.path.join(os.path.dirname(__file__), "pycoder.cfg"))

    PYCODER_LISTEN_ADDRESS = None
    if os.environ.has_key("GRPC_LISTEN_ADDRESS"):
        PYCODER_LISTEN_ADDRESS = os.environ.get("GRPC_LISTEN_ADDRESS")
    elif CONFIG.has_option("main", "listen_address"):
        PYCODER_LISTEN_ADDRESS = CONFIG.get("main", "listen_address")
    else:
        raise RuntimeError("A value must be defined for the grpc listen address either in pycoder.cfg or as an environment variable GRPC_LISTEN_ADDRESS")

    PYCODER_LISTEN_PORT = None
    if os.environ.has_key("GRPC_LISTEN_PORT"):
        PYCODER_LISTEN_PORT = os.environ.get("GRPC_LISTEN_PORT")
    elif CONFIG.has_option("main", "listen_port"):
        PYCODER_LISTEN_PORT = CONFIG.get("main", "listen_port")
    else:
        raise RuntimeError("A value must be defined for the grpc listen port either in pycoder.cfg or as an environment variable GRPC_LISTEN_PORT")

    SERVER = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    playcloud_pb2.add_EncoderDecoderServicer_to_server(CodingService(), SERVER)
    PYCODER_LISTEN = PYCODER_LISTEN_ADDRESS + ":" + PYCODER_LISTEN_PORT
    SERVER.add_insecure_port(PYCODER_LISTEN)
    SERVER.start()
    print "pycoder server listening on ", PYCODER_LISTEN
    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        SERVER.stop(10)
