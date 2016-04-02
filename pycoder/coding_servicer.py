"""Wrapper for pyeclib encoders using GRPC"""
from ConfigParser import ConfigParser
import os
import logging
import logging.config

from pyeclib.ec_iface import ECDriver

from custom_drivers import ECStripingDriver
from custom_drivers import PylonghairDriver
from playcloud_pb2 import BetaEncoderDecoderServicer
from playcloud_pb2 import DecodeReply
from playcloud_pb2 import EncodeReply
from playcloud_pb2 import Strip

from safestore.encryption.xor_driver import XorDriver
from safestore.encryption.hashed_xor_driver import HashedXorDriver, Hash, IntegrityException
from safestore.encryption.signed_xor_driver import SignedXorDriver
from safestore.encryption.signed_hashed_xor_driver import SignedHashedXorDriver
from safestore.encryption.aes_driver import AESDriver
from safestore.encryption.shamir_driver import ShamirDriver

CONFIG = ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), "pycoder.cfg"))

log_config = os.getenv("LOG_CONFIG", "/usr/local/src/app/logging.conf")
logging.config.fileConfig(log_config)

logger = logging.getLogger("pycoder")


class DriverFactory():

    def __init__(self, config):
        self.config = config
        self.driver = config.get("main", "driver")
        logger.info("Selected driver was {}".format(self.driver))
        self.drivers = {'xor': self.xor,
                        'hashed_xor_driver': self.hash_xor_driver,
                        'signed_hashed_xor_driver': self.signed_hashed_xor_driver,
                        'shamir': self.shamir,
                        'signed_xor_driver': self.signed_xor_driver,
                        'ec': self.erasure_driver,
                        'aes_driver': self.aes_driver
                        }

    def xor(self):
        nblocks = self.config.getint("xor", "n_blocks")
        nblocks = int(os.environ.get("NBLOCKS", nblocks))
        return XorDriver(nblocks)

    def hash_xor_driver(self):
        nblocks = self.config.getint("hashed_xor_driver", "n_blocks")
        nblocks = int(os.environ.get("NBLOCKS", nblocks))
        hash = self.config.get("hashed_xor_driver", "hash")
        hash = os.environ.get('HASH', hash)
        return HashedDriver(HashedXorDriver(nblocks, Hash[hash]))

    def signed_hashed_xor_driver(self):
        nblocks = self.config.getint("signed_hashed_xor_driver", "n_blocks")
        nblocks = int(os.environ.get("NBLOCKS", nblocks))
        hash = self.config.get("signed_hashed_xor_driver", "hash")
        hash = os.environ.get('HASH', hash)
        return HashedDriver(SignedHashedXorDriver(nblocks, Hash[hash]))

    def shamir(self):
        nblocks = self.config.getint("shamir", "n_blocks")
        threshold = self.config.getint("shamir", "threshold")
        nblocks = int(os.environ.get("NBLOCKS", nblocks))
        threshold = int(os.environ.get("THRESHOLD", nblocks))

        return ShamirDriver(nblocks, threshold)

    def signed_xor_driver(self):
        nblocks = self.config.getint("signed_xor_driver", "n_blocks")
        nblocks = int(os.environ.get("NBLOCKS", nblocks))
        return SignedXorDriver(nblocks)

    def erasure_driver(self):
        EC_K=int(os.environ.get("EC_K", CONFIG.get("ec", "k")))
        EC_M=int(os.environ.get("EC_M", CONFIG.get("ec", "m")))
        EC_TYPE=os.environ.get("EC_TYPE", CONFIG.get("ec", "type"))
        return Eraser(EC_K, EC_M, EC_TYPE)

    def get_driver(self):
        return self.drivers[self.driver]






    def encode(self, data):
        """Encode a string of bytes in flattened string of byte strips"""
        return self.driver.encode(data)

    def decode(self, strips):
        """Decode byte strips in a string of bytes"""
        return self.driver.decode(strips)


def strips_to_bytes(strips):
    """Flatens a list of byte strings in single byte string"""
    flattened_bytes=""
    for strip in strips:
        if isinstance(strip, bytearray):
            flattened_bytes += str(strip)
        else:
            flattened_bytes += strip
    return flattened_bytes


class Eraser(object):
    """A wrapper for pyeclib erasure coding driver (ECDriver)"""

    def __init__(self, k=8, m=2, ec_type="liberasurecode_rs_vand"):
        self.k=k
        self.m=m
        self.ec_type=ec_type
        if EC_TYPE == "pylonghair":
            self.driver=PylonghairDriver(k=EC_K, m=EC_M, ec_type=EC_TYPE)
        elif EC_TYPE == "striping" or EC_TYPE == "bypass":
            self.driver=ECStripingDriver(k=EC_K, m=0, hd=None)
        else:
            self.driver=ECDriver(k=EC_K, m=EC_M, ec_type=EC_TYPE)

    def encode(self, data):
        """Encode a string of bytes in flattened string of byte strips"""
        strips=self.driver.encode(data)
        return strips_to_bytes(strips)

    def decode(self, data):
        """Decode a flattened string of byte strips in a string of bytes"""
        strips=bytes_to_strips(self.k, self.m, data)
        return self.driver.decode(strips)


class CodingService(BetaEncoderDecoderServicer):
    """
    An Encoder/Decoder built on top of playcloud.proto that can be loaded by a
    GRPC server
    """

    def Encode(self, request, context):
        """Encode data sent in an EncodeRequest into a EncodeReply"""
        reply = EncodeReply()
        logger.info("Received encode request")

        raw_strips = self.driver.encode(request.payload)

        log_temp = "Encoded and returned {} raw_strips"
        logger.debug(log_temp.format(len(raw_strips)))

        strips = []
        for raw_strip in raw_strips:
            strip = Strip()
            strip.data = raw_strip
            strips.append(strip)

        reply.strips.extend(strips)
        log_temp = "Request encoded, returning reply with {} strips"
        logger.info(log_temp.format(len(strips)))
        return reply

    def Decode(self, request, context):
        """Decode data sent in an DecodeRequest into a DecodeReply"""
        logger.info("Received decode request")

        reply = DecodeReply()
        strips = convert_strips_to_bytes_list(request.strips)
        reply.dec_block = self.driver.decode(strips)
        logger.info("Request decoded, returning reply")
        return reply
