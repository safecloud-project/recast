"""Main pycoder module that launches the GRPC server"""
import ConfigParser
import time

from playcloud_pb2 import beta_create_EncoderDecoder_server
from coding_servicer import CodingService

if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read("pycoder.cfg")
    PYCODER_LISTEN_ADDRESS = config.get("grpc", "listen_address")
    PYCODER_LISTEN_PORT = config.get("grpc", "listen_port")
    PYCODER_LISTEN = PYCODER_LISTEN_ADDRESS + ":" + PYCODER_LISTEN_PORT
    SERVER = beta_create_EncoderDecoder_server(CodingService())
    SERVER.add_insecure_port(PYCODER_LISTEN)
    print "starting server on"
    print "k =", int(config.get("ec", "k"))
    print "m =", int(config.get("ec", "m"))
    print "type =", config.get("ec", "type")
    SERVER.start()
    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        SERVER.stop(10)
