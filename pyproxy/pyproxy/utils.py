"""
Utility methods
"""
import logging
import multiprocessing
import subprocess
import time

import kazoo.client

def get_threads_per_core():
    """
    Gets the number of threads per core from `lscpu` output.
    Returns:
        int: number of threads per core from `lscpu` output
    Raises:
        EnvironmentError: If the information cannot be found in the lscpu output
    """
    process = subprocess.Popen("lscpu", stdout=subprocess.PIPE)
    out, _ = process.communicate()
    for line in out.split("\n"):
        if line.startswith("Thread(s) per core:"):
            return int(line.split(":")[1])
    raise EnvironmentError("Could not read number of threads per core from lscpu output")

def get_max_threads():
    """
    Gets the number of threads that can run in parallel on the machine.
    Returns:
        int: number of threads that can run in parallel on the machine
    Raises:
        EnvironmentError: If the number of threads per core cannot be read
    """
    return multiprocessing.cpu_count() * get_threads_per_core()

def init_zookeeper_client(host="zoo1", port=2181, max_retries=5):
    """
    Tries to initialize the connection to zookeeper.
    Args:
        host(str, optional): zookeeper host
        port(int, optional): zookeeper port
        max_retries(int, optional): How many times should the connection
                                    establishment be retried
    Returns:
        kazoo.client.KazooClient: An initialized zookeeper client
    Raises:
        EnvironmentError: If the client cannot connect to zookeeper
    """
    zk_logger = logging.getLogger("zookeeper")
    zk_logger.info("initializing connection to zookeeper")
    hosts = "{:s}:{:d}".format(host, port)
    client = kazoo.client.KazooClient(hosts=hosts)
    backoff_in_seconds = 1
    tries = 0
    while tries < max_retries:
        try:
            zk_logger.info("Trying to connect to {:s}".format(hosts))
            client.start()
            if client.connected:
                zk_logger.info("Connected to zookeeper")
                return client
        except kazoo.handlers.threading.KazooTimeoutError:
            tries += 1
            backoff_in_seconds *= 2
            zk_logger.warn("Failed to connect to {:s}".format(hosts))
            zk_logger.warn("Waiting {:d} seconds to reconnect to {:s}"
                           .format(backoff_in_seconds, hosts))
            time.sleep(backoff_in_seconds)
    error_message = "Could not connect to {:s}".format(hosts)
    zk_logger.error(error_message)
    raise EnvironmentError(error_message)
