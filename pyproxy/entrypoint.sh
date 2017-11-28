#! /usr/bin/env bash

uwsgi\
      --http-socket 0.0.0.0:3000\
      --disable-logging\
      --enable-threads\
      --threads 100\
      --wsgi-file /usr/local/src/pyproxy/proxy.py
