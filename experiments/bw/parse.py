#! /usr/bin/env python
import json
import os

import numpy

RESULTS_DIRECTORY = os.path.join(os.path.dirname(__file__), "results")

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

def parse_run(run, stats_filter=None):
    """
    Parses the results of a run looking at the start and end network snapshot
    producing a dictionary with the differences.
    Args:
        run(str): Path to the run directory
        stats_filter(list(str), optional): List of stats to include in the result
                                           If none are mentioned then all results
                                           are returned
    Returns:
        dict: A dictionary with the difference
    """
    check_if_directory_is_explorable(run)
    start_path = os.path.join(run, "bw-start-snapshot.json")
    with open(start_path, "r") as handle:
        start = json.load(handle)
    stop_path = os.path.join(run, "bw-stop-snapshot.json")
    with open(stop_path, "r") as handle:
        stop = json.load(handle)
    delta = {}
    for container in stop:
        container_stats = {}
        for stat in stop[container]:
            if stats_filter and stat not in stats_filter:
                continue
            difference = stop[container][stat] - start[container][stat]
            container_stats[stat] = difference
        delta[container] = container_stats
    return delta

def parse():
    run_directories = list_in_directory(RESULTS_DIRECTORY, filters=[os.path.isdir])
    if not run_directories:
        return {}
    results = []
    # Filter for stats we are interested in
    stats_to_keep = ["rx_bytes", "tx_bytes"]
    for run_directory in run_directories:
        results.append(parse_run(run_directory, stats_filter=stats_to_keep))
    # Compile results
    containers = results[0].keys()
    compiled_results = {}
    for container in containers:
        container_stats = {}
        for stat in stats_to_keep:
            values = []
            for result in results:
                values.append([result[container][stat]])
            container_stats[stat] = {
                "min": numpy.min(values),
                "max": numpy.max(values),
                "average": numpy.mean(values),
                "median": numpy.median(values),
                "stdev": numpy.std(values)
            }
        compiled_results[container] = container_stats
    return compiled_results

if __name__ == "__main__":
    print json.dumps(parse(), indent=4)
