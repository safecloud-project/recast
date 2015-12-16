#!/bin/bash
#NEW_UUID=$(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)

function random_key
{
	echo $(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
}

#random_key=$(random_key)
#echo $random_key

TOTAL_KEYS=$1
SIZE=$2 
HOST=$3 #os.getenv("PROXY_PORT_3000_TCP_ADDR") .. ":" .. os.getenv("PROXY_PORT_3000_TCP_PORT")

echo "TOTAL_KEYS=${TOTAL_KEYS}"

for (( i = 0; i < $TOTAL_KEYS; i++ )); do
	wget -q -O/dev/null  --method=PUT --body-file=random${SIZE}.dat ${HOST}/$(random_key)
done
	