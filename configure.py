#! /usr/bin/env python
"""
A script that reads configuration.json and produces a matching configuration files for docker-compose and the pyproxy.
"""
import copy
import json
import os

import pyaml

BASIC_COMPOSE_CONFIGURATION = {
    "version": "\"2\"",
    "services": {
        "coder": {
            "container_name": "coder",
            "hostname": "coder",
            "build": "./pycoder",
            "environment": ["sec_measure=confd", "splitter=ec", "k=10", "m=4", "type=jerasure_rs_cauchy"],
            "env_file": ["./erasure.env"]
        },
        "proxy": {
            "container_name": "proxy",
            "hostname": "proxy",
            "build": "./pyproxy",
            "ports": ["3000:8000"],
            "env_file": ["./erasure.env"]
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

def create_dispatcher_configuration(configuration):
    """
    Read the configuration file and create a coherent pyproxy's dispatcher.json file
    """
    nodes = int(configuration["storage"]["nodes"])
    dispatcher_configuration = {"providers":[]}
    for i in range(1, nodes + 1):
        provider = {
            "type": "redis",
            "host": "redis" + str(i),
            "port": 6379,
        }
        dispatcher_configuration["providers"].append(provider)
    return dispatcher_configuration

def write_dispatcher_file(dispatcher_configuration):
    """
    Writes the new dispatcher file
    """
    # Check if dispatcher file already exists
    PATH_TO_DISPATCHER_FILE = os.path.join(os.path.dirname(__file__), "pyproxy", "dispatcher.json")
    if os.path.exists(PATH_TO_DISPATCHER_FILE):
        rename_existing_file(PATH_TO_DISPATCHER_FILE)
    # Write new dispatcher file
    json_dispatcher = json.dumps(dispatcher_configuration, indent=4, separators=(',', ': ')).strip()
    with open(PATH_TO_DISPATCHER_FILE, "w") as dispatcher_dump_file:
        dispatcher_dump_file.write(json_dispatcher)



def create_docker_compose_configuration(configuration):
    """
    Read the configuration file and create a coherent docker-compose file
    """
    nodes = int(configuration["storage"]["nodes"])
    compose_configuration = copy.deepcopy(BASIC_COMPOSE_CONFIGURATION)
    for i in range(1, nodes + 1):
        container_name = "redis" + str(i)
        compose_configuration["services"][container_name] = {
            "container_name": container_name,
            "image": "redis"
        }
    return compose_configuration

def write_docker_compose_file(compose_configuration):
    """
    Writes the new docker-compose file
    """
    # Check if docker-compose file already exists
    PATH_TO_DOCKER_COMPOSE_FILE = os.path.join(os.path.dirname(__file__), "docker-compose.yml")
    if os.path.exists(PATH_TO_DOCKER_COMPOSE_FILE):
        rename_existing_file(PATH_TO_DOCKER_COMPOSE_FILE)
    # Write new docker-compose file
    yaml_for_compose = pyaml.dump(compose_configuration).strip()
    with open(PATH_TO_DOCKER_COMPOSE_FILE, "w") as compose_dump_file:
        compose_dump_file.write(yaml_for_compose)

if __name__ == "__main__":
    PATH_TO_CONFIGURATION_FILE = os.path.join(os.path.dirname(__file__), "configuration.json")
    global_configuration = read_configuration_file(PATH_TO_CONFIGURATION_FILE)
    dispatcher_configuration = create_dispatcher_configuration(global_configuration)
    write_dispatcher_file(dispatcher_configuration)
    compose_configuration = create_docker_compose_configuration(global_configuration)
    write_docker_compose_file(compose_configuration)
