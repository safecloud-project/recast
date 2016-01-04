#! /bin/bash

function print_help() {
	echo -e "Usage: $0 <requests> <concurrent requests> <payload size> [server]\n"
	echo "Arguments:"
	echo -e "\trequests                Total number of requests to ther server"
	echo -e "\tconcurrent requests     Number of concurrent requests"
	echo -e "\tpayload size            Size of the file to upload to the server"
	echo -e "\tserver                  Server to test in the form of host:port"
}

if [[ $# -ne 3 ]]; then
	print_help
	exit 0
fi

# Benchmark parameters
REQUESTS=$1
CONCURRENT_REQUESTS=$2
PAYLOAD_SIZE=$3
DATA_FILE="random$PAYLOAD_SIZE.dat"
if [ ! -f $DATA_FILE ]; then
	echo "File $DATA_FILE could not be found"
	exit 1
fi
SERVER="$PROXY_PORT_3000_TCP_ADDR:$PROXY_PORT_3000_TCP_PORT"
if [[ $# -ne 4 ]]; then
	SERVER=$4
fi
RANDOM_KEY=$(echo $(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1))

# Output files
COMPLETION_OUTPUT="completion-$REQUESTS-$CONCURRENT_REQUESTS-$PAYLOAD_SIZE.tsv"
GNUPLOT_DATA_OUTPUT="gnuplot-$REQUESTS-$CONCURRENT_REQUESTS-$PAYLOAD_SIZE.tsv"

# Benchmark
ab -n $REQUESTS -c $CONCURRENT_REQUESTS -e $COMPLETION_OUTPUT -g $GNUPLOT_DATA_OUTPUT -u $DATA_FILE http://$SERVER/$RANDOM_KEY
