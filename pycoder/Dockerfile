FROM dburihabwa/grpc-compiler-0.11-flat

#Install PyECLib
RUN apt-get update --quiet && apt-get upgrade --assume-yes --quiet && \
    apt-get install --assume-yes --quiet liberasurecode1 python-pip python-pyeclib wget

# Install python runtime requirements
RUN pip install -U grpcio==0.11.0b1 protobuf==3.0.0a3

# Expose port to other containers
EXPOSE 1234

# Copy server sources
COPY * /usr/local/src/app/
WORKDIR /usr/local/src/app/
ENTRYPOINT ["/usr/bin/python", "/usr/local/src/app/server.py"]
