#! /usr/bin/env python
"""
Renames dstat result files for the encoding benchmark from microbench-encode-* to microbench-decode-*
"""

import os

if __name__ == "__main__":
    HERE = os.path.dirname(__file__)
    LIBRARIES_RESULTS = [ os.path.join(HERE, entry) for entry in os.listdir(HERE) if os.path.isdir(os.path.join(HERE, entry)) ]
    for library_dir in LIBRARIES_RESULTS:
        DSTAT_FILES_TO_RENAME  = [ entry for entry in os.listdir(library_dir) if os.path.isfile(os.path.join(library_dir, entry)) and entry.find("encode") != -1 and entry.find(".csv") != -1 ]
        for dstat_file in DSTAT_FILES_TO_RENAME:
            fixed_name = dstat_file.replace("encode", "decode")
            print "Renaming ", os.path.join(library_dir, dstat_file), "to", os.path.join(library_dir, fixed_name)
            os.rename(os.path.join(library_dir, dstat_file), os.path.join(library_dir, fixed_name))

