#! /usr/bin/env python
import json

from pyproxy.coder_client import CoderClient
from pyproxy.pyproxy.providers import Dispatcher

def reconstruct(path, index):
    with open("./dispatcher.json", "r") as handle:
        dispatcher_configuration = json.load(handle)
    dispatcher = Dispatcher(configuration=dispatcher_configuration)
    blocks = dispatcher.get(path)
    missing_block = blocks[index]
    coder = CoderClient()
    reconstructed = coder.reconstruct(path, [index])[index].data
    assert len(reconstructed) == len(missing_block)
    with open("/opt/missing_block.txt", "wb") as handle:
        handle.write(missing_block)
    with open("/opt/reconstructed.txt", "wb") as handle:
        handle.write(reconstructed)
    for i in xrange(len(reconstructed)):
        if reconstructed[i] != missing_block[i]:
            print "Difference at position {:d}".format(i)
            print reconstructed[:i]
            print "------------------------------------------------------------"
            print missing_block[:i]
            print "************************************************************"
            for j in xrange(i, len(reconstructed), 1):
                print "\t".join([reconstructed[j].encode("hex"), missing_block[j].encode("hex")])
            break
    assert reconstructed == missing_block

if __name__ == "__main__":
    reconstruct("TODO.txt", 0)
