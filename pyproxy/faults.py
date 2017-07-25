"""
Utilities to mess with the blocks, files and storage nodes in playcloud
"""
import logging.config

import docker

LOGGER = logging.getLogger("FAULTS")


def start_node(name):
    """
    Start a node that was previously stopped using its service name
    Args:
        name(str): Name of the storage to stop
    Returns:
        list(docker.models.containers.Container): The list of containers that started
    """
    if not name:
        raise ValueError("name argument must be a non-empty string")
    containers = __get_containers(name)
    started = []
    for container in containers:
        try:
            container.start()
            LOGGER.debug("Successfuly started container {:s} ({:s})"
                         .format(container.name, container.id))
            started.append(container)
        except docker.errors.APIError:
            LOGGER.error("Could not start container {:s} ({:s})"
                         .format(container.name, container.id))

def stop_node(name):
    """
    Stop a node identified by its service name
    Args:
        name(str): Name of the storage to stop
    Returns:
        list(docker.models.containers.Container): The list of containers that were stopped
    """
    if not name:
        raise ValueError("name argument must be a non-empty string")
    containers = __get_containers(name)
    stopped_containers = []
    for container in containers:
        try:
            container.stop()
            LOGGER.debug("Successfuly stopped container {:s} ({:s})"
                         .format(container.name, container.id))
            stopped_containers.append(container)
        except docker.errors.APIError:
            LOGGER.error("Could not stop container {:s} ({:s})"
                         .format(container.name, container.id))
    return stopped_containers

def __get_containers(name):
    """
    Args:
        name(str): Name of the node to match
    Returns:
        list(docker.models.containers.Container): A list of containers matching
            that name
    """
    if not name:
        raise ValueError("name argument must be a non-empty string")
    client = docker.from_env()
    return [c for c in client.containers.list(all=True) if c.name.find(name) != -1]
