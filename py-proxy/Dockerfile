FROM dburihabwa/grpc-compiler-0.11-flat

RUN apt-get update && \
    apt-get upgrade      --assume-yes --quiet && \
    apt-get dist-upgrade --assume-yes --quiet && \
    apt-get autoremove   --assume-yes --quiet && \
    apt-get autoclean    --assume-yes --quiet && \
    apt-get install      --assume-yes --quiet python-numpy && \
    apt-get install      --assume-yes --quiet python-pip
COPY .  /usr/local/src/py-proxy
COPY safestore/data.db /root/data.db
WORKDIR /usr/local/src/py-proxy
RUN pip install --upgrade --requirement requirements.txt && \
    pip install --upgrade --requirement safestore/requirements.txt
EXPOSE 8000
ENTRYPOINT ["python", "/usr/local/src/py-proxy/proxy.py"]
