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

RUN apt-get update && \
    apt-get dist-upgrade --assume-yes --quiet && \
    apt-get autoremove   --assume-yes --quiet && \
    apt-get autoclean    --assume-yes --quiet && \
    apt-get install      --assume-yes --quiet libev-dev python-all-dev python-hiredis python-numpy python-pip && \
    apt-get install --assume-yes --quiet autoconf automake build-essential cython gcc git g++ libtool  python-pip python-numpy wget yasm && \
    ldconfig

# Install intel ISA-L 2.20.0
WORKDIR /tmp/
RUN wget --quiet https://github.com/01org/isa-l/archive/v2.20.0.tar.gz && \
    tar xaf v2.20.0.tar.gz &&\
    cd isa-l-2.20.0/ && \
    ./autogen.sh && ./configure && make -s && make install && \
    echo "/usr/lib" >> /etc/ld.so.conf && ldconfig

# Install gf-complete
RUN git clone https://github.com/ceph/gf-complete /tmp/gf-complete --quiet
WORKDIR /tmp/gf-complete
RUN git fetch --quiet && git checkout 7e61b44404f0ed410c83cfd3947a52e88ae044e1 --quiet && ./autogen.sh && ./configure && make && make install && ldconfig

# Install jerasure
RUN git clone https://github.com/ceph/jerasure.git /tmp/jerasure --quiet
WORKDIR /tmp/jerasure
RUN git fetch --quiet && git checkout f8e5f981859f87cbb0ca82e03f66c06571078093 --quiet && autoreconf --force --install && ./configure && make && make install && ldconfig

# Install liberasurecode 1.4.0
# FIXME: Breaks with 35000cb0c34378a8565a41bbb914ea1aaecd92fa and actual checksum checking
RUN git clone https://github.com/openstack/liberasurecode /tmp/liberasurecode --quiet
WORKDIR /tmp/liberasurecode
RUN git checkout 1.4.0 --quiet && ./autogen.sh && ./configure && make && make test && make install && ldconfig

# Upgrade pip
RUN pip install --upgrade --quiet pip

# Install pylonghair
WORKDIR /tmp/pylonghair
RUN git clone https://github.com/sampot/pylonghair . --quiet
RUN python setup.py install

# Install libgfshare
RUN apt-get update --quiet && apt-get install --assume-yes --quiet libgfshare-dev

# Install pip dependencies
WORKDIR /usr/local/src/app/
COPY requirements.txt /usr/local/src/app
RUN apt-get update &&\
    apt-get install --yes --quiet libssl-dev libffi-dev python-dev &&\
    pip install --quiet --upgrade pip &&\
    pip install --quiet --requirement requirements.txt

COPY requirements.txt  /usr/local/src/pyproxy/requirements.txt
WORKDIR /usr/local/src/pyproxy
RUN pip install --upgrade --requirement requirements.txt
COPY . /usr/local/src/pyproxy
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
EXPOSE 3000
ENV PYTHONPATH "${PYTHONPATH}:/usr/local/src/pyproxy"
ENTRYPOINT ["python", "/usr/local/src/pyproxy/proxy.py"]
