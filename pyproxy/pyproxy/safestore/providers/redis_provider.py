"""
A storage provider inspired by the safestore providers to store and get data
from a Redis database
"""
import os
import sys

import redis

class RedisProvider(object):
    """
    A storage provider that stores data in a Redis database
    """
    def __init__(self, configuration={}):
        host = configuration.get("host", os.getenv("REDIS_PORT_6379_TCP_ADDR", "redis"))
        port = int(configuration.get("port", os.getenv("REDIS_PORT_6379_TCP_PORT", 6379)))
        self.redis = redis.StrictRedis(host=host, port=port, db=0, encoding=None, socket_keepalive=True)

    def get(self, path):
        """
        Fetches data from the database stored under the key <path>
        Args:
            path: Key under which the data is stored
        Returns:
            The data if it was found, None otherwise
        """
        return self.redis.get(path)

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
        return self.redis.set(path, data)

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

    @staticmethod
    def quota():
        """
        A compatibility method that returns sys.maxint.
        Returns:
            The value of sys.maxint
        """
        return sys.maxint
