#! /bin/bash


function print_help() {
	echo -e "Usage: $0 <requests> <concurrent requests> <payload size> [server]\n"
	echo "Arguments:"
	echo -e "\trequests                Total number of requests to ther server"
	echo -e "\tconcurrent requests     Number of concurrent requests"
	echo -e "\tpayload size            Size of the file to upload to the server"
	echo -e "\tserver                  Server to test in the form of host:port"
}

if [[ $# -lt 3 ]]; then
	print_help
	exit 0
fi

# Benchmark parameters
REQUESTS=$1
CONCURRENT_REQUESTS=$2
PAYLOAD_SIZE=$3
BASE_DIR=$(dirname "${BASH_SOURCE[0]}")
DATA_FILE="${BASE_DIR}/random${PAYLOAD_SIZE}.dat"
if [ ! -f "${DATA_FILE}" ]; then
	echo "File ${DATA_FILE} could not be found"
	echo -n "Creating data file..."
	"${BASE_DIR}/gen_random_data.sh" "${PAYLOAD_SIZE}" 2>/dev/null
	echo "done"
fi
SERVER="${PROXY_PORT_3000_TCP_ADDR}:${PROXY_PORT_3000_TCP_PORT}"
if [[ $# -ge 4 ]]; then
	SERVER=$4
fi

# Output files
COMPLETION_OUTPUT="completion-${REQUESTS}-${CONCURRENT_REQUESTS}-${PAYLOAD_SIZE}.csv"
GNUPLOT_DATA_OUTPUT="gnuplot-${REQUESTS}-${CONCURRENT_REQUESTS}-${PAYLOAD_SIZE}.tsv"

# Benchmark
ab -v 5 -n "${REQUESTS}" -c "${CONCURRENT_REQUESTS}" -e "${COMPLETION_OUTPUT}" -g "${GNUPLOT_DATA_OUTPUT}" -u "${DATA_FILE}" "http://${SERVER}/"
