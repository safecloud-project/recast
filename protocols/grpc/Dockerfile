FROM ubuntu:16.04

RUN apt-get update && apt-get dist-upgrade --assume-yes --quiet && \
    apt-get install build-essential autoconf git libtool --assume-yes --quiet && \
    git clone --branch v1.6.x https://github.com/grpc/grpc /grpc --quiet && \
    cd /grpc && \
    git submodule update --init && \
    make && \
    make install && \
    echo -e "\nGRPC_ROOT='/grpc/'" >> /etc/environment && \
    apt-get autoremove autoconf build-essential git libtool --assume-yes --quiet && \
    apt-get autoclean && \
    rm -rf /var/lib/apt/listls/* /var/tmp/*
ENV GRPC_ROOT "/grpc/"
