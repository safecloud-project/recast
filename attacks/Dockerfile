FROM python:2.7.13

RUN apt-get update --quiet && apt-get install bash curl python-tk --yes --quiet
COPY attacks /usr/local/src/app/
COPY pyproxy/dispatcher.json /usr/local/src/app/
RUN pip install --quiet --requirement /usr/local/src/app/requirements.txt &&\
    chmod +x /usr/local/src/app/entrypoint.sh &&\
    chmod +x /usr/local/src/app/ATTACK.sh &&\
    chmod +x /usr/local/src/app/execute.py
WORKDIR /usr/local/src/app

ENTRYPOINT ["/usr/local/src/app/entrypoint.sh"]
