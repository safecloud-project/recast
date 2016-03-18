"""Main pycoder module that launches the GRPC server"""
from ConfigParser import ConfigParser
import os
import time

from playcloud_pb2 import beta_create_EncoderDecoder_server
from coding_servicer import CodingService

if __name__ == "__main__":
    config = ConfigParser()
    config.read("pycoder.cfg")
    PYCODER_LISTEN_ADDRESS = os.environ.get("GRPC_LISTEN_ADDRESS", config.get("grpc", "listen_address"))
    PYCODER_LISTEN_PORT = os.environ.get("GRPC_LISTEN_PORT", config.get("grpc", "listen_port"))
    PYCODER_LISTEN = PYCODER_LISTEN_ADDRESS + ":" + PYCODER_LISTEN_PORT
    SERVER = beta_create_EncoderDecoder_server(CodingService())
    SERVER.add_insecure_port(PYCODER_LISTEN)
    MESSAGE = "starting server on\n" + \
    "k = " +    os.environ.get("EC_K", config.get("ec", "k")) + "\n" +\
    "m = " +    os.environ.get("EC_M", config.get("ec", "m")) + "\n" +\
    "type = " + os.environ.get("EC_TYPE", config.get("ec", "type")) + "\n"
    print MESSAGE
    SERVER.start()
    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        SERVER.stop(10)
