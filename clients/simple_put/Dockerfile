FROM alpine:latest
RUN apk update --quiet && apk add python py-pip --quiet
COPY requirements.txt usr/local/src/app/
RUN pip install --upgrade --requirement /usr/local/src/app/requirements.txt
COPY entrypoint.sh put.py usr/local/src/app/
RUN chmod +x /usr/local/src/app/entrypoint.sh &&\
    chmod +x /usr/local/src/app/put.py &&\
    mkdir -p /data
ENTRYPOINT ["/usr/local/src/app/entrypoint.sh"]
