#! /usr/bin/env python
"""
A script that looks at the current instance of playcloud running and outputs stats
about it.
"""
import argparse
import json

import docker

PROGRAM_DESCRIPTION = "A script that looks at a docker network and returns " + \
                      "network stats for the containers attached to it"

def list_containers_on_network(network="playcloud_default"):
    """
    Args:
        network(str): The name of the docker network whose attached containers
                      must be listed
    Returns:
        list(docker.models.containers.Container): A list of containers
    """
    client = docker.client.DockerClient()
    net = client.networks.get(network)
    return net.containers


def get_network_io(container):
    """
    Args:
        container(docker.models.containers.Container): The container to look at
        network(str): The name of the docker network whose attached containers
                      must be listed
    Returns:
        dict(str, int): Amount of traffic received and exchanged
    """
    if not container or not isinstance(container, docker.models.containers.Container):
        raise ValueError("container argument must be a valid instance of " +
                         "docker.models.containers.Container")
    network_stats = container.stats(stream=False)[u"networks"]
    for interface in network_stats:
        return network_stats[interface]


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(__file__, description=PROGRAM_DESCRIPTION)
    PARSER.add_argument("--network",
                        type=str,
                        default="playcloud_default",
                        help="Name of the docker network to inspect (defaults to playcloud_default)")
    ARGS = PARSER.parse_args()
    CONTAINERS = list_containers_on_network(ARGS.network)
    RESULTS = {CONTAINER.name: get_network_io(CONTAINER) for CONTAINER in CONTAINERS}
    print json.dumps(RESULTS, sort_keys=True, indent=4, separators=(',', ': '))
