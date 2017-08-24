#! /usr/bin/env python
"""
A script that periodically scans the storage nodes and checks the integrity of
the blocks they host
"""
import json
import hashlib
import sys

from pyproxy.coder_client import CoderClient
from pyproxy.files import convert_binary_to_hex_digest, Files
from pyproxy.safestore.providers.dispatcher import Dispatcher, extract_index_from_key, extract_path_from_key


if __name__ == "__main__":
    with open("./dispatcher.json", "r") as handle:
        DISPATCHER = Dispatcher(json.load(handle))
    FILES = Files(host="metadata")
    # List blocks
    BLOCKS = FILES.get_blocks(FILES.list_blocks())
    # For each block
    for block in BLOCKS:
        print "Looking at block {:s}".format(block.key)
    #   For each replica of the block
        for index, provider_name in enumerate(block.providers):
            print "Looking at replica of {:s} on {:s}".format(block.key, provider_name)
    #       Download replica
            replica = DISPATCHER.providers[provider_name].get(block.key)
            computed_checksum = None
            if replica:
                computed_checksum = hashlib.sha256(replica).digest()
    #       If the replica does not match its checksum
            if not replica or computed_checksum != block.checksum:
                repaired = False
                if not replica:
                    sys.stderr.write("Could not load replica of {:s} on {:s}\n".format(block.key, provider_name))
                if computed_checksum:
                    sys.stderr.write("Replica of {:s} on {:s} does not match expected checksum (actual = {:s}, expected = {:s})\n".format(block.key, provider_name, convert_binary_to_hex_digest(computed_checksum), convert_binary_to_hex_digest(block.checksum)))
    #           Look for sane replicas
                other_providers = list(set(block.providers).difference(set([provider_name])))
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
    #               Reconstruct the block
                    sys.stderr.write("Replica of {:s} on {:s} must be reconstructed\n".format(block.key, provider_name))
                    client = CoderClient()
                    path = extract_path_from_key(block.key)
                    index = extract_index_from_key(block.key)
                    reconstructed_block = client.reconstruct(path, [index])[index].data
                    DISPATCHER.providers[provider_name].put(reconstructed_block, block.key)
            else:
                print "Replica of {:s} on {:s} is OK".format(block.key, provider_name)
