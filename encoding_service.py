"""The Python implementation of the GRPC playcloud.EncoderDecoder server."""

import playcloud_pb2

class EncoderDecoder(playcloud_pb2.BetaEncoderDecoderServicer):

    def Encode(self, request, context):
      #here invoke pylonghair  
      return
    def Decode(self, request,context):
      #here invoke pylonghair  
      return 

def serve():
  server = playcloud_pb2.beta_create_EncoderDecoder_server(EncoderDecoder())
  server.add_insecure_port('[::]:50051')
  server.start()
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    server.stop()

if __name__ == '__main__':
  serve()