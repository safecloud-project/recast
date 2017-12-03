#! /usr/bin/env python
"""
A script that reads configuration.json and produces a matching configuration files
for docker-compose and the pyproxy.
"""
import argparse
import copy
import json
import os

from configparser import ConfigParser

import ruamel.yaml

__DESCRIPTION = """
A script that reads configuration.json and produces a matching configuration files
for docker-compose and the pyproxy.
"""

PATH_TO_DISPATCHER_FILE = os.path.join(os.path.dirname(__file__), "..", "pyproxy", "dispatcher.json")
PATH_TO_DOCKER_COMPOSE_FILE = os.path.join(os.path.dirname(__file__), "..", "docker-compose.yml")
PATH_TO_DOCKER_COMPOSE_PRODUCTION_FILE = os.path.join(os.path.dirname(__file__), "..", "docker-compose-production.yml")
PATH_TO_VOLUMES_DIRECTORY = os.path.join(os.path.dirname(__file__), "..", "volumes")
PATH_TO_CODER_CONFIGURATION = os.path.join(os.path.dirname(__file__), "..", "pyproxy", "pycoder.cfg")

BASIC_COMPOSE_CONFIGURATION = {
    "version": "3.3",
    "services": {
        "coder": {
            "container_name": "coder",
            "hostname": "coder",
            "build": "./pyproxy",
            "entrypoint": "python /usr/local/src/pyproxy/coder.py",
            "env_file": ["./erasure.env"],
            "deploy": {
                "placement": {
                    "constraints": ["node.role == manager"]
                }
            }
        },
        "proxy": {
            "container_name": "proxy",
            "hostname": "proxy",
            "build": "./pyproxy",
            "ports": ["3000:3000"],
            "env_file": ["./erasure.env"],
            "deploy": {
                "placement": {
                    "constraints": ["node.role == manager"]
                }
            }
        },
        "metadata": {
            "image": "redis:3.2.8",
            "command": "redis-server --appendonly yes",
            "deploy": {
                "mode": "replicated",
                "placement": {
                    "constraints": ["node.role == manager"]
                }
            },
            "volumes": ["./volumes/metadata/:/data/"]
        },
        "zoo1": {
            "image": "zookeeper",
            "restart": "always",
            "ports": ["2181:2181"],
            "environment": ["ZOO_MY_ID=1"],
            "deploy": {
                "mode": "replicated",
                "placement": {
                    "constraints": ["node.role == manager"]
                }
            }
        }
    }
}


def rename_existing_file(file_path):
    """
    Renames a file with an index number at the end for backup
    """
    if not os.path.exists(file_path):
        return None
    file_index = 1
    while os.path.exists(file_path + "." + str(file_index)):
        file_index += 1
    new_file_path = file_path + "." + str(file_index)
    os.rename(file_path, new_file_path)
    return new_file_path


def read_configuration_file(path):
    """
    Read the configuration file and return a configuration object
    """
    with open(path, "r") as configuration_file:
        return json.load(configuration_file)


def create_redis_dispatcher_node(name):
    """
    Args:
        name(str): Name of the redis node
    Returns:
        dict: A dictionnary with the redis node configuration
    """
    return {
        "host": name,
        "port": 6379,
        "type": "redis"
    }


def create_minio_dispatcher_node(name):
    """
    Args:
        name(str): Name of the minio node
    Returns:
        dict: A dictionnary with the minio node configuration
    """
    return {
        "endpoint_url": "http://{:s}:9000/".format(name),
        "aws_access_key_id": "playcloud",
        "aws_secret_access_key": "playcloud",
        "type": "s3",
    }


def create_dispatcher_configuration(configuration):
    """
    Read the configuration file and create a coherent pyproxy's dispatcher.json file
    """
    nodes = int(configuration["storage"]["nodes"])
    dispatcher_configuration = {"providers":{}}
    make_node = create_redis_dispatcher_node
    if configuration["storage"]["type"] == "minio":
        make_node = create_minio_dispatcher_node
    if nodes == 1:
        name = "storage-node"
        dispatcher_configuration["providers"][name] = make_node(name)
    else:
        for index in range(1, nodes + 1):
            name = "storage-node-{:d}".format(index)
            dispatcher_configuration["providers"][name] = make_node(name)
    replication_factor = int(configuration["storage"].get("replication_factor", 3))
    dispatcher_configuration["replication_factor"] = replication_factor
    dispatcher_configuration["entanglement"] = configuration.get("entanglement", {})
    return dispatcher_configuration


def write_dispatcher_file(dispatcher_configuration):
    """
    Writes the new dispatcher file
    """
    if os.path.exists(PATH_TO_DISPATCHER_FILE):
        rename_existing_file(PATH_TO_DISPATCHER_FILE)
    # Write new dispatcher file
    json_dispatcher = json.dumps(dispatcher_configuration, indent=4, separators=(',', ': ')).strip()
    with open(PATH_TO_DISPATCHER_FILE, "w") as dispatcher_dump_file:
        dispatcher_dump_file.write(json_dispatcher)


def create_redis_compose_node(name):
    """
    Args:
        name(str): Name of the redis node
    Returns:
        dict: The service configuration for the redis node
    """
    return {
        "container_name": name,
        "image": "redis:3.2.8",
        "command": "redis-server --appendonly yes",
        "deploy": {
            "placement": {
                "constraints": ["node.role == worker"]
            }
        },
        "volumes": ["./volumes/{:s}/:/data/".format(name)]
    }

def create_minio_compose_node(name):
    """
    Args:
        name(str): Name of the minio node
    Returns:
        dict: The service configuration for the redis node
    """
    return {
        "container_name": name,
        "image": "minio/minio:latest",
        "command": "server /data",
        "environment": [
            "MINIO_ACCESS_KEY=playcloud",
            "MINIO_SECRET_KEY=playcloud"
        ],
        "volumes": ["./volumes/{:s}:/data/".format(name)]
    }


def create_docker_compose_configuration(configuration, scale=1):
    """
    Read the configuration file and create a coherent docker-compose file
    Args:
        configuration(dict): Configuration file
        scale(int): Number of instances of the proxy
    """
    nodes = int(configuration["storage"]["nodes"])

    compose_configuration = copy.deepcopy(BASIC_COMPOSE_CONFIGURATION)
    if os.path.exists(PATH_TO_DOCKER_COMPOSE_FILE):
        with open(PATH_TO_DOCKER_COMPOSE_FILE) as dc_file:
            compose_configuration = ruamel.yaml.round_trip_load(dc_file.read().strip(),
                                                                preserve_quotes=True)
    services_to_keep = ["coder", "load_balancer", "metadata", "proxy", "zoo1"]
    node_keys = [key for key in compose_configuration["services"] if key not in services_to_keep]
    make_node = create_redis_compose_node
    if scale <= 1:
        del compose_configuration["services"]["load_balancer"]
        compose_configuration["services"]["proxy"]["ports"] = ["3000:3000"]
    else:
        del compose_configuration["services"]["proxy"]["container_name"]
        compose_configuration["services"]["load_balancer"] = {
            "image": "dockercloud/haproxy:latest",
            "restart": "always",
            "volumes": ["/var/run/docker.sock:/var/run/docker.sock"],
            "deploy": {
                "mode": "global"
            },
            "depends_on": ["proxy"],
            "links": ["proxy"],
            "ports": ["3000:80"]
        }
        if not "deploy" in compose_configuration["services"]["proxy"]:
            compose_configuration["services"]["proxy"]["deploy"] = {}
        compose_configuration["services"]["proxy"]["deploy"]["replicas"] = scale
        compose_configuration["services"]["proxy"]["deploy"]["mode"] = "replicated"
        compose_configuration["services"]["proxy"]["ports"] = ["3000"]
    if configuration["storage"]["type"] == "minio":
        make_node = create_minio_compose_node
    for key in node_keys:
        del compose_configuration["services"][key]
    compose_configuration["services"]["proxy"]["depends_on"] = []
    if nodes == 1:
        container_name = "storage-node"
        compose_configuration["services"][container_name] = make_node(container_name)
        create_volume_directory(container_name)
        compose_configuration["services"]["proxy"]["depends_on"].append(container_name)
    else:
        for i in range(1, nodes + 1):
            container_name = "storage-node-{:d}".format(i)
            compose_configuration["services"][container_name] = make_node(container_name)
            create_volume_directory(container_name)
            compose_configuration["services"]["proxy"]["depends_on"].append(container_name)
    create_volume_directory("metadata")
    return compose_configuration


def create_docker_compose_configuration_for_production(configuration):
    """
    Read the configuration file and create a coherent docker-compose file
    """
    dev_compose_configuration = create_docker_compose_configuration(configuration)
    del dev_compose_configuration["services"]["proxy"]["build"]
    dev_compose_configuration["services"]["proxy"]["image"] = "dburihabwa/playcloud_proxy"
    if "coder" in dev_compose_configuration["services"]:
        del dev_compose_configuration["services"]["coder"]["build"]
        dev_compose_configuration["services"]["coder"]["image"] = "dburihabwa/playcloud_coder"
    if "load_balancer" in dev_compose_configuration["services"]:
        del dev_compose_configuration["services"]["load_balancer"]
    for service in dev_compose_configuration["services"].keys():
        if "depends_on" in dev_compose_configuration["services"][service]:
            del dev_compose_configuration["services"][service]["depends_on"]
        if service.startswith("storage-node"):
            del dev_compose_configuration["services"][service]["volumes"]
            del dev_compose_configuration["services"][service]["container_name"]
    return dev_compose_configuration


def write_docker_compose_file(compose_configuration, path):
    """
    Writes the new docker-compose file
    """
    # Check if docker-compose file already exists
    if os.path.exists(path):
        rename_existing_file(path)
    # Write new docker-compose file
    yaml_for_compose = ruamel.yaml.round_trip_dump(compose_configuration,
                                                   indent=4,
                                                   block_seq_indent=2,
                                                   explicit_start=True)
    with open(path, "w") as compose_dump_file:
        compose_dump_file.write(yaml_for_compose)


def write_docker_compose_file_for_dev(compose_configuration):
    """
    Writes to the given docker-compose content to PATH_TO_DOCKER_COMPOSE_FILE
    """
    write_docker_compose_file(compose_configuration, PATH_TO_DOCKER_COMPOSE_FILE)


def write_docker_compose_file_for_production(compose_configuration):
    """
    Writes to the given docker-compose content to PATH_TO_DOCKER_COMPOSE_PRODUCTION_FILE
    """
    write_docker_compose_file(compose_configuration, PATH_TO_DOCKER_COMPOSE_PRODUCTION_FILE)


def create_volume_directory(name):
    """
    Create a volume directory.
    Args:
        name(str): Name of the container and name of the volume directory
    Returns:
        str: Path of the directory
    Raises:
        EnvironmentError: If the volume directory cannot be created
    """
    if not os.path.exists(PATH_TO_VOLUMES_DIRECTORY):
        os.makedirs(PATH_TO_VOLUMES_DIRECTORY, mode=0775)
    if not os.path.isdir(PATH_TO_VOLUMES_DIRECTORY):
        raise EnvironmentError("{:s} is not a directory"
                               .format(PATH_TO_VOLUMES_DIRECTORY))

    volume_directory = os.path.join(PATH_TO_VOLUMES_DIRECTORY, name)

    if os.path.isdir(volume_directory):
        return volume_directory
    os.makedirs(volume_directory, mode=0775)
    if not os.path.exists(volume_directory):
        raise EnvironmentError("{:s} could not be created"
                               .format(volume_directory))
    return volume_directory


def set_coder_configuration(path_to_central_configuration):
    """
    Set the configuration of the coder based on the central configuration file.
    Args:
        path_to_central_configuration(str): Path to the central configuration file
    Returns:
        ConfigParser: The modified configuration
    """
    with open(path_to_central_configuration, "r") as handle:
        configuration = json.load(handle)
    parser = ConfigParser()
    with open(PATH_TO_CODER_CONFIGURATION, "r") as handle:
        parser.read_file(handle)
    parser.set("main", "splitter", "entanglement")
    entanglement_configuration = configuration.get("entanglement")
    parser.set("entanglement", "type", entanglement_configuration.get("type", "step"))
    code_configuration = entanglement_configuration.get("configuration", {"s": 1, "t": 10, "p": 3})
    parser.set("step", "s", str(code_configuration.get("s", 1)))
    parser.set("step", "t", str(code_configuration.get("t", 10)))
    parser.set("step", "p", str(code_configuration.get("p", 3)))
    parser.set("step", "prefetch", str(entanglement_configuration.get("prefetch", 3)))
    rename_existing_file(PATH_TO_CODER_CONFIGURATION)
    with open(PATH_TO_CODER_CONFIGURATION, "w") as handle:
        parser.write(handle)
    return parser


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(__file__,
                                     description=__DESCRIPTION)
    PARSER.add_argument("--scale",
                        type=int,
                        default=1,
                        help="The number of instances of the proxy that should be deployed")
    ARGS = PARSER.parse_args()
    PATH_TO_CONFIGURATION_FILE = os.path.join(os.path.dirname(__file__), "..", "configuration.json")
    GLOBAL_CONFIGURATION = read_configuration_file(PATH_TO_CONFIGURATION_FILE)
    DISPATCHER_CONFIGURATION = create_dispatcher_configuration(GLOBAL_CONFIGURATION)
    write_dispatcher_file(DISPATCHER_CONFIGURATION)
    COMPOSE_CONFIGURATION = create_docker_compose_configuration(GLOBAL_CONFIGURATION, scale=ARGS.scale)
    write_docker_compose_file_for_dev(COMPOSE_CONFIGURATION)
    COMPOSE_PRODUCTION_CONFIGURATION = create_docker_compose_configuration_for_production(GLOBAL_CONFIGURATION)
    write_docker_compose_file_for_production(COMPOSE_PRODUCTION_CONFIGURATION)
    set_coder_configuration(PATH_TO_CONFIGURATION_FILE)
