#! /usr/bin/env python
"""
A script that copies and modifies completion files outputed by apache bench and
sets the seconds to zero in order to be able to plot data from several files in
the same figure.
"""

import os
import sys

SECONDS_INDEX = 1

def get_seconds(line):
    """
    Extracts the "second" column from a line
    Args:
        line(str): The line to extract the second column from
    Returns:
        int: The value in the seconds column
    """
    return int(line.split("\t")[SECONDS_INDEX])

if __name__ == "__main__":
    FILES = [f for f in sys.argv[1:] if os.path.isfile(f)]
    for completion_file in FILES:
        smallest = sys.maxint
        largest = -sys.maxint - 1
        records = None
        with open(completion_file, "r") as lines:
            records = list(lines)
        data = sorted([r.strip() for r in records[1:]], key=get_seconds)
        smallest = get_seconds(data[0])
        corrected_lines = records[0]
        output_filename = os.path.join(os.path.dirname(completion_file),\
                                       "corrected_" +\
                                       os.path.basename(completion_file))
        with open(output_filename, "w") as output_file:
            output_file.write(records[0])
            for record in data:
                columns = record.split("\t")
                columns[SECONDS_INDEX] = str(int(columns[SECONDS_INDEX]) - smallest)
                new_line = "\t".join(columns)
                output_file.write(new_line + "\n")
