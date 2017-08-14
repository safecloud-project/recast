#! /usr/bin/env python
"""
A script that scans the database for blocks that have passed a given threshold
in order to delete their replicas.
"""
# TODO: Actually delete the replicas data from the providers
import argparse
import os
import sys

from safestore.providers.dispatcher import extract_path_from_key
from proxy import init_zookeeper_client
from pyproxy.files import Files, MetaBlock

__PROGRAM_DESCRIPTION = ("A script that scans the database looking for ",
                         "blocks that have passed a given threshold in ",
                         "order to delete their replicas")


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
    files = Files(host=host, port=port)
    blocks = files.list_blocks()
    consider_for_scrubbing = []
    for block in blocks:
        if files.has_been_entangled_enough(block, pointers) and \
           len(set(block.providers)) > 1:
            consider_for_scrubbing.append(files.get_block(block))
    return consider_for_scrubbing


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
    if not block or not isinstance(block, MetaBlock):
        raise ValueError("block argument must be a valid MetaBlock")
    files = Files(host=host, port=port)
    kazoo_client = init_zookeeper_client()
    filename = extract_path_from_key(block.key)
    hostname = os.uname()[1]
    kazoo_resource = os.path.join("/", filename)
    kazoo_identifier = "repair-{:s}".format(hostname)
    with kazoo_client.WriteLock(kazoo_resource, kazoo_identifier):
        metadata = files.get(filename)
        for metablock in metadata.blocks:
            if metablock.key == block.key:
                metablock.providers = metablock.providers_to_free[:1]
                break
        files.put(metadata.path, metadata)
        return len(files.get_block(block.key).providers) == 1


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
    PARSER.add_argument("-s",
                        "--hostname",
                        help="The server hosting the metadata",
                        type=str,
                        default="metadata")

    PARSER.add_argument("-p",
                        "--port",
                        help="The port exposed by the metadata server",
                        type=int,
                        default=6379)
    ARGS = PARSER.parse_args()
    BLOCKS = list_replicas_to_delete(ARGS.pointers)
    for BLOCK in BLOCKS:
        if delete_block(BLOCK):
            print "Removed replicas of {:s}".format(BLOCK.key)
        else:
            sys.stderr.write("Could not delete replicas of {:s}\n".format(BLOCK.key))
