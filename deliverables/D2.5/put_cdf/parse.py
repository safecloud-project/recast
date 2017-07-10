#! /usr/bin/env python

import os

import numpy


def compute_stats(numbers):
    return {
        "count": len(numbers),
        "average": numpy.mean(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "median": numpy.median(numbers),
        "std": numpy.std(numbers)
    }

def read_numbers(file_path):
    with open(file_path, "r") as file_handle:
        lines = file_handle.readlines()[1:]
        numbers = [float(line.strip().split(",")[1]) for line in lines]
        return numbers

def read_for_config(config_path):
    stats = {index: [] for index in xrange(100)}
    for experiment in xrange(1, 6, 1):
        numbers = read_numbers("{:s}/{:d}/completion-1000-4-1.csv".format(config_path, experiment))
        for index, number in enumerate(numbers):
            stats[index].append(number)
    return [compute_stats(stats[key]) for key in sorted(stats.keys())]

def parse(rootdir):
    directories = [directory for directory in os.listdir(rootdir) if os.path.isdir(directory)]
    return {directory: read_for_config(directory) for directory in directories}

def format_output():
    data = parse(".")
    configurations = sorted(data.keys())
    print "percentage" +  ",".join(configurations)
    for index in xrange(100):
        line = [str(index)]
        for conf in configurations:
            line.append(str(data[conf][index]["average"]))
        print ",".join(line)

if __name__ == "__main__":
    print format_output()
