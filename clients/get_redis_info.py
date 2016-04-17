#! /usr/bin/env python
"""
Scripting utilities to extract memory usage information by redis nodes used by a
playcloud instance.
"""

import json
import os
import redis

def is_provider_redis(provider):
    """
    Check if a provider configuration is a redis configuration
    """
    return provider.get("type") is not None and provider.get("type") == "redis"


def load_redis_nodes_config():
    """
    Load py-proxy's dispatcher configuration and filters it to get the redis
    providers configuration.
    Returns:
        A list of dictionaries with the configuration for each redis nodes
    """
    config_path = os.path.join(os.path.dirname(__file__), "../py-proxy/dispatcher.json")
    with open(config_path, "r") as raw_config:
        providers = json.load(raw_config).get('providers')
        return [provider for provider in providers if is_provider_redis(provider)]

def get_redis_info_all(configuration):
    """
    Connect to a redis database and execute an 'INFO ALL' command:
    Args:
        configuration: A dictionary with the settings to connect to the database
    Returns:
        A dictionary with the values obtained from the 'INFO ALL' comman on a
        redis instance.
    """
    host = configuration.get("host", os.getenv("REDIS_PORT_6379_TCP_ADDR", "127.0.0.1"))
    port = int(configuration.get("port", os.getenv("REDIS_PORT_6379_TCP_PORT", 6379)))
    redis_cxn = redis.StrictRedis(host=host, port=port, db=0)
    data = redis_cxn.info()
    return data

if __name__ == "__main__":
    REDIS_CONFIGURATIONS = load_redis_nodes_config()
    infos = []
    for redis_configuration in REDIS_CONFIGURATIONS:
        infos.append(get_redis_info_all(redis_configuration))
    print json.dumps(infos, sort_keys=True, indent=4)
