import argparse
import os
import pstats
import re

SIZE_PATTERN = re.compile("a")

def is_python_encode_key(line):
    return line[0].endswith("py") and line[2].find("encode") != -1

def is_native_encode_key(line):
    return line[0] == "~" and line[2].find("encode") != -1

def extract(path):
    """
    """
    stats = pstats.Stats(path)
    total_time = stats.total_tt
    native = []
    python_encode_keys = filter(is_python_encode_key, stats.stats.keys())
    wrapper_encoding_time = max(map(lambda key: stats.stats.get(key)[3], python_encode_keys))
    native_encode_keys = filter(is_native_encode_key, stats.stats.keys())
    native_encoding_time = sum(map(lambda key: stats.stats.get(key)[3], native_encode_keys))
    return {"native": native_encoding_time, "total": total_time, "wrapper": wrapper_encoding_time}


if __name__ == "__main__":
    path_to_profile_dump = os.path.join(os.path.dirname(__file__), \
    "xpdata/cprofile/jerasure_rs_cauchy/4MB.cProfile")
    extract(path_to_profile_dump)
    directory = os.path.join(os.path.dirname(__file__), "xpdata/cprofile/")
    libraries = map(lambda x: os.path.join(directory, x), os.listdir(directory))
    for library in libraries:
        data = []
        profiles = map(lambda x: os.path.join(library, x), os.listdir(library))
        for profile in profiles:
            size = re.findall("\d+MB", profile)[0]
            time_data = extract(profile)
            time_data["size"] = size
            print time_data
