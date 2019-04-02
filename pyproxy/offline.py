#! /usr/bin/env python2
"""
A script to perform offline entanglement
"""
import argparse
import errno
import json
import logging
import os
import shutil

import numpy

import pyproxy.coder.playcloud_pb2
import pyproxy.coder.entangled_driver
import pyproxy.metadata

DEFAULT_CONFIGURATION_FILE = os.path.join(os.path.dirname(__file__), "./dispatcher.json")


def mkdir_p(path):
    """
    Recursively creates a directory tree.
    Shamelessly copied from https://stackoverflow.com/a/600612
    Args:
        path(str): Tree to create
    Returns:
        bool: True if the directory was created, False otherwise
    Raises:
        OSError: If an error occurs during the creation of the directories
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
    return os.path.isdir(path)


def clean_path(path):
    """
    Removes extra space and leading slash at the beginning of a path
    Args:
        path(str): Path to clean
    Returns:
        str: A cleaned up path
    """
    clean_key = path.strip()
    if clean_key[0] == '/':
        clean_key = clean_key[1:]
    return clean_key

def list_all_files(directory):
    """
    Traverses a directory (and its subdirectories) and lists all the regular files encountered
    :param directory: Base directory to explore
    :return: list(str): The list of files found
    """
    if not os.path.exists(directory):
        raise ValueError("Could not find directory {:s}".format(directory))
    if not os.path.isdir(directory):
        raise ValueError("{:s} is not a directory".format(directory))
    result = []
    for path, _, files in os.walk(directory):
        for name in files:
            full_path = os.path.join(path, name)
            if os.path.isfile(full_path) and not os.path.islink(full_path):
                result.append(full_path)
    return sorted(result)


def get_document_path(base_directory, full_path):
    """
    Extracts the necessary part of the path to the document
    Args:
        base_directory(str):
        full_path(str):
    Returns:
        str: The path to the document in the system
    """
    return clean_path(full_path.replace(base_directory, ""))


class Storage(object):
    """
    On disk storage and pointer source for random entanglement
    """

    def __init__(self, base_directory):
        self.disk = Disk(base_directory)
        self.blocks = set(list_all_files(self.disk.root_folder))

    def get_random_blocks(self, pointers):
        """

        :param pointers:
        :return:
        """
        keys = list(self.blocks)
        indices = Storage.normal_selection(pointers, len(keys))
        strips = []
        for index in indices:
            strip = pyproxy.coder.playcloud_pb2.Strip()
            strip.id = keys[index]
            strip.data = self.disk.get(strip.id)
            strips.append(strip)
        return strips

    @staticmethod
    def normal_selection(pointers, available_pointers, std=1000):
        """
        Select pointer indices using normal distribution
        Args:
            pointers(int): Number of pointers
            available_pointers(int): Number of blocks
            std(int, optional): Standard deviation (defaults to 1000)
        Returns:
            list(int): A list of unique indices ranging from 0 to (n - 1) selected
                       using normal distribution
        """
        selected = []
        if pointers >= available_pointers:
            return [element for element in xrange(available_pointers)]
        std = min(available_pointers, std)
        difference = available_pointers - pointers
        if difference < pointers:
            selected = [index for index in xrange(available_pointers)]
            while len(selected) > pointers:
                index = int(round(numpy.random.normal(len(selected), min(std, len(selected)))))
                if index < 0 or index >= len(selected):  # Checking that we are withtin bounds
                    continue
                selected.pop(index)
            return selected
        while len(selected) < pointers:
            index = int(round(numpy.random.normal(available_pointers, std)))
            if index < 0 or index >= available_pointers:  # Checking that we are withtin bounds
                continue
            if index in selected:
                continue
            selected.append(index)
        return selected

    def get(self, path):
        """
        Returns a block from storage
        Args:
            path(str): Path to the block
        Returns:
            bytes: Block data
        """
        if path not in self.blocks:
            raise ValueError("{:s} is not known")
        return self.disk.get(path)

    def get_block(self, path):
        """
        Alias to Storage.get that matches random block source signature
        Args:
            path(str): Path to the block
        Returns:
            bytes: Block data
        """
        return self.get(path)

    def put(self, path, data):
        """
        Stores a block under a path
        Args:
            path(str): Path to the block
            data(bytes): Block data
        """
        self.disk.put(path, data)
        self.blocks.add(path)


class Disk(object):
    """
    A storage provider for playcloud that stores blocks on the disk
    """

    def __init__(self, folder="/data"):
        self.root_folder = folder

    def get(self, key):
        """
        Retrieves a block from the disk. Returns None if nothing found
        Args:
            key(str): Path to the block from the filsystem
        Returns:
            (byte|None): The data or None if the block does not exist
        """
        clean_key = clean_path(key)
        path = os.path.join(self.root_folder, clean_key)
        if not os.path.isfile(path):
            return None
        with open(path, "rb") as handle:
            data = handle.read()
        return data

    def put(self, key, value):
        """
        Saves a block on the disk
        Args:
            key(str): Path to the block from the file system
            value(bytes): The data to store
        """
        clean_key = clean_path(key)
        path = os.path.join(self.root_folder, clean_key)
        mkdir_p(os.path.dirname(path))
        with open(path, "wb") as handle:
            handle.write(value)

    def delete(self, key):
        """
        Deletes a block from the filesytem
        Args:
            key(str): Path to the block from the filsystem
        Returns:
            bool: True if the block was deleted, False otherwise.
        """
        clean_key = clean_path(key)
        path = os.path.join(self.root_folder, clean_key)
        if not os.path.exists(path):
            return False
        os.unlink(path)
        return not os.path.exists(path)

    def clear(self):
        """
        Removes all blocks from the filesystem
        Returns:
            bool: True if all data was deleted, False otherwise
        """
        for entry in os.listdir(self.root_folder):
            path = os.path.join(self.root_folder, entry)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

        return len(os.listdir(self.root_folder)) == 0


def seed_system(configuration_file, storage):
    """
    Provides the system with anchor blocks to ensure that the first entangled documents are recoverable
    :param configuration_file: Path to the configuration file that describes the STeP configuration
    :param storage: Object that holds all the data and that will host the new anchor files
    """
    seed_logger = logging.getLogger("seed")
    seed_logger.info("Checking if the system needs to be seeded")
    with open(configuration_file, "r") as handle:
        configuration = json.load(handle)
    if "entanglement" not in configuration or "type" not in configuration["entanglement"] or \
            configuration["entanglement"]["type"] != "step":
        seed_logger.info("No need to see the system")
        return
    pointers_needed = configuration["entanglement"]["configuration"]["t"]
    pointers_available = len(storage.blocks)
    anchors_directory = ".recast/anchors"
    mkdir_p(os.path.join(storage.disk.root_folder, anchors_directory))
    difference = pointers_needed - pointers_available
    for index in xrange(difference):
        file_path = os.path.join(anchors_directory, "anchor-{:d}".format(index))
        storage.put(file_path, pyproxy.coder.entangled_driver.pad("", 1024 * 1024))
    seed_logger.info("Seeding done")


def main():
    """
    Main routine
    """
    #FIXME load possible configuration from disk
    parser = argparse.ArgumentParser(__file__, description="Perform offline entanglement")
    parser.add_argument("input", type=str, help="Input directory with the files to entangle")
    parser.add_argument("output", type=str, help="Output directory to store the entangled files")
    parser.add_argument("-c", "--configuration", type=str, help="Configuration file",
                        default=DEFAULT_CONFIGURATION_FILE)

    args = parser.parse_args()

    if not os.path.exists(args.output):
        raise ValueError("output directory cannot be found: {:s}".format(args.output))
    if not os.path.isdir(args.output):
        raise ValueError("output directory does not point to directory: {:s}".format(args.output))
    if not os.access(args.output, os.W_OK):
        raise ValueError("output directory is not writeable: {:s}")

    settings_directory = os.path.join(args.output, ".recast")
    mkdir_p(settings_directory)
    source = Storage(args.output)
    seed_system(args.configuration, source)
    driver = pyproxy.coder.entangled_driver.StepEntangler(source, 1, 10, 3)

    files = list_all_files(args.input)
    metadata = {}
    for input_file in files:
        name = get_document_path(args.input, input_file)
        with open(input_file, "rb") as handle:
            data = handle.read()
        parities = driver.encode(data)
        entangling_blocks = ["{:s}-{:d}".format(ep[0], ep[1]) for ep in pyproxy.metadata.extract_entanglement_data(parities[0])]
        file_metadata = {
            "entangling_blocks": entangling_blocks,
            "blocks": []
        }

        for index, parity in enumerate(parities):
            block_name = "{:s}-{:d}".format(name, index)
            source.put(block_name, parity)
            file_metadata["blocks"].append(block_name)
        metadata[name] = file_metadata
    with open(os.path.join(settings_directory, "metadata.json"), "w") as handle:
        json.dump(metadata, handle)

if __name__ == '__main__':
    main()
