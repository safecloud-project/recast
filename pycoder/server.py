import time
import sys

from playcloud_pb2 import beta_create_EncoderDecoder_server
from coding_servicer import CodingService

if __name__ == "__main__":
    server = beta_create_EncoderDecoder_server(CodingService())
    server.add_insecure_port("0.0.0.0:1234")
    server.start()
    try:
        while True:
          time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(10)
