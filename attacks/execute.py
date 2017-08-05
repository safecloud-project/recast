#! /usr/bin/env python
"""
A script that performs an attack planned by the `censor.py` script
"""
import json
import os
import re

from pyproxy.files import Files
from pyproxy.safestore.providers.redis_provider import RedisProvider

BLOCKS_TO_ERASE_DIR = os.path.join(os.path.dirname(__file__), "blocks-to-erase")

PATH_TO_DISPATCHER_CONFIGURATION = os.path.join(os.path.dirname(__file__),
                                                "dispatcher.json")

BLOCK_COMPILED_PATTERN = re.compile(r"^(.+)-(\d+)$")

def list_files():
    """
    Files to destroy and the blocks that need to be deleted to insure its
    destruction.
    Returns:
        dict(str, list(str)): Files to destroy and the blocks that need to be
                              deleted to insure its destruction
    """
    files = {}
    for filename in os.listdir(BLOCKS_TO_ERASE_DIR):
        file_path = os.path.join(BLOCKS_TO_ERASE_DIR, filename)
        if not os.path.isfile(file_path):
            continue
        with open(file_path, "r") as handle:
            blocks = [line.strip() for line in handle.readlines()]
        files[filename] = blocks
    return files

def split_block_info(block):
    """
    Args:
        block(str): Block name
    Returns:
        (str, int): Tuple with the name of the file and block index
    """
    tokens = BLOCK_COMPILED_PATTERN.findall(block)[0]
    return (tokens[0], int(tokens[1]))

def delete_block(block_key):
    """
    Returns the list of providers where the file is stored
    Args:
        block(str): The block whose replicas we are trying to locate
    Returns:
        int: The number of replicas of the block that were deleted
    """
    files = Files(host="metadata")
    filename, index = split_block_info(block_key)
    metafile = files.get(filename)
    metablock = None
    for block in metafile.blocks:
        _, b_index = split_block_info(block.key)
        if b_index == index:
            metablock = block
            break
    provider_names = set(metablock.providers)
    with open(PATH_TO_DISPATCHER_CONFIGURATION, "r") as handle:
        providers_configuration = json.loads(handle.read()).get("providers", [])
    deletion_counter = 0
    for name in providers_configuration:
        if name in provider_names:
            configuration = providers_configuration[name]
            provider = RedisProvider(configuration=configuration)
            print "Trying to delete {:s} from storage node {:s}".format(metablock.key, name)
            if provider.delete(metablock.key):
                deletion_counter += 1
                print "SUCCESS: Deleted {:s} from storage node {:s}".format(metablock.key, name)
            else:
                print "FAILURE: Could not delete {:s} from storage node {:s}".format(metablock.key,
                                                                                     name)
    return deletion_counter

if __name__ == "__main__":
    FILES_AND_BLOCKS_TO_ERASE = list_files()
    for f in FILES_AND_BLOCKS_TO_ERASE:
        BLOCKS = FILES_AND_BLOCKS_TO_ERASE[f]
        for BLOCK in BLOCKS:
            delete_block(BLOCK)