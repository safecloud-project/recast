FROM dburihabwa/grpc-compiler-0.11-flat

RUN apt-get update && \
    apt-get upgrade      --assume-yes --quiet && \
    apt-get dist-upgrade --assume-yes --quiet && \
    apt-get autoremove   --assume-yes --quiet && \
    apt-get autoclean    --assume-yes --quiet && \
    apt-get install      --assume-yes --quiet python-numpy && \
    apt-get install      --assume-yes --quiet python-pip
COPY requirements.txt  /usr/local/src/pyproxy/requirements.txt
COPY safestore/requirements.txt  /usr/local/src/pyproxy/safestore/requirements.txt
COPY safestore/data.db /root/data.db
WORKDIR /usr/local/src/pyproxy
RUN pip install --upgrade --requirement requirements.txt && \
    pip install --upgrade --requirement safestore/requirements.txt
COPY . /usr/local/src/pyproxy
EXPOSE 8000
ENTRYPOINT ["python", "/usr/local/src/pyproxy/proxy.py"]
