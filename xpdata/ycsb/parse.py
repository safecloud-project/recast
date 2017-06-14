#! /usr/bin/env python
"""
A script to parse ycsb run files
"""
import argparse
import json
import os
import re
import shlex
import subprocess


OPERATIONS = [
    "READ"
]

def get_float(line):
    """
    Args:
        line(str): The line to parse
    Returns:
        float: The floating point number on the line
    """
    compiled_pattern = re.compile(r"^.*,.*,\s+((\d+)([\.|,](\d+))?)")
    average_latency = float(compiled_pattern.findall(line)[0][0])
    return average_latency

def get_operation_data(run_file, operation):
    """
    Returns operation data from a run file.
    Args:
        run_file(str): Path to the run file
        operation(str): Type of operation
    Returns:
        dict(str, int): Operation data read from the run file
    """
    lines = get_tagged_lines(run_file, operation)
    data = {}
    for line in lines:
        if line.find("AverageLatency") != -1:
            data["average_latency"] = get_float(line)
        elif line.find("MinLatency") != -1:
            data["min_latency"] = get_float(line)
        elif line.find("MaxLatency") != -1:
            data["max_latency"] = get_float(line)
        elif line.find("Operations") != -1:
            data["operations"] = int(get_float(line))
        elif line.find("95thPercentileLatency") != -1:
            data["95th_percentile_latency"] = get_float(line)
        elif line.find("99thPercentileLatency") != -1:
            data["99th_percentile_latency"] = get_float(line)
    return data

def get_tagged_lines(run_file, tag):
    """
    Filter the lines out of a file that are prefixed by a given tag.
    Args:
        run_file(str): Path to the run file
        tag(str): The tag to look out for
    Returns:
        list(str): The list of tagged lines
    """
    tags = []
    compiled_pattern = re.compile(r"^\[{}\]".format(tag))
    with open(run_file) as lines:
        for line in lines:
            tags_found = compiled_pattern.findall(line)
            if tags_found:
                tags.append(line.strip())
    return tags

def list_run_files(base_directory):
    """
    Returns the list of run files located in base_directory or any of its subfolder.
    Args:
        base_directory(str): Base directory to search from
    Returns:
        list(str): A list of files that match run files
    """
    if not os.path.isdir(base_directory):
        raise RuntimeError("{} is not a directory".format(base_directory))
    command = shlex.split("find {} -mindepth 1 -type f -iname \"run.txt\"".format(base_directory))
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    files = [line.strip() for line in process.stdout.read().split("\n")]
    files = [f for f in files if os.path.isfile(f)]
    return files


if __name__ == "__main__":
    ARG_PARSER = argparse.ArgumentParser(description="A script to parse ycsb run files")
    ARG_PARSER.add_argument("base_directory",
                            help="Root folder for db_bench results", type=str)
    ARGS = ARG_PARSER.parse_args()
    DATA_DIRECTORY = ARGS.base_directory
    RUN_FILES = list_run_files(DATA_DIRECTORY)
    RECORDS = {}
    for rf in RUN_FILES:
        RECORDS[rf] = {}
        for op in OPERATIONS:
            RECORDS[rf][op] = get_operation_data(rf, op)
    print json.dumps(RECORDS, indent=4, sort_keys=True)
