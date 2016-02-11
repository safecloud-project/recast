FROM dburihabwa/grpc-compiler-0.11-flat

#Install PyECLib
RUN apt-get update --quiet && apt-get upgrade --assume-yes --quiet && \
    apt-get install --assume-yes --quiet liberasurecode1 python-pip python-pyeclib wget

# Install python runtime requirements
RUN pip install -U cython grpcio==0.11.0b1 protobuf==3.0.0a3
RUN git clone https://github.com/sampot/pylonghair /usr/local/src/app
WORKDIR /usr/local/src/app/
RUN python setup.py build_ext --inplace

# Copy server sources
ADD *.py /usr/local/src/app/
WORKDIR /usr/local/src/app/
