#! /usr/bin/env python
"""
A script that starts remote storage nodes
"""
import argparse
import os
import re
import subprocess
import threading

import configure

__SCRIPT_DESCRIPTION = """
A script that starts remote storage nodes
"""

PATH_TO_DISPATCHER_CONF = os.path.join(os.path.dirname(__file__),
                                       "..",
                                       "pyproxy/dispatcher.json")
MINIO_ENDPOINT_PATTERN = re.compile(r"^http://(.+):(\d+)/?$")


START_MINIO_TEMPLATE = ("ssh -o StrictHostKeyChecking=no -p {:d} {:s} " +
                        "docker ps -aq | xargs --no-run-if-empty docker rm -fv && " +
                        "docker pull minio/minio && " +
                        "docker run --detach=true --name {:s} " +
                        "--publish={:d}:{:d} " +
                        "-e 'MINIO_ACCESS_KEY={:s}' -e 'MINIO_SECRET_KEY={:s}' " +
                        "--volume ~/playcloud/volumes/{:s}:/data " +
                        "minio/minio server --address '0.0.0.0:9000' /data")
START_REDIS_TEMPLATE = ("ssh -o StrictHostKeyChecking=no -p {:d} {:s} " +
                        "docker ps -aq | xargs --no-run-if-empty docker rm -fv && " +
                        "docker pull redis:3.2.8 && " +
                        "docker run --detach=true --name {:s} " +
                        "--publish={:d}:{:d} " +
                        "--volume ~/playcloud/volumes/{:s}:/data " +
                        "redis")

class MinioStarter(threading.Thread):
    """
    Remotely starts a minio node through SSH
    """
    def __init__(self, provider, provider_conf, ssh_port=22):
        """
        Args:
            provider(str): Name of the storage node
            provider_conf(dict): Configuration of the provider
            ssh_port(int): Port number used by the SSH server on host
        """
        super(MinioStarter, self).__init__()
        endpoint_url = provider_conf["endpoint_url"]
        groups = MINIO_ENDPOINT_PATTERN.match(endpoint_url).groups()
        minio_host = groups[0]
        minio_port = int(groups[1])
        minio_aws_access_key_id = provider_conf["aws_access_key_id"]
        minio_aws_secret_access_key = provider_conf["aws_secret_access_key"]
        self.host = minio_host
        self.command = START_MINIO_TEMPLATE.format(ssh_port,
                                                   minio_host,
                                                   provider,
                                                   minio_port,
                                                   minio_port,
                                                   minio_aws_access_key_id,
                                                   minio_aws_secret_access_key,
                                                   provider)

    def run(self):
        """
        Remotely starts a minio node through SSH
        Returns:
            int: Return code of the SSH command
        """
        ret = subprocess.call(self.command.split())
        if ret == 0:
            print "Successfully started node {:s}".format(self.host)
        else:
            print "Startup of node {:s} ended with {:d} return code".format(self.host, ret)
        return ret

class RedisStarter(threading.Thread):
    """
    Remotely starts a redis node through SSH
    """
    def __init__(self, provider, provider_conf, ssh_port=22):
        """
        Args:
            provider(str): Name of the storage node
            provider_conf(dict): Configuration of the provider
            ssh_port(int): Port number used by the SSH server on host
        """
        super(RedisStarter, self).__init__()
        redis_host = provider_conf["host"]
        redis_port = int(provider_conf["port"])
        self.host = redis_host
        self.command = START_REDIS_TEMPLATE.format(ssh_port,
                                                   redis_host,
                                                   provider,
                                                   redis_port,
                                                   redis_port,
                                                   provider)
    def run(self):
        """
        Remotely starts a redis node through SSH
        Returns:
            int: Return code of the SSH command
        """
        ret = subprocess.call(self.command.split())
        if ret == 0:
            print "Successfully started node {:s}".format(self.host)
        else:
            print "Startup of node {:s} ended with {:d} return code".format(self.host, ret)
        return ret

def start(configuration):
    """
    Traverses the dispatcher configuration and starts the various storage nodes
    Args:
        configuration(dict): Dispatcher configuration
    """
    providers = configuration["providers"]
    starters = []
    for provider in providers:
        provider_type = providers[provider]["type"]
        if provider_type == "s3":
            starters.append(MinioStarter(provider, providers[provider]))
        elif provider_type == "redis":
            starters.append(MinioStarter(provider, providers[provider]))
        else:
            raise RuntimeError("Unsupported type of provider")
    for starter in starters:
        starter.start()
    for starter in starters:
        starter.join()

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(__file__, description=__SCRIPT_DESCRIPTION)
    ARGS = PARSER.parse_args()
    CONFIGURATION = configure.read_configuration_file(PATH_TO_DISPATCHER_CONF)
    start(CONFIGURATION)
