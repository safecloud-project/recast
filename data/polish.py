#! /usr/bin/python

import os
import sys

SECONDS_INDEX = 1

def clean_line(line):
    return line.strip()

def get_seconds(line):
    return int(line.split("\t")[SECONDS_INDEX])

if __name__ == "__main__":
    files = filter(os.path.isfile, sys.argv[1:])
    for file in files:
        smallest = 0
        largest = -1
        with open(file, "r") as lines:
            records = list(lines)
            data = map(clean_line, records[1:])
            data = sorted(data, key=get_seconds)
            smallest = get_seconds(data[0])
            corrected_lines = records[0]
            output_filename = "corrected_" + file
            with open(output_filename, "w") as output_file:
                output_file.write(records[0])
                for record in data:
                    columns = record.split("\t")
                    columns[SECONDS_INDEX] = str(int(columns[SECONDS_INDEX]) - smallest)
                    new_line = "\t".join(columns)
                    output_file.write(new_line + "\n")
