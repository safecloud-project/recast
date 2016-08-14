"""
A GRPC client for the proxy service that recovers block from the data stores
"""
from grpc.beta import implementations

from playcloud_pb2 import beta_create_Proxy_stub, BlockRequest

# TODO Read the default grpc timeout in configuration file before assigning this value
DEFAULT_GRPC_TIMEOUT_IN_SECONDS = 60

class ProxyClient(object):
    """
    A GRPC client for the proxy service that gets blocks from the data stores
    """
    def __init__(self, host="proxy", port=1234):
        grpc_channel = implementations.insecure_channel(host, port)
        self.stub = beta_create_Proxy_stub(grpc_channel)

    def get_random_blocks(self, blocks):
        """
        Returns a number of random blocks from the data stores.
        Args:
            blocks (int): The number of blocks desired
        Returns:
            list(Strip): Returns a list of ```blocks``` strips from the data stores
        Raises:
            ValueError: if the blocks arguments has a value that is lower or equal to 0
        """
        # TODO Handle grpc.framework.interfaces.face.face.RemoteError
        if blocks <= 0:
            raise ValueError("argument blocks cannot be lower or equal to 0")
        request = BlockRequest()
        request.blocks = blocks
        reply = self.stub.GetRandomBlocks(request, DEFAULT_GRPC_TIMEOUT_IN_SECONDS)
        strips = [strip for strip in reply.strips]
        return strips
