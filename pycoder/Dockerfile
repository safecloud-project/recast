FROM ubuntu:15.10

# Install dependencies
RUN apt-get update --quiet && apt-get upgrade --assume-yes --quiet
RUN apt-get install --assume-yes --quiet automake build-essential gcc liberasurecode1 python-dev python-setuptools wget

#Install PyECLib
RUN ldconfig
WORKDIR /tmp/
RUN wget https://pypi.python.org/packages/source/P/PyECLib/PyECLib-1.1.1.tar.gz#md5=53ba4101e01e22728bc25fcd43287565
RUN tar xf PyECLib-1.1.1.tar.gz && rm PyECLib-1.1.1.tar.gz
WORKDIR /tmp/PyECLib-1.1.1
RUN python setup.py install
RUN rm -rf /tmp/PyECLib-1.1.1
WORKDIR /


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
RUN apt-get install --assume-yes --quiet autoconf git libtool libgrpc-dev libssl-dev python-all-dev python-virtualenv zlib1g-dev
RUN git clone https://github.com/grpc/grpc
WORKDIR grpc
RUN make
RUN make install
RUN make clean
WORKDIR /

# Cleanup
RUN apt-get autoremove  --assume-yes --quiet autoconf automake build-essential curl gcc git libtool unzip wget
RUN rm -rf /protobuf-3.0.0-beta-1 /v3.0.0-beta-1.tar.gz
RUN apt-get autoclean
