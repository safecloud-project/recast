#! /usr/bin/env python
"""
A script that periodically scans the storage nodes and checks the integrity of
the blocks they host
"""
import hashlib
import logging
import json
import os
import sys

from pyproxy.coder_client import CoderClient
from pyproxy.coding_utils import reconstruct_as_pointer
from pyproxy.files import compute_block_key, convert_binary_to_hex_digest, Files
from pyproxy.safestore.providers.dispatcher import Dispatcher, extract_index_from_key, extract_path_from_key

PATH_TO_DISPATCHER_CONFIGURATION = os.path.join(os.path.dirname(__file__),
                                                "dispatcher.json")

LOGGER = logging.getLogger("repair.py")
LOGGER.setLevel(logging.INFO)
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setLevel(logging.ERROR)
LOGGER.addHandler(CONSOLE_HANDLER)
RECONSTRUCT_QUEUE = {}

def get_dispatcher_configuration(path_to_configuration=PATH_TO_DISPATCHER_CONFIGURATION):
    """
    Reads the dispatcher's configuration
    Args:
        path(str): Path to the dispatcher's configuration file
    Returns:
        dict: The dispatcher's configuration
    """
    with open(path_to_configuration, "r") as handle:
        dispatcher_configuration = json.load(handle)
    return dispatcher_configuration

def get_erasure_threshold():
    """
    Computes the erasure threshold of the STeP configuration
    Returns:
        int: The erasure threshold for STeP (P - S)
    """
    entanglement_configuration = get_dispatcher_configuration()["entanglement"]["configuration"]
    source_blocks = entanglement_configuration["s"]
    parities = entanglement_configuration["p"]
    return parities - source_blocks

if __name__ == "__main__":
    DISPATCHER = Dispatcher(get_dispatcher_configuration())
    FILES = Files(host="metadata")
    # List blocks
    BLOCKS = FILES.get_blocks(FILES.list_blocks())
    # For each block
    for block in BLOCKS:
        LOGGER.debug("Looking at block {:s}".format(block.key))
    #   For each replica of the block
        providers = list(set(block.providers))
        for index, provider_name in enumerate(providers):
            LOGGER.debug("Looking at replica of {:s} on {:s}".format(block.key, provider_name))
    #       Download replica
            replica = DISPATCHER.providers[provider_name].get(block.key)
            computed_checksum = None
            if replica:
                computed_checksum = hashlib.sha256(replica).digest()
    #       If the replica does not match its checksum
            if not replica or computed_checksum != block.checksum:
                repaired = False
                if not replica:
                    LOGGER.warn("Could not load replica of {:s} on {:s}\n".format(block.key, provider_name))
                if computed_checksum:
                    LOGGER.warn("Replica of {:s} on {:s} does not match expected checksum (actual = {:s}, expected = {:s})\n".format(block.key, provider_name, convert_binary_to_hex_digest(computed_checksum), convert_binary_to_hex_digest(block.checksum)))
    #           Look for sane replicas
                other_providers = list(set(providers).difference(set([provider_name])))
                if other_providers:
                    for other_provider in other_providers:
                        candidate_replica = DISPATCHER.providers[other_provider].get(block.key)
                        if not candidate_replica:
                            continue
                        candidate_checksum = hashlib.sha256(candidate_replica).digest()
                        if candidate_checksum == block.checksum:
    #                       Copy the new valid replica
                            DISPATCHER.providers[provider_name].put(candidate_replica, block.key)
                            repaired = True
                            break
    #           Otherwise
                if not repaired:
    #               Queue the block for reconstruction
                    sys.stderr.write("Replica of {:s} on {:s} must be reconstructed\n".format(block.key, provider_name))
                    path = extract_path_from_key(block.key)
                    index = extract_index_from_key(block.key)
                    q = RECONSTRUCT_QUEUE.get(path, set())
                    q.add(index)
                    RECONSTRUCT_QUEUE[path] = set(q)
            else:
                LOGGER.debug("Replica of {:s} on {:s} is OK".format(block.key, provider_name))

    ERASURES_THRESHOLD = get_erasure_threshold()
    CLIENT = CoderClient()
    for path in RECONSTRUCT_QUEUE:
        indices_to_reconstruct = list(RECONSTRUCT_QUEUE.get(path))
        if len(indices_to_reconstruct) <= ERASURES_THRESHOLD:
            LOGGER.info("Should repair {:s}".format(indices_to_reconstruct))
            reconstructed_blocks = CLIENT.reconstruct(path, indices_to_reconstruct)
            for index in reconstructed_blocks:
                reconstructed_block = reconstructed_blocks[index].data
                metablock = FILES.get_block(compute_block_key(path, index))
                for provider_name in set(metablock.providers):
                    DISPATCHER.providers[provider_name].put(reconstructed_block,
                                                            metablock.key)
        else:
            #FIXME order of blocks to reach e erasures than do RS reconstuction
            for index in indices_to_reconstruct:
                reconstructed_block = reconstruct_as_pointer(path, index)
                metablock = FILES.get_block(compute_block_key(path, index))
                for provider_name in set(metablock.providers):
                    DISPATCHER.providers[provider_name].put(reconstructed_block,
                                                            metablock.key)
