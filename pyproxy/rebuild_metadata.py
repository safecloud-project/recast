#! /usr/bin/env python
"""
A script that rebuilds playcloud metadata in a given redis database
"""
import argparse
import hashlib
import json
import os

import pyproxy.safestore.providers.dispatcher as d
import pyproxy.metadata as metadata


DEFAULT_DISPATCHER_CONFIGURATION = os.path.join(os.path.dirname(__file__), "dispatcher.json")

def rebuild(configuration_path):
    """
    Args:
        configuration_path(str): Path to the dispatcher configuration file
    Returns:
        list(metadata.MetaDocument): The rebuilt metadata information
    """
    if not configuration_path or not isinstance(configuration_path, str):
        raise ValueError("configuration_path argument must be a non-empty string")
    with open(configuration_path, "r") as handle:
        dispatcher_configuration = json.load(handle)
    dispatcher = d.Dispatcher(configuration=dispatcher_configuration)

    documents = {}
    for provider_name in dispatcher.providers:
        provider = dispatcher.providers[provider_name]
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
                document.blocks.append(metablock)
            metablock.providers = list(set(metablock.providers + [provider_name]))
            documents[document_name] = document
    return documents

def write_metadata(host, port, documents):
    """
    Args:
        host(str): Host of the metadata server to write to
        port(int): Port number the metadata server is listening on
        documents(dict(str, metadata.MetaDocument)): MetaDocuments to insert
    """
    if not host or not isinstance(host, str):
        raise ValueError("argument host must be a non-empty string")
    if not isinstance(port, int) or port < 0 or port > 65535:
        raise ValueError("argument port must be an integer in a range of 0 to 65535")
    if not isinstance(documents, dict):
        raise ValueError("argument documents must be a dictionary")
    metadata_server = metadata.Files(host=host, port=port)
    documents_grouped_by_pointers = {}
    for path in documents:
        doc = documents[path]
        number_of_pointers = len(doc.entangling_blocks)
        group = documents_grouped_by_pointers.get(number_of_pointers, [])
        group.append(doc)
        documents_grouped_by_pointers[number_of_pointers] = group

    print "Formed {:d} groups of documents based on the number of pointers".format(len(documents_grouped_by_pointers))
    inserted = []
    for number_of_pointers in sorted(documents_grouped_by_pointers):
        documents_group = documents_grouped_by_pointers[number_of_pointers]
        print "Grouped {:d} documents with {:d} pointers".format(len(documents_group), number_of_pointers)
        while documents_group:
            last_inserts = []
            current_documents_set = set([unicode(doc.path) for doc in documents_group])
            print "####################################################################################################"
            print "{:d} Documents left in the current document set".format(len(current_documents_set))
            print "####################################################################################################"
            for document in documents_group:
                print document.path
                # If any of the entangling blocks of the current document have not been inserted yet, we move on to the next one
                documents_pointed = set([eb[0] for eb in document.entangling_blocks])
                print "************************************************************************************************"
                must_abort = False
                for pointed_d in documents_pointed:
                    if pointed_d in current_documents_set:
                        print "{:s} is in the current document set".format(pointed_d)
                        must_abort = True
                        break
                if must_abort:
                    continue
                metadata_server.put(document.path, document)
                last_inserts.append(document)
                print "inserted document {:s}".format(document.path)
            for inserted in last_inserts:
                documents_group.remove(inserted)

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(__file__, description="A script to rebuild the metadata in a different server")
    PARSER.add_argument("--host", type=str, required=True, help="Host of the new metadata server")
    PARSER.add_argument("--port", type=int, required=True, help="Port of the new metadata server")
    PARSER.add_argument("--conf", type=str, help="Path to the dispatcher configuration", default=DEFAULT_DISPATCHER_CONFIGURATION)

    ARGS = PARSER.parse_args()

    DOCUMENTS_METADATA = rebuild(ARGS.conf)
    write_metadata(ARGS.host, ARGS.port, DOCUMENTS_METADATA)
