#! /usr/bin/env python
"""
A script that configures playcloud for a semi-manual distributed deployment
"""
import argparse
import copy
import os
import re

import configure

__SCRIPT_DESCRIPTION = """
A script that configures playcloud for a semi-manual distributed deployment"""


PATH_TO_CONFIGURATION_JSON = os.path.join(os.path.dirname(__file__),
                                          "..",
                                          "configuration.json")

STORAGE_NODE_PATTERN = re.compile(r".+-(\d+)$")

def read_hosts_file(hosts_file):
    """
    Reads a hosts file where host are listed line by line
    Args:
        hosts_file: Path to the hosts file
    Returns:
        list(str): A list hosts
    """
    if not os.path.isfile(hosts_file):
        message = "{:s} is not a valid file".format(hosts_file)
        raise ValueError(message)
    with open(hosts_file, "r") as handle:
        return [line.strip() for line in handle.readlines()]

def move_minio_node(node, provider_name, host):
    """
    Changes the configuration of a minio node in the dispatcher configuration to
    point to a given host.
    Args:
        node(dict): Configuration of the storage node
        provider_name(str): Name of the original provider used locally
        host(str): Name of the host the address must be changed to
    Returns:
        dict: A modified version of the minio node pointing to the given host
    """
    if not node or not isinstance(node, dict):
        raise ValueError("argument node should be a valid dictionnary")
    if not provider_name or not isinstance(provider_name, (str, unicode)):
        raise ValueError("argument provider_name should be a valid string")
    if not host or not isinstance(host, (str, unicode)):
        raise ValueError("argument host should be a valid string")
    modified_node = copy.deepcopy(node)
    modified_node["endpoint_url"] = modified_node["endpoint_url"].replace(provider_name, host)
    return modified_node

def move_redis_node(node, provider_name, host):
    """
    Changes the configuration of a redis node in the dispatcher configuration to
    point to a given host.
    Args:
        node(dict): Configuration of the storage node
        provider_name(str): Name of the original provider used locally
        host(str): Name of the host the address must be changed to
    Returns:
        dict: A modified version of the redis node pointing to the given host
    """
    if not node or not isinstance(node, dict):
        raise ValueError("argument node should be a valid dictionnary")
    if not provider_name or not isinstance(provider_name, (str, unicode)):
        raise ValueError("argument provider_name should be a valid string")
    if not host or not isinstance(host, (str, unicode)):
        raise ValueError("argument host should be a valid string")
    modified_node = copy.deepcopy(node)
    modified_node["host"] = host
    return modified_node

def get_index_from_provider_name(name):
    """
    Extratcs the index from a storage node name
    Args:
        name(str): storage node name
    Returns:
        int: Index of the storage node
    """
    return int(STORAGE_NODE_PATTERN.match(name).group(1))

def distribute_disptacher_configuration(dispatcher_configuration, hosts):
    """
    Assign each of the storage node in a dispatcher configuration object to a
    list of hosts.
    Args:
        dispatcher_configuration(dict): The configuration of the dispatcher
        hosts(list(str)): The list of hosts
    Returns:
        dict: The modified dispatcher configuration that is distributed node aware
    """
    if len(dispatcher_configuration["providers"]) != len(hosts):
        message = "The number of storage nodes listed by the dispatcher and the hosts file is different ({:d} != {:d})".format(len(dispatcher_configuration["providers"]), len(hosts))
        raise RuntimeError(message)
    conf = copy.deepcopy(dispatcher_configuration)
    for index, provider in enumerate(sorted(conf["providers"], key=get_index_from_provider_name)):
        provider_type = conf["providers"][provider]["type"]
        if provider_type == "s3":
            conf["providers"][provider] = move_minio_node(conf["providers"][provider],
                                                          provider,
                                                          hosts[index])
        elif provider_type == "redis":
            conf["providers"][provider] = move_redis_node(conf["providers"][provider],
                                                          provider,
                                                          hosts[index])
        else:
            message = "{:s} is not a supported node type"
            raise RuntimeError(message)
    return conf

def distribute_docker_compose_configuration(compose_configuration):
    """
    Remove the storage nodes from the docker compose configuration
    Args:
        compose_configuration(dict): Original docker-compose configuration
    Returns:
        dict: Modified docker-compose configuration
    """
    modified_compose_configuration = copy.deepcopy(compose_configuration)
    services = modified_compose_configuration["services"]
    storage_nodes = [s for s in services if STORAGE_NODE_PATTERN.match(s)]
    for node in storage_nodes:
        del modified_compose_configuration["services"][node]
        if node in modified_compose_configuration["services"]["proxy"]["depends_on"]:
            modified_compose_configuration["services"]["proxy"]["depends_on"].remove(node)
    return modified_compose_configuration

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(__file__, description=__SCRIPT_DESCRIPTION)
    PARSER.add_argument("hosts_file",
                        type=str,
                        help="""
                        Path to the file containing the list of hosts that will run a storage node
                        """)
    ARGS = PARSER.parse_args()
    HOSTS = read_hosts_file(ARGS.hosts_file)
    CONFIGURATION = configure.read_configuration_file(PATH_TO_CONFIGURATION_JSON)
    DISPATCHER_CONFIGURATION = configure.create_dispatcher_configuration(CONFIGURATION)
    DISTRIBUTED_DISPATCHER_CONFIGURATION = distribute_disptacher_configuration(DISPATCHER_CONFIGURATION, HOSTS)
    configure.write_dispatcher_file(DISTRIBUTED_DISPATCHER_CONFIGURATION)
    COMPOSE_CONFIGURATION = configure.create_docker_compose_configuration(CONFIGURATION)
    DISTRIBUTED_COMPOSE_CONFIGURATION = distribute_docker_compose_configuration(COMPOSE_CONFIGURATION)
    configure.write_docker_compose_file_for_dev(DISTRIBUTED_COMPOSE_CONFIGURATION)
