FROM dburihabwa/grpc-compiler-0.11-flat

#Install dependencies
RUN apt-get update --quiet && apt-get upgrade --assume-yes --quiet && \
    apt-get install --assume-yes --quiet liberasurecode1 liberasurecode-dev libjerasure2 python-pip wget && \
    ldconfig

# Install python runtime requirements
RUN pip install --upgrade --quiet grpcio==0.11.0b1 pyeclib==1.2.0 protobuf==3.0.0a3

# Expose port to other containers
EXPOSE 1234

# Copy server sources
COPY * /usr/local/src/app/
WORKDIR /usr/local/src/app/
ENTRYPOINT ["/usr/bin/python", "/usr/local/src/app/server.py"]
