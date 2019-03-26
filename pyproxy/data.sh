#!/usr/bin/env bash

mkdir -p /tmp/{in,out}
cat /dev/urandom | base64 | head -c 1000000 > /tmp/in/input.txt