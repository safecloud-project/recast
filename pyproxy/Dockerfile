FROM dburihabwa/grpc-compiler-1.0-flat

RUN apt-get update && \
    apt-get dist-upgrade --assume-yes --quiet && \
    apt-get autoremove   --assume-yes --quiet && \
    apt-get autoclean    --assume-yes --quiet && \
    apt-get install      --assume-yes --quiet libev-dev python-all-dev python-hiredis python-numpy python-pip && \
    apt-get install --assume-yes --quiet autoconf automake build-essential cython gcc git g++ libjerasure2 libtool  python-pip python-numpy wget yasm && \
    ldconfig

# Install intel ISA-L 2.20.0
WORKDIR /tmp/
RUN wget --quiet https://github.com/01org/isa-l/archive/v2.20.0.tar.gz && \
    tar xaf v2.20.0.tar.gz &&\
    cd isa-l-2.20.0/ && \
    ./autogen.sh && ./configure && make -s && make install && \
    echo "/usr/lib" >> /etc/ld.so.conf && ldconfig

# Install liberasurecode 1.1.1
WORKDIR /tmp
RUN git clone https://bitbucket.org/tsg-/liberasurecode.git --quiet
WORKDIR /tmp/liberasurecode
RUN git checkout v1.1.1 --quiet && ./autogen.sh && ./configure && make && make test && make install && ldconfig

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
    easy_install -U cffi &&\
    pip install --quiet --requirement requirements.txt

COPY requirements.txt  /usr/local/src/pyproxy/requirements.txt
COPY pyproxy/safestore/data.db /root/data.db
WORKDIR /usr/local/src/pyproxy
RUN pip install --upgrade --requirement requirements.txt
COPY . /usr/local/src/pyproxy
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
EXPOSE 8000
ENV PYTHONPATH "${PYTHONPATH}:/usr/local/src/pyproxy"
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
