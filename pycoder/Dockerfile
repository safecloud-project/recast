FROM ubuntu:15.10

# Install dependencies
RUN apt-get update --quiet && apt-get upgrade --assume-yes --quiet
RUN apt-get install --assume-yes --quiet automake build-essential gcc liberasurecode1 wget

#Install PyECLib
RUN apt-get install --assume-yes --quiet python-pyeclib

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

# Install python runtime requirements
RUN pip install -U grpcio==0.11.0b1
RUN pip install -U protobuf==3.0.0a3

# Cleanup
RUN apt-get autoremove  --assume-yes --quiet autoconf automake build-essential curl git libtool unzip wget
RUN rm -rf /protobuf-3.0.0-beta-1 /v3.0.0-beta-1.tar.gz
RUN apt-get --assume-yes --quiet autoremove
RUN apt-get --assume-yes --quiet autoclean

# Copy server sources
COPY *.py /usr/local/src/app/
ENTRYPOINT ["/usr/bin/python", "/usr/local/src/app/server.py"]
