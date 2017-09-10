#! /usr/bin/env python
"""
A script that tries to use recursive reconstruction to recover a block
"""
from pyproxy.coding_utils import reconstruct_as_pointer

if __name__ == "__main__":
    PATH = "README.md"
    INDEX = 0
    reconstruct_as_pointer(PATH, INDEX)
