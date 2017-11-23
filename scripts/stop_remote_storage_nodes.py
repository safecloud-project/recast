#! /usr/bin/env python
"""
A script that stops remote storage nodes
"""
import argparse
import os
import re
import subprocess
import threading

import configure

__SCRIPT_DESCRIPTION = """
A script that stops remote storage nodes
"""

PATH_TO_DISPATCHER_CONF = os.path.join(os.path.dirname(__file__),
                                       "..",
                                       "pyproxy/dispatcher.json")
MINIO_ENDPOINT_PATTERN = re.compile(r"^http://(.+):(\d+)/?$")


STOP_CONTAINER_TEMPLATE = ("ssh -o StrictHostKeyChecking=no -p {:d} {:s} " +
                           "docker ps -aq | xargs --no-run-if-empty docker rm -fv")

class MinioStopper(threading.Thread):
    """
    Remotely stops a minio node through SSH
    """
    def __init__(self, provider_conf, ssh_port=22):
        """
        Args:
            provider_conf(dict): Configuration of the provider
            ssh_port(int): Port number used by the SSH server on host
        """
        super(MinioStopper, self,).__init__()
        endpoint_url = provider_conf["endpoint_url"]
        groups = MINIO_ENDPOINT_PATTERN.match(endpoint_url).groups()
        minio_host = groups[0]
        self.host = minio_host
        self.command = STOP_CONTAINER_TEMPLATE.format(ssh_port, minio_host)

    def run(self):
        """
        Remotely stops a minio node through SSH
        Returns:
            int: Return code of the SSH command
        """
        ret = subprocess.call(self.command.split())
        if ret == 0:
            print "Successfully stopped node {:s}".format(self.host)
        else:
            print "Shutdown of node {:s} ended with {:d} return code".format(self.host, ret)
        return ret

class RedisStopper(threading.Thread):
    """
    Remotely stops a redis node through SSH
    """
    def __init__(self, provider_conf, ssh_port=22):
        """
        Args:
            provider_conf(dict): Configuration of the provider
            ssh_port(int): Port number used by the SSH server on host
        """
        super(RedisStopper, self,).__init__()
        redis_host = provider_conf["host"]
        self.host = redis_host
        self.command = STOP_CONTAINER_TEMPLATE.format(ssh_port, redis_host)

    def run(self):
        """
        Remotely stops a redis node through SSH
        Returns:
            int: Return code of the SSH command
        """
        ret = subprocess.call(self.command.split())
        if ret == 0:
            print "Successfully stopped node {:s}".format(self.host)
        else:
            print "Shutdown of node {:s} ended with {:d} return code".format(self.host, ret)
        return ret


def start(configuration):
    """
    Traverses the dispatcher configuration and stops the various storage nodes
    Args:
        configuration(dict): Dispatcher configuration
    """
    providers = configuration["providers"]
    stoppers = []
    for provider in providers:
        provider_type = providers[provider]["type"]
        if provider_type == "s3":
            stoppers.append(MinioStopper(providers[provider]))
        elif provider_type == "redis":
            stoppers.append(RedisStopper(providers[provider]))
        else:
            raise RuntimeError("Unsupported type of provider")
    for stopper in stoppers:
        stopper.start()
    for stopper in stoppers:
        stopper.join()

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(__file__, description=__SCRIPT_DESCRIPTION)
    ARGS = PARSER.parse_args()
    CONFIGURATION = configure.read_configuration_file(PATH_TO_DISPATCHER_CONF)
    start(CONFIGURATION)
