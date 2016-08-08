"""
A GRPC service that provides clients with blocks from the active data stores
"""
from globals import get_dispatcher_instance
from proxy_pb2 import BetaProxyServicer
from proxy_pb2 import BlockReply
from proxy_pb2 import Strip

class ProxyService(BetaProxyServicer):
    """
    A GRPC enabled server that serves blocks.
    """

    def GetRandomBlocks(self, request, context):
        """
        Returns a number of random blocks from the data stores
        Args:
            request (BlockRequest): A block request
        Returns:
            BlockReply: A reply with the number of random blocks requested
        """
        blocks = request.blocks
        strips = get_random_blocks(blocks)
        reply = BlockReply()
        reply.strips.extend(strips)
        return reply

def get_random_blocks(blocks):
    """
    Returns a list of blocks
    Args:
        blocks (int): Number of blocks to retrieve
    Returns:
        list: A list of blocks randomly selected from the data stores
    Raises:
        ValueError: If the number of blocks is lower or equal to zero
    """
    if blocks <= 0:
        raise ValueError("argument blocks cannot be lower or equal to 0")
    dispatcher = get_dispatcher_instance()
    random_blocks = dispatcher.get_random_blocks(blocks)
    strips = []
    for random_block in random_blocks:
        strip = Strip()
        strip.data = random_block[1]
        strips.append(strip)
    return strips
