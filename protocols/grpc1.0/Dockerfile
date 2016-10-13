FROM ubuntu:15.10

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
      zlib1g-dev

# Install protobuf

# Setup protobuf version e8ae137c96444ea313485ed1118c5e43b2099cf1
RUN git clone https://github.com/google/protobuf /protobuf --quiet
WORKDIR /protobuf
RUN git checkout 3.0.x --quiet && \
    ./autogen.sh && ./configure && make && make check && make install && make clean
RUN ldconfig
WORKDIR /
RUN rm -rf /protobuf

# Install GRPC
RUN git clone https://github.com/grpc/grpc /grpc --quiet
WORKDIR /grpc
RUN git checkout v1.0.x --quiet && git submodule update --init && ldconfig && pip install --requirement requirements.txt --quiet && make && make install
WORKDIR /

# Cleanup
RUN apt-get --assume-yes --quiet --purge autoremove \
      autoconf \
      curl \
      gcc \
      g++ \
      libtool \
      libssl-dev \
      openjdk-8-jdk-headless \
      python-all-dev \
      python-pip \
      unzip \
      wget && \
    apt-get --quiet --assume-yes --quiet clean

# Setup necessary env variables
ENV GRPC_ROOT "/grpc/"

WORKDIR /
