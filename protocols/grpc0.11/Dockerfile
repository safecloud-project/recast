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
      unzip \
      wget \
      zlib1g-dev

# Install protobuf 3
WORKDIR /
RUN wget --quiet https://github.com/google/protobuf/archive/v3.0.0-beta-1.tar.gz \
    && tar xf v3.0.0-beta-1.tar.gz && rm -rf /v3.0.0-beta-1.tar.gz
WORKDIR /protobuf-3.0.0-beta-1
RUN ./autogen.sh && ./configure && make && make check && make install && make clean \
    && ldconfig
WORKDIR /
RUN rm -rf /protobuf-3.0.0-beta-1

# Install GRPC
RUN git clone https://github.com/grpc/grpc /grpc
WORKDIR /grpc
RUN git checkout release-0_11 --quiet && make && make install

# Install grpc-java
RUN git clone --quiet https://github.com/grpc/grpc-java /grpc-java \
    && update-ca-certificates --fresh
WORKDIR /grpc-java/compiler
RUN git checkout v0.9.1 --quiet && ../gradlew java_pluginExecutable && ../gradlew test

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
      unzip \
      wget && \
    apt-get install --assume-yes --quiet  openjdk-8-jre-headless && \
    apt-get --quiet --assume-yes --quiet clean

# Setup necessary env variables
ENV GRPC_ROOT "/grpc/"
ENV GRPC_JAVA_ROOT "/grpc-java/"

WORKDIR /
