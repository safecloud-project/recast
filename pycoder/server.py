"""Main pycoder module that launches the GRPC server"""
import time

from playcloud_pb2 import beta_create_EncoderDecoder_server
from coding_servicer import CodingService

if __name__ == "__main__":
    SERVER = beta_create_EncoderDecoder_server(CodingService())
    SERVER.add_insecure_port("0.0.0.0:1234")
    SERVER.start()
    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        SERVER.stop(10)
