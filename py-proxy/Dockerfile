FROM dburihabwa/grpc-compiler-0.11-flat

RUN apt-get update && \
    apt-get upgrade      --assume-yes --quiet && \
    apt-get dist-upgrade --assume-yes --quiet && \
    apt-get autoremove   --assume-yes --quiet && \
    apt-get autoclean    --assume-yes --quiet
COPY * /usr/local/src/app/
WORKDIR /usr/local/src/app
RUN pip install --upgrade --requirement requirements.txt
EXPOSE 8000
#ENTRYPOINT ["python", "/usr/local/src/app/proxy.py"]
