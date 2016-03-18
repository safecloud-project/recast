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

CONFIG = ConfigParser()
CONFIG.read("pycoder.cfg")

def convert_strips_to_bytes_list(playcloud_strips):
    """Extract the data bytes from alist of playcloud strips"""
    return [strip.data for strip in playcloud_strips]

class Eraser(object):
    """A wrapper for pyeclib erasure coding driver (ECDriver)"""
    def __init__(self, k=8, m=2, ec_type="liberasurecode_rs_vand"):
        self.k = k
        self.m = m
        self.ec_type = ec_type
        if EC_TYPE == "pylonghair":
            self.driver = PylonghairDriver(k=EC_K, m=EC_M, ec_type=EC_TYPE)
        elif EC_TYPE == "striping" or EC_TYPE == "bypass":
            self.driver = ECStripingDriver(k=EC_K, m=0, hd=None)
        else:
            self.driver = ECDriver(k=EC_K, m=EC_M, ec_type=EC_TYPE)

    def encode(self, data):
        """Encode a string of bytes in flattened string of byte strips"""
        raw_strips = self.driver.encode(data)
        strips = []
        for raw_strip in raw_strips:
            strip = Strip()
            strip.data = raw_strip
            strips.append(strip)
        return strips

    def decode(self, playcloud_strips):
        """Decode byte strips in a string of bytes"""
        strips = convert_strips_to_bytes_list(playcloud_strips)
        return self.driver.decode(strips)

EC_K = int(os.environ.get("EC_K", CONFIG.get("ec", "k")))
EC_M = int(os.environ.get("EC_M", CONFIG.get("ec", "m")))
EC_TYPE = os.environ.get("EC_TYPE", CONFIG.get("ec", "type"))

ERASER = Eraser(EC_K, EC_M, EC_TYPE)

class CodingService(BetaEncoderDecoderServicer):
    """
    An Encoder/Decoder built on top of playcloud.proto that can be loaded by a
    GRPC server
    """
    def Encode(self, request, context):
        """Encode data sent in an EncodeRequest into a EncodeReply"""
        reply = EncodeReply()
        strips = ERASER.encode(request.payload)
        reply.strips.extend(strips)
        return reply

    def Decode(self, request, context):
        """Decode data sent in an DecodeRequest into a DecodeReply"""
        reply = DecodeReply()
        reply.dec_block = ERASER.decode(request.strips)
        return reply
