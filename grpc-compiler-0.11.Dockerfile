FROM ubuntu:15.10

# Install dependencies
RUN apt-get update --quiet && apt-get upgrade --assume-yes --quiet
RUN apt-get install --assume-yes --quiet automake build-essential gcc liberasurecode1 wget

# Install protobuf 3
RUN apt-get install --assume-yes --quiet autoconf curl libtool unzip
RUN wget --quiet https://github.com/google/protobuf/archive/v3.0.0-beta-1.tar.gz
RUN tar xf v3.0.0-beta-1.tar.gz
WORKDIR /protobuf-3.0.0-beta-1
RUN ./autogen.sh
RUN ./configure
RUN make
RUN make check
RUN make install
RUN ldconfig
RUN make clean
WORKDIR /

# Install GRPC
RUN apt-get install --assume-yes --quiet autoconf git libtool libgrpc-dev libssl-dev python-all-dev python-pip python-virtualenv zlib1g-dev
RUN git clone https://github.com/grpc/grpc
WORKDIR grpc
RUN git checkout release-0_11
RUN make
RUN make install
WORKDIR /

# Install grpc-java
RUN apt-get install --quiet --assume-yes openjdk-8-jdk
RUN git clone --quiet https://github.com/grpc/grpc-java /grpc-java
RUN update-ca-certificates -f
WORKDIR  /grpc-java/compiler
RUN ../gradlew java_pluginExecutable

# Cleanup
RUN apt-get autoremove  --assume-yes --quiet autoconf automake build-essential curl git libtool unzip wget
RUN rm -rf /protobuf-3.0.0-beta-1 /v3.0.0-beta-1.tar.gz
RUN apt-get --assume-yes --quiet autoremove
RUN apt-get --assume-yes --quiet autoclean

# Setup necessary env variables
RUN echo "export GRPC_ROOT=\"/grpc/\"" >> /etc/bash.bashrc
RUN echo "export GRPC_JAVA_ROOT=\"/grpc-java/\"" >> /etc/bash.bashrc
