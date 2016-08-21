"""Main pycoder module that launches the GRPC server."""
from ConfigParser import ConfigParser
import os
import time

from playcloud_pb2 import beta_create_EncoderDecoder_server
from coding_servicer import CodingService

if __name__ == "__main__":
    config = ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "pycoder.cfg"))
    PYCODER_LISTEN_ADDRESS = "0.0.0.0"
    if os.environ.get("GRPC_LISTEN_ADDRESS") is not None:
        PYCODER_LISTEN_ADDRESS = os.environ.get("GRPC_LISTEN_ADDRESS")
    elif config.has_section("main") and config.get("main", "listen_address") is not None:
        PYCODER_LISTEN_ADDRESS = config.get("main", "listen_address")
    PYCODER_LISTEN_PORT = "1234"
    if os.environ.get("GRPC_LISTEN_PORT"):
        PYCODER_LISTEN_PORT = os.environ.get("GRPC_LISTEN_PORT")
    elif config.has_section("main") and config.get("main", "listen_port") is not None:
        PYCODER_LISTEN_PORT = config.get("main", "listen_port")
    PYCODER_LISTEN = PYCODER_LISTEN_ADDRESS + ":" + PYCODER_LISTEN_PORT
    SERVER = beta_create_EncoderDecoder_server(CodingService())
    SERVER.add_insecure_port(PYCODER_LISTEN)
    SERVER.start()
    print "pycoder server listening on ", PYCODER_LISTEN
    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        SERVER.stop(10)
