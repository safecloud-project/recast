FROM dburihabwa/grpc-compiler-0.11-flat

# Install dependencies
RUN apt-get update --quiet && apt-get upgrade --assume-yes --quiet && \
    apt-get install --assume-yes --quiet autoconf automake build-essential gcc git g++ libjerasure2 libtool  python-pip wget yasm && ldconfig

# Install intel ISA-L
WORKDIR /tmp/
RUN wget --quiet https://01.org/sites/default/files/downloads/intelr-storage-acceleration-library-open-source-version/isa-l-2.14.0.tar.gz && \
    tar xf isa-l-2.14.0.tar.gz
WORKDIR isa-l-2.14.0
RUN sed -i 's/1.14.1/1.15.1/' aclocal.m4 configure Makefile.in && \
    sed -i 's/1.14/1.15/'     aclocal.m4 configure Makefile.in && \
    ./configure && make && make install && \
    echo "/usr/lib" >> /etc/ld.so.conf && ldconfig

# Install liberasurecode
WORKDIR /tmp
RUN git clone https://bitbucket.org/tsg-/liberasurecode.git --quiet
WORKDIR /tmp/liberasurecode
RUN git checkout v1.1.1 --quiet && ./autogen.sh && ./configure && make && make test && make install && ldconfig

# Install pyeclib
WORKDIR /tmp
RUN git clone https://bitbucket.org/kmgreen2/pyeclib.git --quiet
WORKDIR /tmp/pyeclib
RUN python setup.py install && \
    echo "/usr/local/lib/python2.7/dist-packages/" >> /etc/ld.so.conf && ldconfig

# Install python runtime requirements
RUN pip install --upgrade --quiet cython
RUN git clone https://github.com/sampot/pylonghair /usr/local/src/app --quiet
WORKDIR /usr/local/src/app/
RUN python setup.py build_ext --inplace

# Copy server sources
ADD *.py /usr/local/src/app/
ADD pylonghair_driver.py /usr/local/src/app/
WORKDIR /usr/local/src/app/
