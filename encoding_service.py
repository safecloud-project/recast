"""The Python implementation of the GRPC playcloud.EncoderDecoder server."""

import playcloud_pb2

class EncoderDecoder(playcloud_pb2.EarlyAdopterEncoderDecoderServicer):

  def Encode(self, request, context):
    #here invoke pylonghair
  def Decode(self, request,context):
    #here invoke pylonghair   

def serve():
  server = playcloud_pb2.early_adopter_create_EncoderDecoder_server(Greeter())
  server.add_insecure_port('[::]:50051')
  server.start()
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    server.stop()

if __name__ == '__main__':
  serve()