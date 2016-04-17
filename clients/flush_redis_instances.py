#! /usr/bin/env python
"""
Scripting utilities to flush redis instances
"""

from get_redis_info import load_redis_nodes_config
from get_redis_info import get_redis_connection

def flush_instance(configuration):
    """
    Empties redis instances by sending a 'FLUSH ALL' command
    """
    redis_cxn = get_redis_connection(configuration)
    redis_cxn.flushall()


if __name__ == "__main__":
    REDIS_CONFIGURATIONS = load_redis_nodes_config()
    for redis_conf in REDIS_CONFIGURATIONS:
        flush_instance(redis_conf)
