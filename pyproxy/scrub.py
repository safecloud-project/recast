#! /usr/bin/env python
"""
A script that scans the database for blocks that have passed a given threshold
in order to delete their replicas.
"""
import argparse
import json
import logging
import os
import sys
import time

import pyproxy.metadata as mtdt
import pyproxy.safestore.providers.dispatcher as dsp
import pyproxy.utils as utils

__PROGRAM_DESCRIPTION = ("A script that scans the database looking for ",
                         "blocks that have passed a given threshold in ",
                         "order to delete their replicas")
LOGGER = None
KAZOO_CLIENT = None

def list_replicas_to_delete(pointers, host="metadata", port=6379):
    """
    List the blocks that match the given threshold
    Args:
        pointers(int): The minimum number of documents pointing to a block for
                       the block to be considered for scrubbing
        host(str, optional): The host metadata server
        port(int, optional): The port the metadata server is listening in
    Returns:
        list(MetaBlock): The list of blocks that have passed the threshold
    Raises:
        ValueError: if the pointers argument is not integer or is lower than 0
    """
    if not isinstance(pointers, int) or pointers < 0:
        raise ValueError("pointers must be an integer greater or equal to 0")
    LOGGER.debug("list_replicas_to_delete: pointers={:d}, host={:s}, port={:d}".format(pointers, host, port))
    files = mtdt.Files(host=host, port=port)
    blocks = files.get_blocks(files.list_blocks())
    LOGGER.debug("list_replicas_to_delete: loaded {:d} blocks to inspect".format(len(blocks)))
    consider_for_scrubbing = []
    for block in blocks:
        if files.has_been_entangled_enough(block.key, pointers) and \
           len(set(block.providers)) > 1:
            consider_for_scrubbing.append(block)
    return consider_for_scrubbing

def has_replicas(block):
    """
    Returns True if the block has replicas. False otherwise.
    Args:
        block(MetaBlock): The block to examine
    Returns:
        Bool: Result of the test
    """
    if not block or not isinstance(block, mtdt.MetaBlock):
        msg = "block must be a valid instance of MetaBlock"
        raise ValueError(msg)
    return len(block.providers) > 1


def list_replicas_out_of_window_to_delete(window, host="metadata", port=6379):
    """
    List the documents whose replicas can be deleted.
    Args:
        window(int): The number of most recent documents whose blocks need to be replicated
        host(str): Host of the metadata server
        port(int): Port number the metadata server is listening on
    Returns:
        list(MetaBlock): The list of blocks that are considered in the old generation and can be deleted
    Raises:
        ValueError: if window is not a number greater or equal to 0,
                    if host is not a valid string or
                    if port is not a number between 0 and 65535
    """
    if not isinstance(window, int) or window < 0:
        msg = "window must be an integer greater than 0"
        raise ValueError(msg)
    if not host or not isinstance(host, (str, unicode)):
        msg = "host argument must be a non-empty string"
        raise ValueError(msg)
    if not isinstance(port, int) or port < 0 or port > 65535:
        msg = "port argument must be an integer between 0 and 65535"
        raise ValueError(msg)
    metadata = mtdt.Files(host=host, port=port)
    blocks = metadata.get_blocks(metadata.list_blocks()[-window:])
    blocks_to_cleanup = [b for b in blocks if has_replicas(b)]
    return blocks_to_cleanup


def delete_block(block, host="metadata", port=6379):
    """
    Removes location of replicas from metadata.
    Args:
        block(MetaBlock): The block whose replicas need to be destroyed
        host(str, optional): The host metadata server
        port(int, optional): The port the metadata server is listening on
    Returns:
        bool: Whether the block was deleted
    Raises:
        ValueError: if the block is not a MetaBlock instance
    """
    if not block or not isinstance(block, mtdt.MetaBlock):
        raise ValueError("block argument must be a valid MetaBlock")
    LOGGER.debug("delete_block: block={:s}, host={:s}, port={:d}".format(block.key, host, port))
    files = mtdt.Files(host=host, port=port)
    filename = dsp.extract_path_from_key(block.key)
    with open("./dispatcher.json", "r") as handle:
        dispatcher_configuration = json.load(handle)
    dispatcher = dsp.Dispatcher(configuration=dispatcher_configuration)
    hostname = os.uname()[1]
    kazoo_resource = os.path.join("/", filename)
    kazoo_identifier = "repair-{:s}".format(hostname)
    with KAZOO_CLIENT.WriteLock(kazoo_resource, kazoo_identifier):
        metadata = files.get(filename)
        for metablock in metadata.blocks:
            if metablock.key == block.key:
                metablock.providers = metablock.providers[:1]
                for provider_name in metablock.providers[1:]:
                    dispatcher.providers[provider_name].delete(metablock.key)
                    LOGGER.debug("delete_block: Removed replica of {:s} from {:s}".format(metablock.key, provider_name))
                break
        files.put(metadata.path, metadata)
        return len(files.get_block(block.key).providers) == 1


def init_logger():
    """
    Returns:
        logger: Initialized logger
    """
    log_config = os.getenv("LOG_CONFIG", os.path.join(os.path.dirname(__file__), "logging.conf"))
    logging.config.fileConfig(log_config)

    logger = logging.getLogger("scrub")

    file_handler = logging.FileHandler("scrub.log")

    logger.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(prog="scrub.py",
                                     description=__PROGRAM_DESCRIPTION)
    PARSER.add_argument("-p",
                        "--pointers",
                        help=("The minimum number of documents pointing to a ",
                              "block for the block to be considered for",
                              "scrubbing"),
                        type=int,
                        default=3)
    PARSER.add_argument("-w",
                        "--window",
                        help="The size of the replication window",
                        type=int)
    PARSER.add_argument("--hostname",
                        help="The server hosting the metadata",
                        type=str,
                        default="metadata")

    PARSER.add_argument("--port",
                        help="The port exposed by the metadata server",
                        type=int,
                        default=6379)
    PARSER.add_argument("-i",
                        "--interval",
                        help="The time between two scrubbings in seconds",
                        type=int,
                        default=0)
    ARGS = PARSER.parse_args()
    LOGGER = init_logger()
    KAZOO_CLIENT = utils.init_zookeeper_client()
    if ARGS.interval:
        LOGGER.info("Going to start scrubbing with {:d} seconds interval".format(ARGS.interval))
        while True:
            try:
                time.sleep(ARGS.interval)
                LOGGER.info("Scrubbing database...")
                BLOCKS = None
                if ARGS.window:
                    BLOCKS = list_replicas_out_of_window_to_delete(ARGS.window)
                else:
                    BLOCKS = list_replicas_to_delete(ARGS.pointers)
                LOGGER.info("Found {:d} blocks to scrub".format(len(BLOCKS)))
                for BLOCK in BLOCKS:
                    LOGGER.debug("Looking at {:s}".format(BLOCK.key))
                    if delete_block(BLOCK):
                        LOGGER.info("Removed replicas of {:s}".format(BLOCK.key))
                    else:
                        LOGGER.error("Could not delete replicas of {:s}".format(BLOCK.key))
                LOGGER.info("Scrubbing finished")
            except (KeyboardInterrupt, SystemExit):
                LOGGER.info("Exiting")
                KAZOO_CLIENT.stop()
                sys.exit(0)
    else:
        LOGGER.info("Going to start scrubbing with {:d} seconds interval".format(ARGS.interval))
        LOGGER.info("Scrubbing database...")
        BLOCKS = None
        if ARGS.window:
            LOGGER.info("Looking for blocks out of the {:d} documents window...".format(ARGS.window))
            BLOCKS = list_replicas_out_of_window_to_delete(ARGS.window)
        else:
            LOGGER.info("Looking for blocks that have been pointed at at least {:d} times...".format(ARGS.pointers))
            BLOCKS = list_replicas_to_delete(ARGS.pointers)
        LOGGER.info("Found {:d} blocks to scrub".format(len(BLOCKS)))
        for BLOCK in BLOCKS:
            LOGGER.debug("Looking at {:s}".format(BLOCK.key))
            if delete_block(BLOCK):
                LOGGER.info("Removed replicas of {:s}".format(BLOCK.key))
            else:
                LOGGER.error("Could not delete replicas of {:s}".format(BLOCK.key))
        LOGGER.info("Scrubbing finished")
        LOGGER.info("Exiting")
        KAZOO_CLIENT.stop()
        sys.exit(0)
