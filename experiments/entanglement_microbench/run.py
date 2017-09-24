#! /usr/bin/env python
import argparse
import errno
import os
import sys
import time

sys.path.append(os.path.abspath('../../pyproxy'))
import pyproxy.coder.entangled_driver as entangled_driver

with open("./header.pack", "rb") as handle:
    FRAGMENT_HEADER = entangled_driver.FragmentHeader(handle.read())

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

def encode(source, s, t, p, runs):
    entangler = entangled_driver.StepEntangler(source, s, t, p, ec_type="liberasurecode_rs_vand")
    data = os.urandom(ARGS.block_size)
    results = []
    for _ in xrange(runs):
        start = time.clock()
        entangler.encode(data)
        end = time.clock()
        elapsed = end - start
        results.append(elapsed)
    return results

def decode(source, s, t, p, runs):
    entangler = entangled_driver.StepEntangler(source, s, t, p, ec_type="liberasurecode_rs_vand")
    data = os.urandom(ARGS.block_size)
    encoded = entangler.encode(data)
    results = []
    for _ in xrange(runs):
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

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(__file__, description="")
    PARSER.add_argument("-s", "--source", help="Number of source blocks", type=int, required=True)
    PARSER.add_argument("-t", "--pointers", help="Number of pointer blocks", type=int, required=True)
    PARSER.add_argument("-p", "--parities", help="Number of parity blocks", type=int, required=True)
    PARSER.add_argument("-b", "--block-size", help="Size of the block in bytes", type=int, required=True)
    PARSER.add_argument("-r", "--repetitions", help="Number of times the operation must be performed", type=int, required=True)
    ARGS = PARSER.parse_args()
    SOURCE = BogusSource(ARGS.block_size)

    RUNS = 5
    RESULTS_DIRECTORY = os.path.join("results",
                                     "conf-{:d}-{:d}-{:d}".format(ARGS.source, ARGS.pointers, ARGS.parities))
    
    for run in xrange(1, 6, 1):
        RUN_RESULTS_PATH = os.path.join(RESULTS_DIRECTORY, str(ARGS.block_size), str(run))
        mkdir_p(RUN_RESULTS_PATH)
        NUMBERS = encode(SOURCE, ARGS.source, ARGS.pointers, ARGS.parities, ARGS.repetitions)
        with open(os.path.join(RUN_RESULTS_PATH, "encode.txt"), "w") as handle:
            handle.write("\n".join([str(number) for number in NUMBERS]))
        NUMBERS = decode(SOURCE, ARGS.source, ARGS.pointers, ARGS.parities, ARGS.repetitions)
        with open(os.path.join(RUN_RESULTS_PATH, "decode.txt"), "w") as handle:
            handle.write("\n".join([str(number) for number in NUMBERS]))