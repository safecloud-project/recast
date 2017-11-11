#! /usr/bin/env sh

PLAYCLOUD_HOST=${PLAYCLOUD_HOST:="proxy"}
PLAYCLOUD_PORT=${PLAYCLOUD_PORT:=3000}
PLAYCLOUD_REQUESTS=${PLAYCLOUD_REQUESTS:=1000}
PLAYCLOUD_CONCURRENCY=${PLAYCLOUD_CONCURRENCY:=4}
PLAYCLOUD_PAYLOAD_SIZE=${PLAYCLOUD_PAYLOAD_SIZE:=1024}

/usr/local/src/app/put.py --host "${PLAYCLOUD_HOST}"\
                          --port "${PLAYCLOUD_PORT}"\
                          --requests "${PLAYCLOUD_REQUESTS}"\
                          --concurrency "${PLAYCLOUD_CONCURRENCY}"\
                          --payload-size "${PLAYCLOUD_PAYLOAD_SIZE}" > /data/data.json