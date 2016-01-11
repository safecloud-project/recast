from playcloud_pb2 import *

class CodingService(BetaEncoderDecoderServicer):
    def Encode(self, request, context):
        reply = EncodeReply()
        reply.enc_blocks = request.payload
        return reply

    def Decode(self, request, context):
        reply = DecodeReply()
        reply.dec_block = request.enc_blocks[0]
        return reply
