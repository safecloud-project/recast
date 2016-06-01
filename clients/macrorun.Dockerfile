FROM ubuntu:latest
RUN apt-get update --quiet && apt-get install --quiet --assume-yes apache2-utils autoconf automake build-essential ca-certificates curl gcc gcc-doc netcat openssl wget
RUN wget -q https://github.com/JoeDog/siege/archive/v4.0.0.tar.gz -O siege-4.0.0.tgz && tar xf siege-4.0.0.tgz
WORKDIR siege-4.0.0
RUN utils/bootstrap && ./configure && make && make install
COPY test-load.sh /usr/local/bin/
WORKDIR /
