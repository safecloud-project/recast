"""
A GRPC service that provides clients with blocks from the active data stores
"""
import logging

from pyproxy.playcloud_pb2_grpc import ProxyServicer
from pyproxy.playcloud_pb2 import BlockReply, Strip
from pyproxy.pyproxy_globals import get_dispatcher_instance

import pyproxy.safestore.providers.dispatcher

class ProxyService(ProxyServicer):
    """
    A GRPC enabled server that serves blocks.
    """
    def __init__(self):
        self.logger = logging.getLogger("ProxyService")

    def GetRandomBlocks(self, request, context):
        """
        Returns a number of random blocks from the data stores
        Args:
            request (BlockRequest): A block request
        Returns:
            BlockReply: A reply with the number of random blocks requested
        """
        self.logger.info("Received GetRandomBlocks request")
        blocks = request.blocks
        self.logger.info("Start request to get " + str(blocks) + " random blocks")
        strips = get_random_blocks(blocks)
        self.logger.info("End request to get " + str(blocks) + " random blocks with " + str(len(strips)) + " blocks")
        reply = BlockReply()
        reply.strips.extend(strips)
        self.logger.info("Replying to GetRandomBlocks request")
        return reply

    def GetBlock(self, request, context):
        """
        Returns one block from the data stores.
        Args:
            request (BlockRequest): A block request
        Returns:
            Strip: A reply with the requested block
        """
        dispatcher = get_dispatcher_instance()
        path = request.path
        index = request.index
        reconstruct_if_missing = request.reconstruct_if_missing
        call_signature = "GetBlock({:s}, {:3d}, reconstruct_if_missing={})".format(path, index, reconstruct_if_missing)
        self.logger.debug("Start {:s}".format(call_signature))
        data = dispatcher.get_block(path,
                                    index,
                                    reconstruct_if_missing=reconstruct_if_missing)
        reply = Strip()
        if not isinstance(data, pyproxy.safestore.providers.dispatcher.NoReplicaException):
            reply.data = data
        self.logger.debug("End   {:s}".format(call_signature))
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
        strip.id = random_block[0]
        strip.data = random_block[1]
        strips.append(strip)
    return strips
