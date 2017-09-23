#! /usr/bin/env python
import os

import numpy

def check_if_directory_is_explorable(base):
    if not isinstance(base, str) or not base:
        raise ValueError("base argument must be a non empty string")
    if not os.path.isdir(base):
        error_message = "{:s} must be an existing directory".format(base)
        raise ValueError(error_message)
    if not os.access(base, os.X_OK):
        error_message = "user must have exuction rights on directory {:s}".format(base)
        raise ValueError("{:s} must grant x permission")


def list_in_directory(base, filters=None):
    """
    Args:
        base(str): Path to a directory
        filters(list(function), optional):
    Returns:
        list(str): A list of, potentiallly filtered, entries in the directory
    """
    check_if_directory_is_explorable(base)
    entries = []
    for entry in os.listdir(base):
        full_path = os.path.join(base, entry)
        if filters:
            index = 0
            for predicate in filters:
                if not predicate(full_path):
                    break
                index += 1
            if index < len(filters):
                continue
        entries.append(full_path)
    return entries
    
def parse_file(memory_file):
    """
    """
    with open(memory_file, "r") as handle:
        lines = handle.readlines()
    for line in lines:
        if "../../volumes/metadata/dump.rdb" in line:
            return int(line.replace("../../volumes/metadata/dump.rdb", ""))
    raise RuntimeError("Could not find used_memory line in text")
    

def parse_run(run_directory):
    memory_files = list_in_directory(run_directory, filters=[os.path.isfile])
    numbers = {}
    for memory_file in memory_files:
        number_of_documents = int(os.path.basename(memory_file).replace("-info_memory.txt", ""))
        numbers[number_of_documents] = parse_file(memory_file)
    return numbers

def parse_config(config_directory):
    run_directories = list_in_directory(config_directory, filters=[os.path.isdir])
    runs = []
    for run_directory in run_directories:
        runs.append(parse_run(run_directory))
    number_of_documents = sorted(runs[0].keys())
    config_result = {}
    for increment in number_of_documents:
        numbers = [run[increment] for run in runs]
        config_result[increment] = {
            "min": numpy.min(numbers),
            "max": numpy.max(numbers),
            "average": numpy.average(numbers),
            "std": numpy.std(numbers),
            "median": numpy.median(numbers),
            "numbers": numbers
        }
    return config_result

def parse(base_directory):
    config_directories = list_in_directory(base_directory, filters=[os.path.isdir])
    results = {}
    for config_directory in config_directories:
        config_name = os.path.basename(config_directory)
        results[config_name] = parse_config(config_directory)
    return results
    
def format_results(results):
    configs = sorted(results.keys())
    lines = []
    lines.append(",".join(["documents"] + configs))
    increments = results[results.keys()[0]].keys()
    for increment in sorted(increments):
        line = []
        line.append(str(increment))
        for config in configs:
            line.append(str(results[config][increment]["average"]))
        lines.append(",".join(line))
    return "\n".join(lines)
    

if __name__ == "__main__":
    print format_results(parse("./results/"))