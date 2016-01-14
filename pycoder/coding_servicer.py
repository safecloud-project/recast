"""Wrapper for pyeclib encoders using GRPC"""
import ConfigParser

from playcloud_pb2 import BetaEncoderDecoderServicer
from playcloud_pb2 import DecodeReply
from playcloud_pb2 import EncodeReply
from pyeclib.ec_iface import ECDriver

config = ConfigParser.ConfigParser()
config.read("pycoder.cfg")

def bytes_to_strips(k, m, payload):
    """Transforms a byte string in a list of bytes string"""
    disks = k + m
    length = len(payload) / disks
    strips = []
    for i in range(disks):
        start = i * length
        end = min(len(payload), length + i * length)
        strips.append(payload[start:end])
    return strips

def strips_to_bytes(strips):
    """Flatens a list of byte strings in single byte string"""
    return "".join(strips)

class Eraser(object):
    """A wrapper for pyeclib erasure coding driver (ECDriver)"""
    def __init__(self, k=8, m=2, ec_type="liberasurecode_rs_vand"):
        self.k = k
        self.m = m
        self.ec_type = ec_type
        self.driver = ECDriver(k=self.k, m=self.m, ec_type=self.ec_type)

    def encode(self, data):
        """Encode a string of bytes in flattened string of byte strips"""
        strips = self.driver.encode(data)
        return strips_to_bytes(strips)

    def decode(self, data):
        """Decode a flattened string of byte strips in a string of bytes"""
        strips = bytes_to_strips(self.k, self.m, data)
        return self.driver.decode(strips)

EC_K = int(config.get("ec", "k"))
EC_M = int(config.get("ec", "m"))
EC_TYPE = config.get("ec", "type")
ERASER = Eraser(EC_K, EC_M, EC_TYPE)

class CodingService(BetaEncoderDecoderServicer):
    """An Encoder/Decoder built on top of playcloud.proto that can be loaded by a GRPC server"""
    def Encode(self, request, context):
        """Encode data sent in an EncodeRequest into a EncodeReply"""
        reply = EncodeReply()
        reply.enc_blocks = ERASER.encode(request.payload)
        return reply

    def Decode(self, request, context):
        """Decode data sent in an DecodeRequest into a DecodeReply"""
        reply = DecodeReply()
        reply.dec_block = ERASER.decode(request.enc_blocks[0])
        return reply
