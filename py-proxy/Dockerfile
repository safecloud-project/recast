FROM dburihabwa/grpc-compiler-0.11-flat

RUN apt-get update && \
    apt-get upgrade      --assume-yes --quiet && \
    apt-get dist-upgrade --assume-yes --quiet && \
    apt-get autoremove   --assume-yes --quiet && \
    apt-get autoclean    --assume-yes --quiet && \
    apt-get install      --assume-yes --quiet python-numpy
COPY py-proxy  /usr/local/src/py-proxy
COPY safestore /usr/local/lib/python2.7/dist-packages/safestore
WORKDIR /usr/local/src/
RUN pip install --upgrade --requirement py-proxy/requirements.txt && \
    pip install --upgrade --requirement /usr/local/lib/python2.7/dist-packages/safestore/requirements.txt
EXPOSE 8000
ENTRYPOINT ["python", "/usr/local/src/py-proxy/proxy.py"]
