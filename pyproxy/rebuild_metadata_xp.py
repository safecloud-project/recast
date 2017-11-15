#! /usr/bin/env python
"""
A script that rebuilds playcloud metadata in a given redis database
"""
import argparse
import hashlib
import logging
import json
import os
import random
import sys

import pyproxy.safestore.providers.dispatcher as d
import pyproxy.metadata as metadata

DEFAULT_DISPATCHER_CONFIGURATION = os.path.join(os.path.dirname(__file__), "dispatcher.json")


def rebuild_node(provider, provider_name, documents=None):
    """
    Rebuilds metadata by reading data from a given storage node.
    Args:
        provider(Provider): Storage provider
        provider_name(str): Name of the provider
        documents(str, metadata.MetaDocument): The current list of MetaDocuments
    Returns:
        dict(str, metadata.MetaDocument): The list of MetaDocuments built from the database
    """
    if not provider:
        raise ValueError("provider argument must be a valid Provider with a list and a get method")
    if not provider_name or not isinstance(provider_name, (str, unicode)):
        raise ValueError("provider_name argument must be a non empty string")
    documents = documents or {}
    for block_id in provider.list():
        document_name = d.extract_path_from_key(block_id)
        document = documents.get(document_name, None)
        if not document:
            document = metadata.MetaDocument(document_name)
        metablock = None
        for a_metablock in document.blocks:
            if a_metablock.key == block_id:
                metablock = a_metablock
                break
        if not metablock:
            data = provider.get(block_id)
            checksum = hashlib.sha256(data).digest()
            if not document.entangling_blocks:
                document.entangling_blocks = metadata.extract_entanglement_data(data)
            if not document.original_size:
                document.original_size = metadata.extract_document_size(data)
            metablock = metadata.MetaBlock(block_id, checksum=checksum, size=len(data))
            document.blocks = sorted((document.blocks + [metablock]), key=lambda b: b.key)
        metablock.providers = list(set(metablock.providers + [provider_name]))
        documents[document_name] = document
    return documents


def count_blocks(documents):
    """
    Counts the total number of blocks in a list of documents
    Args:
        documents(metadata.MetaDocument): The list of documents
    Returns:
        int: Size of the list
    """
    return sum([len(doc.blocks) for doc in documents])

def compute_block_completion(block, original_block):
    """
    Computes the amount of accuracy of a reconstructed MetaBlock against the original MetaBlock
    :param block:
    :param original_block:
    Returns:
        float: Completion level
    """
    if block.key == original_block.key and block.providers and \
       block.checksum == original_block.checksum and block.size == original_block.size:
        return 1.0
    return 0.0

def rebuild(configuration_path):
    """
    Rebuilds metadata by data from the storage nodes
    Args:
        configuration_path(str): Path to the dispatcher configuration file
    Returns:
        list(metadata.MetaDocument): The rebuilt metadata information
    """
    if not configuration_path or not isinstance(configuration_path, str):
        raise ValueError("configuration_path argument must be a non-empty string")
    with open(configuration_path, "r") as handle:
        dispatcher_configuration = json.load(handle)


    metadata_server = metadata.Files()
    original_documents = metadata_server.get_files(metadata_server.keys())
    total_documents = len(original_documents)
    total_blocks = count_blocks(original_documents)
    dispatcher = d.Dispatcher(configuration=dispatcher_configuration)
    completion = {
        "files": [0],
        "blocks": [0],
        "block_accuracy": [0]
    }
    documents = {}
    provider_names = dispatcher.providers.keys()
    random.shuffle(provider_names)
    sys.stderr.write("total_blocks: {:d}\n".format(total_blocks))
    for provider_name in provider_names:
        blocks_score = 0.0
        provider = dispatcher.providers[provider_name]
        documents = rebuild_node(provider, provider_name, documents=documents)
        completion["files"].append(float(len(documents)) / total_documents)
        current_block_count = count_blocks(documents.values())
        sys.stderr.write("{:d} blocks read\n".format(current_block_count))
        completion["blocks"].append(float(current_block_count / total_blocks))
        for document in documents.values():
            original_blocks = {b.key: b for b in metadata_server.get(document.path).blocks}
            for block in document.blocks:
                blocks_score += compute_block_completion(block, original_blocks[block.key])
        completion["block_accuracy"].append(float(blocks_score) / total_blocks)
    return completion

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(__file__, description="A script to rebuild the metadata in a different server")
    PARSER.add_argument("--conf", type=str, help="Path to the dispatcher configuration",
                        default=DEFAULT_DISPATCHER_CONFIGURATION)

    logging.getLogger("botocore.vendored.requests.packages.urllib3.connectionpool").setLevel(logging.WARNING)

    ARGS = PARSER.parse_args()
    RESULTS = rebuild(ARGS.conf)
    print json.dumps(RESULTS, indent=4, sort_keys=True)
