"""Wrapper for pyeclib encoders using GRPC"""
from ConfigParser import ConfigParser
import os

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
CONFIG.read("pycoder.cfg")


class DriverFactory():

    def __init__(self):
        self.driver = CONFIG.get("main", "grpc")
        self.drivers = {'xor': self.xor,
                        'hashed_xor_driver': self.hash_xor_driver,
                        'signed_hashed_xor_driver': self.signed_hashed_xor_driver,
                        'shamir': self.shamir,
                        'signed_xor_driver': self.signed_xor_driver
                        'erasure_driver': self.erasure_driver}

    def xor(self):
        return XorDriver(CONFIG.getint("xor", "n_blocks")

    def hash_xor_driver(self):
        nblocks=CONFIG.getint("hashed_xor_driver", "n_blocks")
        hash=CONFIG.get("hashed_xor_driver", "hash")
        return HashedXorDriver(nblocks, hash)

    def signed_hashed_xor_driver(self):
        nblocks=CONFIG.getint("signed_hashed_xor_driver", "n_blocks")
        hash=CONFIG.get("signed_hashed_xor_driver", "hash")
        return SignedHashedXorDriver(nblocks, hash)

    def shamir(self):
        nblocks=CONFIG.getint("shamir", "n_blocks")
        threshold=CONFIG.getint("shamir", "threshold")
        return Shamir(nblocks, hash)

    def signed_xor_driver(self):
        nblocks=CONFIG.getint("signed_xor_driver", "n_blocks")
        return SignedXorDriver(nblocks)

    def erasure_driver(self):
        EC_K=int(os.environ.get("EC_K", CONFIG.get("ec", "k")))
        EC_M=int(os.environ.get("EC_M", CONFIG.get("ec", "m")))
        EC_TYPE=os.environ.get("EC_TYPE", CONFIG.get("ec", "type"))
        return Eraser(EC_K, EC_M, EC_TYPE)

    def get_driver(self):
        return self.drivers[self.driver]






def bytes_to_strips(k, m, payload):
    """Transforms a byte string in a list of bytes string"""
    disks=k + m
    length=len(payload) / disks
    strips=[]
    for i in xrange(0, len(payload), length):
        strips.append(payload[i: i + length])
    return strips


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
        reply=EncodeReply()
        reply.enc_blocks=ERASER.encode(request.payload)
        return reply

    def Decode(self, request, context):
        """Decode data sent in an DecodeRequest into a DecodeReply"""
        reply=DecodeReply()
        reply.dec_block=ERASER.decode(request.enc_blocks)
        return reply
