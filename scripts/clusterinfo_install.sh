#! /usr/bin/env bash

# Install dependencies
sudo apt-get update && \
sudo apt-get dist-upgrade --assume-yes && \
sudo apt-get install apache2-utils curl python-dev python-pip wget --assume-yes && \
sudo apt-get autoremove --assume-yes && \
sudo pip install configparser docker ruamel.yaml requests

# Cleanup the system
docker system prune --force
