"""
A storage provider inspired by the safestore providers to store and get data
from a Redis database
"""
import logging
import os
import sys
import time

from redis import ConnectionPool, StrictRedis

LOGGER = logging.getLogger("dispatcher")

class RedisProvider(object):
    """
    A storage provider that stores data in a Redis database
    """
    CONNECTION_POOLS = {}

    @staticmethod
    def get_pool(host, port):
        """
        Gets an existing connection pool to a given server or creates a new one
        Args:
            host(str): Host of the redis server
            port(int): Port number the resdis server is listening on
        Returns:
            BlockingConnectionPool: A blocking redis connection pool
        """
        if not isinstance(host, (str, unicode)) or not host:
            raise ValueError("host argument must be a non empty string")
        if not isinstance(port, int) or port <= 0 or port > 65535:
            raise ValueError("port argument must be an integer between 0 and 65535")
        if not host in RedisProvider.CONNECTION_POOLS:
            RedisProvider.CONNECTION_POOLS[host] = {}
        if not port in RedisProvider.CONNECTION_POOLS[host]:
            RedisProvider.CONNECTION_POOLS[host][port] = ConnectionPool(host=host,
                                                                        port=port,
                                                                        db=0,
                                                                        max_connections=128,
                                                                        socket_keepalive=True)
        return RedisProvider.CONNECTION_POOLS[host][port]

    def __init__(self, configuration=None):
        configuration = configuration or {}
        host = configuration.get("host", os.getenv("REDIS_PORT_6379_TCP_ADDR", "redis"))
        port = int(configuration.get("port", os.getenv("REDIS_PORT_6379_TCP_PORT", 6379)))
        pool = RedisProvider.get_pool(host, port)
        self.host = host
        self.redis = StrictRedis(connection_pool=pool, encoding=None, socket_keepalive=True)

    def get(self, path):
        """
        Fetches data from the database stored under the key <path>
        Args:
            path: Key under which the data is stored
        Returns:
            The data if it was found, None otherwise
        """
        start = time.clock()
        value = self.redis.get(path)
        end = time.clock()
        elapsed = end - start
        LOGGER.info("Provider {:s} fetched {:s} in {:f} seconds".format(self.host, path, elapsed))
        return value

    def put(self, data, path):
        """
        Inserts data in the database under the key <path>
        Args:
            data: Data to store in the database
            path: Key under which the data is stored
        Returns:
            True if the insertion worked
        Raises:
            ConnectionError: If the client cannot connect to the server
        """
        start = time.clock()
        value = self.redis.set(path, data)
        end = time.clock()
        elapsed = end - start
        LOGGER.info("Provider {:s} stored {:s} in {:f} seconds".format(self.host, path, elapsed))
        return value

    def delete(self, path):
        """
        Delete data from the database
        Args:
            path: key of the file to delete
        Returns:
            The number of keys deleted from the database
        """
        return self.redis.delete(path)

    def clear(self):
        """
        Deletes all entries in the redis database
        """
        return self.redis.flushall()

    def list(self):
        """
        Returns:
            list(str): The list of blocks on the storage provider
        """
        return self.redis.keys("*")

    @staticmethod
    def quota():
        """
        A compatibility method that returns sys.maxint.
        Returns:
            The value of sys.maxint
        """
        return sys.maxint
