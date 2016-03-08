#!/bin/bash
if [[ $# == 0 ]]
then
	echo "How to use:"
	echo "$0 size_of_random_data [MB]"
	exit 1
fi

readonly size=$1
readonly output_file="$(dirname "${BASH_SOURCE[0]}")/random${size}.dat"

dd if=/dev/urandom of="${output_file}"  bs=1048576 count="${size}"
