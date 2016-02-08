FROM dburihabwa/grpc-compiler-0.11-flat

#Install PyECLib
RUN apt-get update --quiet && apt-get upgrade --assume-yes --quiet && \
    apt-get install --assume-yes --quiet liberasurecode1 python-pip python-pyeclib wget

# Install python runtime requirements
RUN pip install -U grpcio==0.11.0b1 protobuf==3.0.0a3

# Copy server sources
ADD *.py /usr/local/src/app/
ADD pycoder.cfg /usr/local/src/app
WORKDIR /usr/local/src/app/
