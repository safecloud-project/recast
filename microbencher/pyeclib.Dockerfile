FROM dburihabwa/grpc-compiler-0.11-flat

# Install PyECLib
RUN apt-get update --quiet && apt-get upgrade --assume-yes --quiet && \
    apt-get install --assume-yes --quiet gcc git g++ python-pip wget yasm

# Install liberasurecode
WORKDIR /tmp
RUN git clone https://bitbucket.org/tsg-/liberasurecode.git
WORKDIR /tmp/liberasurecode
RUN git checkout v1.1.1 && ./autogen.sh && ./configure && make && make test && make install

# Install pyeclib
RUN apt-get install --assume-yes --quiet python-pyeclib

# Install python runtime requirements
RUN pip install -U --quiet cython grpcio==0.11.0b1 protobuf==3.0.0a3
RUN git clone https://github.com/sampot/pylonghair /usr/local/src/app
WORKDIR /usr/local/src/app/
RUN python setup.py build_ext --inplace

# Install intel ISA-L
WORKDIR /tmp/
RUN wget --quiet https://01.org/sites/default/files/downloads/intelr-storage-acceleration-library-open-source-version/isa-l-2.14.0.tar.gz && \
    tar xf isa-l-2.14.0.tar.gz
WORKDIR isa-l-2.14.0
RUN sed -i 's/1.14.1/1.15.1/' aclocal.m4 configure Makefile.in && \
    sed -i 's/1.14/1.15/'     aclocal.m4 configure Makefile.in && \
    ./configure && make && make install

# Copy server sources
ADD *.py /usr/local/src/app/
WORKDIR /usr/local/src/app/
