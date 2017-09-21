"""
A GRPC client for the proxy service that recovers block from the data stores
"""
import grpc

import pyproxy.coder.playcloud_pb2_grpc
from pyproxy.coder.playcloud_pb2 import BlockRequest, NamedBlockRequest, Strip
from pyproxy.proxy_service import get_random_blocks
from pyproxy.pyproxy_globals import get_dispatcher_instance
from pyproxy.safestore.providers.dispatcher import NoReplicaException

# TODO Read the default grpc timeout in configuration file before assigning this value
DEFAULT_GRPC_TIMEOUT_IN_SECONDS = 60

class ProxyClient(object):
    """
    A GRPC client for the proxy service that gets blocks from the data stores
    """
    def __init__(self, host="proxy", port=1234):
        server_listen = host + ":" + str(port)
        grpc_message_size = (2 * 1024 * 1024 * 1024) - 1 # 2^31 - 1
        grpc_options = [
            ("grpc.max_receive_message_length", grpc_message_size),
            ("grpc.max_send_message_length", grpc_message_size)
        ]
        grpc_channel = grpc.insecure_channel(server_listen, options=grpc_options)
        self.stub = pyproxy.coder.playcloud_pb2_grpc.ProxyStub(grpc_channel)

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

    def get_block(self, path, index, reconstruct_if_missing=True):
        """
        Returns a single block from the data stores.
        Args:
            path(str): Name of the file
            index(int): Index of the block
            reconstruct_if_missing(bool, optional): If the dispatcher should try
                                                    to reconstruct the block if
                                                    it cannot be fetched from
                                                    the storage nodes. Defaults
                                                    to True
        Returns:
            Strip: The data requested
        Raises:
            ValueError: if the path is empty or the index is negative
        """
        if not path or not path.strip():
            raise ValueError("path argument cannot empty")
        if index < 0:
            raise ValueError("index argument cannot be negative")
        request = NamedBlockRequest()
        request.path = path
        request.index = index
        request.reconstruct_if_missing = reconstruct_if_missing
        return self.stub.GetBlock(request, DEFAULT_GRPC_TIMEOUT_IN_SECONDS)

class LocalProxyClient(object):
    """
    Local proxy client
    """
    def __init__(self):
        self.dispatcher = get_dispatcher_instance()

    def get_random_blocks(self, blocks):
        """
        Args:
            blocks(int): The number of blocks desired
        Returns:
            list(Strip): Returns a list of ```blocks``` strips from the data stores
        Raises:
            ValueError: if the blocks arguments has a value that is lower or equal to 0
        """
        if blocks <= 0:
            raise ValueError("argument blocks cannot be lower or equal to 0")
        return get_random_blocks(blocks)

    def get_block(self, path, index, reconstruct_if_missing=True):
        """
        Returns a single block from the data stores.
        Args:
            path(str): Name of the file
            index(int): Index of the block
            reconstruct_if_missing(bool, optional): If the dispatcher should try
                                                    to reconstruct the block if
                                                    it cannot be fetched from
                                                    the storage nodes. Defaults
                                                    to True
        Returns:
            Strip: The data requested
        Raises:
            ValueError: if the path is empty or the index is negative
        """
        if not path or not path.strip():
            raise ValueError("path argument cannot empty")
        if index < 0:
            raise ValueError("index argument cannot be negative")
        data = self.dispatcher.get_block(path,
                                         index,
                                         reconstruct_if_missing=reconstruct_if_missing)
        reply = Strip()
        if not isinstance(data, NoReplicaException):
            reply.data = data
        return reply
