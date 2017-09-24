#! /usr/bin/env python
import argparse
import json
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
    
def parse_result_file(result_file):
    with open(result_file, "r") as handle:
        latencies = [float(line) for line in handle.readlines()]
    return {
        "min": numpy.min(latencies),
        "max": numpy.max(latencies),
        "average": numpy.mean(latencies),
        "median": numpy.median(latencies),
        "std": numpy.std(latencies),
        "count": len(latencies)
    }

def parse_run(run_directory):
    return {
        "encode": parse_result_file(os.path.join(run_directory, "encode.txt")),
        "decode": parse_result_file(os.path.join(run_directory, "decode.txt"))
    }

def parse_payload(payload_directory):
    run_directories = list_in_directory(payload_directory, filters=[os.path.isdir])
    results = {}
    for run_directory in run_directories:
        run_number = os.path.basename(run_directory)
        results[run_number] = parse_run(run_directory)
    return {
        "encode": {
            "min": numpy.mean([results[run]["encode"]["min"] for run in results.keys()]),
            "max": numpy.mean([results[run]["encode"]["max"] for run in results.keys()]),
            "average": numpy.mean([results[run]["encode"]["average"] for run in results.keys()]),
            "std": numpy.mean([results[run]["encode"]["std"] for run in results.keys()])
        },
        "decode": {
            "min": numpy.mean([results[run]["decode"]["min"] for run in results.keys()]),
            "max": numpy.mean([results[run]["decode"]["max"] for run in results.keys()]),
            "average": numpy.mean([results[run]["decode"]["average"] for run in results.keys()]),
            "std": numpy.mean([results[run]["decode"]["std"] for run in results.keys()])
        }
    }

def parse_config(config_directory):
    payload_directories = list_in_directory(config_directory, filters=[os.path.isdir])
    results = {}
    for payload_directory in payload_directories:
        payload_size = os.path.basename(payload_directory)
        results[payload_size] = parse_payload(payload_directory)
    return results
    
def parse_results(results_directory):
    config_directories = list_in_directory(results_directory, filters=[os.path.isdir])
    results = {}
    payload_sizes = set()
    for config_directory in config_directories:
        config_name = os.path.basename(config_directory)
        results[config_name] = parse_config(config_directory)
        for payload_size in results[config_name].keys():
            payload_sizes.add(payload_size)
    configs_grouped_by_payload = {}
    for payload_size in payload_sizes:
        payload_size_result = {}
        for config in results:
            payload_size_result[config] = results[config][payload_size]
        configs_grouped_by_payload[payload_size] = payload_size_result
    return configs_grouped_by_payload
    
def format(parsing_results, operation):
    lines = []
    configs = sorted(parsing_results[parsing_results.keys()[0]].keys())
    lines.append(",".join(["payload size"] + configs))
    for payload_size in parsing_results:
        line = [str(int(payload_size) / (2**10))]
        for config in configs:
            latency = parsing_results[payload_size][config][operation]["average"]
            throughput = float(payload_size) / latency
            throughput_in_kb = throughput / (2**20)
            line.append(str(throughput_in_kb))
        lines.append(",".join(line))
    return "\n".join(lines)
        

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(__file__, description="Parses results from microbench")
    PARSER.add_argument("results_directory", help="Results directory", type=str)
    ARGS = PARSER.parse_args()
    print format(parse_results(ARGS.results_directory), "encode")
    