#!/bin/bash
declare -a PAYLOAD_SIZES=(1024 2048 131072 262144 4194304 8388608) #1K 2K 128K 256K 4MB 8MB
INPUT="fuse.log"
for size in ${PAYLOAD_SIZES[@]}; do
	#echo $size
	grep "$size" $INPUT | nl > data/${size}_data.txt
done