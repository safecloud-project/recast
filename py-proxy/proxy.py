#! /usr/bin/env python
"""
A python implementation of playcloud's proxy server
"""

import os
import uuid

from bottle import run, request
import bottle
import redis

# Redis configuration
HOST = os.getenv("REDIS_PORT_6379_TCP_ADDR", "127.0.0.1")
PORT = os.getenv("REDIS_PORT_6379_TCP_PORT", 6379)
REDIS = redis.StrictRedis(host=HOST, port=PORT, db=0)

# Bottle webapp configuration
bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 * 1024
APP = bottle.app()

def store(key=None, data=None):
    """
    Store data into playcloud

    key -- Key under which the data should be stored (default None)
    """
    if key is None:
        key = str(uuid.uuid4())
    REDIS.set(key, data)
    return key

@APP.route("/<key>", method="PUT")
def put(key):
    """
    Handles PUT requests to store data into playcloud
    """
    return store(key=key, data=request.body.getvalue())

@APP.route("/", method="PUT")
def put_keyless():
    """
    Handle PUT requests for key-less database insertions
    """
    return store(key=None, data=request.body.getvalue())

if __name__ == "__main__":
    run(app=APP, host="0.0.0.0", port=8000)
