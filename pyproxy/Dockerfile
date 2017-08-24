FROM dburihabwa/grpc-compiler-1.0-flat

RUN apt-get update && \
    apt-get dist-upgrade --assume-yes --quiet && \
    apt-get autoremove   --assume-yes --quiet && \
    apt-get autoclean    --assume-yes --quiet && \
    apt-get install      --assume-yes --quiet python-all-dev python-numpy python-pip
COPY requirements.txt  /usr/local/src/pyproxy/requirements.txt
COPY pyproxy/safestore/data.db /root/data.db
WORKDIR /usr/local/src/pyproxy
RUN pip install --upgrade --requirement requirements.txt
COPY . /usr/local/src/pyproxy
EXPOSE 8000
ENV PYTHONPATH "${PYTHONPATH}:/usr/local/src/pyproxy"
ENTRYPOINT ["python", "/usr/local/src/pyproxy/proxy.py"]
