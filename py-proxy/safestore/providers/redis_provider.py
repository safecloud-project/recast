"""
A storage provider inspired by the safestore providers to store and get data
from a Redis database
"""
import os
import redis

class RedisProvider(object):
    """
    A storage provider that stores data in a Redis database
    """

    def __init__(self,
                 host=os.getenv("REDIS_PORT_6379_TCP_ADDR", "127.0.0.1"),
                 port=int(os.getenv("REDIS_PORT_6379_TCP_PORT", 6379))):
        self.redis = redis.StrictRedis(host=host, port=port, db=0)

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
            True if the insertion worked, false otherwise
        """
        self.redis.set(path, data)

    def delete(self, path):
        """
        Delete data from the database
        Args:
            path: key of the file to delete
        Returns:
            The number of keys deleted from the database
        """
        return self.redis.delete(path)
