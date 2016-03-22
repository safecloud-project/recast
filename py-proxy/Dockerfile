from gerasim13/alpine-pypy
COPY * /usr/local/src/app/
RUN pip install --upgrade --requirement /usr/local/src/app/requirements.txt
EXPOSE 8000
ENTRYPOINT ["pypy", "/usr/local/src/app/proxy.py"]
