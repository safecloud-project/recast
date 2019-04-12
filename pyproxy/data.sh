#!/usr/bin/env bash

mkdir -p /tmp/{in,out}
cat /dev/urandom | base64 | head -c $((1024 * 1024)) > /tmp/in/input.txt
./offline.py /etc/ /tmp/out/
mkdir /tmp/copy
./offline.py --decode /tmp/out/ /tmp/copy