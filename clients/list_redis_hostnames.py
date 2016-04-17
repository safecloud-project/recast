#! /usr/bin/env python
"""
Scripting utilities to recover the list of hosts
"""

import os

from get_redis_info import load_redis_nodes_config

def get_host_from_config(provider_configuration):
    """
    Returns the host in the configuration or a default value
    Args:
        provider_configuration -- A dictionary with the configuration to connect
            to a storage provider
    Returns:
        a hostname either read from the dictionary, the environment
            variables or the default value 127.0.0.1
    """
    if provider_configuration.has_key("host"):
        return provider_configuration.get("host")
    return os.environ.get("$REDIS_PORT_6379_TCP_ADDR", "127.0.0.1")

def list_hosts():
    """
    Returns the list of hosts for the redis nodes
    Returns:
        a list with hostnames of the machines
    """
    configurations = load_redis_nodes_config()
    return [get_host_from_config(line) for line in configurations]



if __name__ == "__main__":
    hosts = list_hosts()
    for host in hosts:
        print host
