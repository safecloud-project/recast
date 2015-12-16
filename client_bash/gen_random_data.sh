#!/bin/bash
if [[ $# == 0 ]]
then
	echo "How to use:"
    echo "$0 size_of_random_data [MB]"
    exit 1
fi
size=$1
dd if=/dev/urandom of=random${size}.dat bs=1048576 count=${size}

