FROM ubuntu:16.04

MAINTAINER "Dorian BURIHABWA <dorian DOT burihabwa AT unine DOT ch >"

RUN apt-get update --quiet && \
    apt-get install --assume-yes --quiet \
      autoconf \
      curl \
      gcc \
      g++ \
      git \
      libgrpc-dev \
      libssl-dev \
      libtool \
      make \
      openjdk-8-jdk-headless \
      python-all-dev \
      python-pip \
      unzip \
      wget \
      zlib1g-dev && \
# Install protobuf
    git clone https://github.com/google/protobuf /protobuf --quiet && \
    cd /protobuf && \
    git checkout v3.2.0 --quiet && \
    ./autogen.sh && \
    ./configure && \
    make -s && \
    make check -s && \
    make install -s && \
    make clean -s && \
    ldconfig && \
    cd / && \
    rm -rf /protobuf && \
# Install GRPC
    cd / && \
    git clone https://github.com/grpc/grpc /grpc --quiet && \
    cd /grpc && \
    git checkout v1.1.2 --quiet && \
    git submodule update --init && \
    ldconfig && \
    pip install --requirement requirements.txt --quiet && \
    make -s && \
    make install -s && \
    ldconfig && \
    apt-get --assume-yes --quiet --purge autoremove \
      autoconf \
      curl \
      gcc \
      git \
      g++ \
      libtool \
      libssl-dev \
      openjdk-8-jdk-headless \
      python-all-dev \
      python-pip \
      unzip \
      wget && \
    apt-get --quiet --assume-yes --quiet clean && \
    rm -rf /var/lib/apt/lists/* /var/tmp/* && \
# Setup necessary env variables
    echo -e "\nGRPC_ROOT='/grpc/'" >> /etc/environment
ENV GRPC_ROOT "/grpc/"


WORKDIR /
