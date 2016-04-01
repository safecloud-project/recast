FROM dburihabwa/grpc-compiler-0.11-flat

#Install dependencies
RUN apt-get update --quiet && apt-get upgrade --assume-yes --quiet && \
    apt-get install --assume-yes --quiet autoconf automake build-essential gcc git g++ libjerasure2 libtool  python-pip python-numpy wget yasm && \
    ldconfig


# Install intel ISA-L
WORKDIR /tmp/
RUN wget --quiet https://01.org/sites/default/files/downloads/intelr-storage-acceleration-library-open-source-version/isa-l-2.14.0.tar.gz && \
    tar xf isa-l-2.14.0.tar.gz
WORKDIR isa-l-2.14.0
RUN sed -i 's/1.14.1/1.15.1/' aclocal.m4 configure Makefile.in && \
    sed -i 's/1.14/1.15/'     aclocal.m4 configure Makefile.in && \
    ./configure && make && make install && \
    echo "/usr/lib" >> /etc/ld.so.conf && ldconfig

# Install liberasurecode 1.1.1
WORKDIR /tmp
RUN git clone https://bitbucket.org/tsg-/liberasurecode.git --quiet
WORKDIR /tmp/liberasurecode
RUN git checkout v1.1.1 --quiet && ./autogen.sh && ./configure && make && make test && make install && ldconfig

# Install python runtime requirements
RUN pip install --upgrade --quiet pip
RUN pip install --quiet \
    # pylonghair dependencies
    cython==0.23.4 \
    # Pycoder depenencies
    grpcio==0.11.0b1 pyeclib==1.2.0 protobuf==3.0.0a3 \
    # Safestore dependencies
    cryptography==1.0.1 fake-factory==0.5.7 pycrypto==2.6.1 secretsharing==0.2.6

# Install pylonghair
WORKDIR /tmp/pylonghair
RUN git clone https://github.com/sampot/pylonghair . --quiet
RUN python setup.py install

# Expose port to other containers
EXPOSE 1234

# Copy server source
COPY *py /usr/local/src/app/
COPY pycoder.cfg /usr/local/src/app/
COPY safestore /usr/local/src/app/safestore
COPY test_files  /usr/local/src/app/test_files
COPY safestore/keys /usr/local/src/app/safestore/keys
COPY logging.conf /usr/local/src/app/
WORKDIR /usr/local/src/app/
ENTRYPOINT /usr/bin/python /usr/local/src/app/server.py
