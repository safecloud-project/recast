#! /usr/bin/env python
"""
A script that periodically scans the storage nodes and checks the integrity of
the blocks they host
"""
import argparse
import hashlib
import logging
import json
import os
import time

from pyproxy.coding_utils import reconstruct_as_pointer, reconstruct_with_RS
from pyproxy.metadata import compute_block_key, convert_binary_to_hex_digest, Files
from pyproxy.safestore.providers.dispatcher import Dispatcher, extract_index_from_key, extract_path_from_key

PATH_TO_DISPATCHER_CONFIGURATION = os.path.join(os.path.dirname(__file__),
                                                "dispatcher.json")
DAEMON_INTERVAL_IN_SECONDS = 10 * 60

LOGGER = logging.getLogger("repair.py")
LOGGER.setLevel(logging.INFO)
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setLevel(logging.INFO)
LOGGER.addHandler(CONSOLE_HANDLER)

#TODO: Order blocks reconstruction lookingfor dependencies between them
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

def audit():
    """
    Downloads and checks the integrity of the blocks stored on the storage nodes.
    Failing blocks that cannot be recovered by copying from a replica are grouped
    by documents and added to a queue returned by the function.
    Returns:
        dict(str, set(int)): Documents and the indices of the blocks that need
                              to be reconstructed
    """
    reconstruction_needed = []
    dispatcher = Dispatcher(get_dispatcher_configuration())
    files = Files(host="metadata")
    # List blocks
    blocks = files.get_blocks(files.list_blocks())
    # For each block
    for block in blocks:
        LOGGER.debug("Looking at block {:s}".format(block.key))
    #   For each replica of the block
        providers = list(set(block.providers))
        for provider_name in providers:
            LOGGER.debug("Looking at replica of {:s} on {:s}".format(block.key, provider_name))
    #       Download replica
            replica = dispatcher.providers[provider_name].get(block.key)
            computed_checksum = None
            if replica:
                computed_checksum = hashlib.sha256(replica).digest()
    #       If the replica does not match its checksum
            if not replica or computed_checksum != block.checksum:
                repaired = False
                if not replica:
                    LOGGER.warn("Could not load replica of {:s} on {:s}".format(block.key, provider_name))
                if computed_checksum:
                    LOGGER.warn("Replica of {:s} on {:s} does not match expected checksum (actual = {:s}, expected = {:s})".format(block.key, provider_name, convert_binary_to_hex_digest(computed_checksum), convert_binary_to_hex_digest(block.checksum)))
    #           Look for sane replicas
                other_providers = list(set(providers).difference(set([provider_name])))
                if other_providers:
                    for other_provider in other_providers:
                        candidate_replica = dispatcher.providers[other_provider].get(block.key)
                        if not candidate_replica:
                            continue
                        candidate_checksum = hashlib.sha256(candidate_replica).digest()
                        if candidate_checksum == block.checksum:
    #                       Copy the new valid replica
                            dispatcher.providers[provider_name].put(candidate_replica, block.key)
                            repaired = True
                            break
    #           Otherwise
                if not repaired:
    #               Queue the block for reconstruction
                    LOGGER.warn("Replica of {:s} on {:s} must be reconstructed".format(block.key, provider_name))
                    reconstruction_needed.append(block.key)
            else:
                LOGGER.debug("Replica of {:s} on {:s} is OK".format(block.key, provider_name))
    return group_blocks_by_path(reconstruction_needed)

def group_blocks_by_path(block_keys):
    """
    Groups the block indices by document paths
    Args:
        block_keys(list(str)): Keys of the blocks to repair
    Returns:
        dict(path, set(int)): The indices of the blocks grouped by document path
    """
    if not isinstance(block_keys, list):
        raise ValueError("block_keys argument must be a list")
    groups = {}
    for key in block_keys:
        if not isinstance(key, str):
            raise ValueError("elements of block_keys argument must be of type string")
        path = extract_path_from_key(key)
        index = extract_index_from_key(key)
        indices = groups.get(path, set())
        indices.add(index)
        groups[path] = indices
    return groups

def repair(path, indices):
    """
    Repairs one or multiple blocks of a document
    Args:
        path(str): Path to the document
        indices(list(int)): Indices of the blocks to retrieve
    """
    if not isinstance(path, str) or not path:
        raise ValueError("Argument path must be a non-empty string")
    if not isinstance(indices, list):
        raise ValueError("Argument indices must be list")
    if not indices:
        return
    for index, index_to_reconstruct in enumerate(indices):
        if not isinstance(index_to_reconstruct, int):
            error_message = "indices[{:d}] is not an integer".format(index)
            raise ValueError(error_message)
    erasures_threshold = get_erasure_threshold()
    dispatcher = Dispatcher(get_dispatcher_configuration())
    files = Files()
    if len(indices) <= erasures_threshold:
        reconstructed_blocks = reconstruct_with_RS(path, indices)
        for index in reconstructed_blocks:
            reconstructed_block = reconstructed_blocks[index]
            metablock = files.get_block(compute_block_key(path, index))
            for provider_name in set(metablock.providers):
                dispatcher.providers[provider_name].put(reconstructed_block,
                                                        metablock.key)
    else:
        #FIXME order of blocks to reach e erasures than do RS reconstuction
        indices.sort()
        while len(indices) > erasures_threshold:
            index = indices.pop(0)
            reconstructed_block = reconstruct_as_pointer(path, index)
            metablock = files.get_block(compute_block_key(path, index))
            for provider_name in set(metablock.providers):
                dispatcher.providers[provider_name].put(reconstructed_block,
                                                        metablock.key)
        reconstructed_blocks = reconstruct_with_RS(path, indices)
        for index in reconstructed_blocks:
            reconstructed_block = reconstructed_blocks[index]
            metablock = files.get_block(compute_block_key(path, index))
            for provider_name in set(metablock.providers):
                dispatcher.providers[provider_name].put(reconstructed_block,
                                                        metablock.key)

def run_audit_and_repair():
    """
    Audits the data nodes and repairs the blocks if possible
    """
    LOGGER.info("Starting audit and repair")
    reconstruction_queue = audit()
    for document_path in reconstruction_queue:
        indices_to_reconstruct = list(reconstruction_queue.get(document_path))
        repair(document_path, indices_to_reconstruct)
    LOGGER.info("Finishing audit and repair")

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(__file__, description="A script that repairs lost or corrupted blocks")
    PARSER.add_argument("-d",
                        "--daemon",
                        help="Start the script as a daemon",
                        action="store_true")
    PARSER.add_argument("key", nargs="*")
    ARGS = PARSER.parse_args()
    if ARGS.daemon:
        LOGGER.info("Starting the repair daemon auditing every {:d} seconds".format(DAEMON_INTERVAL_IN_SECONDS))
        while True:
            time.sleep(DAEMON_INTERVAL_IN_SECONDS)
            run_audit_and_repair()
    elif ARGS.key:
        RECONSTRUCTION_QUEUE = group_blocks_by_path(ARGS.key)
        for path_to_repair in RECONSTRUCTION_QUEUE:
            indices_to_repair = list(RECONSTRUCTION_QUEUE.get(path_to_repair))
            repair(path_to_repair, indices_to_repair)
    else:
        run_audit_and_repair()
