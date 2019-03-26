#!/usr/bin/env python2
"""
A script to perform offline entanglement
"""
import argparse
import errno
import json
import logging
import os
import uuid

import numpy

import pyproxy.coder.playcloud_pb2
import pyproxy.coder.entangled_driver


DEFAULT_CONFIGURATION_FILE = os.path.join(os.path.basename(__file__), "./dispatcher.json")


class Storage(object):
    def __init__(self, base_directory):
        self.directory = base_directory
        self.blocks = set(list_all_files(self.directory))

    def register_block(self, path):
        self.blocks.add(path)

    def get_random_blocks(self, pointers):
        keys = list(self.blocks)
        indices = Storage.normal_selection(pointers, len(keys))
        strips = []
        for index in indices:
            strip = pyproxy.coder.playcloud_pb2.Strip()
            strip.id = keys[index]
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

    def get_block(self, path):
        if path not in self.blocks:
            raise ValueError("{:s} is not known")
        with open(os.path.join(self.directory, path), "r") as handle:
            return handle.read()

    def get(self, path):
        return self.get_block(path)

    def put(self, path, data):
        with open(os.path.join(self.directory, path), "w") as handle:
            handle.write(data)
        self.register_block(path)


def mkdir_p(path):
    """
    Create a directory in similar way to bash's mkdir -p
    :param path: Path of the new directory
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


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
    anchors_directory = os.path.join(storage.directory, ".anchors")
    mkdir_p(anchors_directory)
    while pointers_available < pointers_needed:
        file_path = os.path.join(anchors_directory, str(uuid.uuid4()))
        storage.put(file_path, os.urandom(1024 * 1024))
        pointers_available = len(storage.blocks)
    seed_logger.info("Seeding done")


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
            result.append(os.path.join(path, name))
    return result


def main():
    """
    Main routine
    """
    parser = argparse.ArgumentParser(__file__, description="Perform offline entanglement")
    parser.add_argument("input", type=str, help="Input directory with the files to entangle")
    parser.add_argument("output", type=str, help="Output directory to store the entangled files")
    parser.add_argument("-c", "--configuration", type=str, help="Configuration file", default=DEFAULT_CONFIGURATION_FILE)

    args = parser.parse_args()
    if not os.path.exists(args.output):
        raise ValueError("output directory cannot be found: {:s}".format(args.output))
    if not os.path.isdir(args.output):
        raise ValueError("output directory does not point to directory: {:s}".format(args.output))
    if not os.access(args.output, os.W_OK):
        raise ValueError("output directory is not writeable: {:s}")

    source = Storage(args.output)
    seed_system("dispatcher.json", source)
    driver = pyproxy.coder.entangled_driver.StepEntangler(source, 1, 10, 3)

    files = list_all_files(args.input)
    for input_file in files:
        name = input_file.replace(args.input, "")
        with open(input_file, "r") as handle:
            data = handle.read()
        parities = driver.encode(data)
        for index, parity in enumerate(parities):
            block_name = "{:s}-{:d}".format(name, index)
            source.put(block_name, parity)


if __name__ == '__main__':
    main()
