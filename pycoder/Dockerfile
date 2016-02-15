FROM dburihabwa/grpc-compiler-0.11-flat

#Install dependencies
RUN apt-get update --quiet && apt-get upgrade --assume-yes --quiet && \
    apt-get install --assume-yes --quiet liberasurecode1 liberasurecode-dev libjerasure2 python-pip wget yasm && \
    ldconfig

# Install python runtime requirements
RUN pip install --upgrade --quiet grpcio==0.11.0b1 pyeclib==1.2.0 protobuf==3.0.0a3

# Install intel ISA-L
WORKDIR /tmp/
RUN wget --quiet https://01.org/sites/default/files/downloads/intelr-storage-acceleration-library-open-source-version/isa-l-2.14.0.tar.gz && \
    tar xf isa-l-2.14.0.tar.gz
WORKDIR isa-l-2.14.0
RUN sed -i 's/1.14.1/1.15.1/' aclocal.m4 configure Makefile.in && \
    sed -i 's/1.14/1.15/'     aclocal.m4 configure Makefile.in && \
    ./configure && make && make install && \
    echo "/usr/lib" >> /etc/ld.so.conf && ldconfig

# Expose port to other containers
EXPOSE 1234

# Copy server sources
COPY * /usr/local/src/app/
WORKDIR /usr/local/src/app/
ENTRYPOINT ["/usr/bin/python", "/usr/local/src/app/server.py"]
