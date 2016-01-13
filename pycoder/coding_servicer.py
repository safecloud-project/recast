import logging

from playcloud_pb2 import *
from pyeclib.ec_iface import ECDriver


class Eraser:
    def __init__(self, k=8, m=2, ec_type="liberasurecode_rs_vand"):
        self.k = k
        self.m = m
        self.ec_type = ec_type
        self.driver = ECDriver(k=self.k, m=self.m, ec_type=self.ec_type)

    def bytes_to_strips(self, data):
        n = self.k + self.m
        length = len(data) / n
        strips = []
        for i in range(n):
            start = i * length
            end = min(len(data), length + i * length)
            strips.append(data[start:end])
        return strips

    def strips_to_bytes(self, strips):
        return "".join(strips)

    def encode(self, data):
        strips = self.driver.encode(data)
        return self.strips_to_bytes(strips)

    def decode(self, data):
        strips = self.bytes_to_strips(data)
        return self.driver.decode(strips)


class CodingService(BetaEncoderDecoderServicer):

    def Encode(self, request, context):
        eraser = Eraser()
        reply = EncodeReply()
        reply.enc_blocks = eraser.encode(request.payload)
        return reply

    def Decode(self, request, context):
        eraser = Eraser()
        reply = DecodeReply()
        reply.dec_block = eraser.decode(request.enc_blocks[0])
        return reply
