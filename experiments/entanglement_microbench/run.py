#! /usr/bin/env python
import argparse
import errno
import json
import os
import sys
import time

sys.path.append(os.path.abspath('../../pyproxy'))
import pyproxy.coder.entangled_driver as entangled_driver

with open("./header.pack", "rb") as FILE_HANDLE:
    FRAGMENT_HEADER = entangled_driver.FragmentHeader(FILE_HANDLE.read())

#TODO add a fragment header to the bogus script

class BogusStrip(object):
    HEADER_DELIMITER = chr(29)
    def __init__(self, id, header, data, document_size):
        self.id = id
        self.document_size = document_size
        block_header = entangled_driver.serialize_entanglement_header(header)
        self.data = block_header + entangled_driver.HEADER_DELIMITER + \
                    str(document_size) + entangled_driver.HEADER_DELIMITER + \
                    FRAGMENT_HEADER.pack() + data

class BogusSource(object):
    def __init__(self, block_size):
        self.block_size = block_size
        self.default_block = "\0" * self.block_size

    def get_block(self, path, index, reconstruct_if_missing=True):
        return BogusStrip("{:s}-{:d}".format(path, index), [], self.default_block[:], self.block_size)

    def get_random_blocks(self, number_of_blocks):
        random_blocks = []
        for _ in xrange(number_of_blocks):
            block = BogusStrip("path-00", [], self.default_block[:], self.block_size)
            random_blocks.append(block)
        return random_blocks

def encode(source, s, t, p, block_size, repetitions):
    entangler = entangled_driver.StepEntangler(source, s, t, p, ec_type="liberasurecode_rs_vand")
    data = os.urandom(block_size)
    results = []
    for _ in xrange(repetitions):
        start = time.clock()
        entangler.encode(data)
        end = time.clock()
        elapsed = end - start
        results.append(elapsed)
    return results

def decode(source, s, t, p, block_size, repetitions):
    entangler = entangled_driver.StepEntangler(source, s, t, p, ec_type="liberasurecode_rs_vand")
    data = os.urandom(block_size)
    encoded = entangler.encode(data)
    results = []
    for _ in xrange(repetitions):
        start = time.clock()
        entangler.decode(encoded)
        end = time.clock()
        elapsed = end - start
        results.append(elapsed)
    return results

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def run_once(source_blocks, pointers, parities, block_size, repetitions, run_number):
    source = BogusSource(block_size)
    results_directory = os.path.join("results",
                                     "conf-{:d}-{:d}-{:d}".format(source_blocks, pointers, parities))

    run_results_path = os.path.join(results_directory, str(block_size), str(run_number))
    mkdir_p(run_results_path)
    numbers = encode(source, source_blocks, pointers, parities, block_size, repetitions)
    with open(os.path.join(run_results_path, "encode.txt"), "w") as handle:
        handle.write("\n".join([str(number) for number in numbers]))
    numbers = decode(source, source_blocks, pointers, parities, block_size, repetitions)
    with open(os.path.join(run_results_path, "decode.txt"), "w") as handle:
        handle.write("\n".join([str(number) for number in numbers]))

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(__file__, description="")
    PARSER.add_argument("configuration_file", help="Number of source blocks", type=str)
    ARGS = PARSER.parse_args()
    CONFIGURATION_FILE = ARGS.configuration_file
    with open(CONFIGURATION_FILE, "r") as file_handle:
        PARAMETERS = json.load(file_handle)

    RUNS = PARAMETERS["runs"]
    for run in xrange(1, RUNS + 1, 1):
        for bs in PARAMETERS["block_sizes"]:
            for configuration in PARAMETERS["configurations"]:
                run_once(configuration["s"],
                         configuration["t"],
                         configuration["p"],
                         bs,
                         PARAMETERS["repetitions"],
                         run)
