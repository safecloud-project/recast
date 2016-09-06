#!/bin/bash

if [ -z "$1" ]
  then
    echo "No input file supplied"
	exit 1; 
fi

declare -a PAYLOAD_SIZES=(1024 2048 131072 262144 524288 4194304 8388608) #1K 2K 128K 256K 4MB 8MB
INPUT=$1
for size in ${PAYLOAD_SIZES[@]}; do
	grep "$size" $INPUT | nl > data/${size}_data.txt
done