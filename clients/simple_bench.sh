#!/bin/bash

function random_key
{
	cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1
}

readonly UNUSED=${1:-10} #1st param left for argument order compatibility
readonly SIZE=${2:-16} #2nd param or default to 16
readonly HOST=${3:-"192.168.99.104:3000"} #os.getenv("PROXY_PORT_3000_TCP_ADDR") .. ":" .. os.getenv("PROXY_PORT_3000_TCP_PORT")
readonly DATA_FILE="$(dirname "${BASH_SOURCE[0]}")/random${PAYLOAD_SIZE}.dat"

if [ ! -f "${DATA_FILE}" ]; then
	echo "File ${DATA_FILE} could not be found"
	echo -n "Creating data file..."
	"${BASE_DIR}/gen_random_data.sh" "${PAYLOAD_SIZE}" 2>/dev/null
	echo "done"
fi

while [[ true ]]; do
	wget -q -O/dev/null  --method=PUT --body-file="${DATA_FILE}" "${HOST}/$(random_key)"
	rc=${?}
	if [[ "${rc}" -ne 0 ]]; then
		echo "Exiting..."
		exit 0
	fi
done
