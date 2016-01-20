FROM ubuntu:15.10

MAINTAINER "Dorian BURIHABWA <dorian DOT burihabwa AT unine DOT ch >"

RUN apt-get update --quiet && apt-get upgrade --assume-yes --quiet \
    && apt-get install --assume-yes --quiet gcc g++ make wget \
    autoconf curl libtool unzip \
    git libgrpc-dev libssl-dev python-all-dev zlib1g-dev \
    openjdk-8-jdk

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
RUN git checkout release-0_11 && make && make install

# Install grpc-java
RUN git clone --quiet https://github.com/grpc/grpc-java /grpc-java \
    && update-ca-certificates --fresh
WORKDIR /grpc-java/compiler
RUN ../gradlew java_pluginExecutable

# Cleanup
RUN apt-get --assume-yes --quiet autoremove && apt-get --assume-yes --quiet autoclean

# Setup necessary env variables
RUN echo "export GRPC_ROOT=\"/grpc/\"" >> /etc/bash.bashrc \
    && echo "export GRPC_JAVA_ROOT=\"/grpc-java/\"" >> /etc/bash.bashrc

WORKDIR /
