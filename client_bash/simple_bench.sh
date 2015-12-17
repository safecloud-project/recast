#!/bin/bash

function random_key
{
	echo $(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
}

UNUSED=${1:-10} #1st param left for argument order compatibility
SIZE=${2:-16} #2nd param or default to 16
HOST=${3:-"192.168.99.104:3000"} #os.getenv("PROXY_PORT_3000_TCP_ADDR") .. ":" .. os.getenv("PROXY_PORT_3000_TCP_PORT")

while [[ true ]]; do
	wget -q -O/dev/null  --method=PUT --body-file=random${SIZE}.dat ${HOST}/$(random_key)
	#rc=$?
	#if [[ $rc -ne 0 ]]; then
	#	echo "Exiting..."
	#	exit 0
	#fi
done
