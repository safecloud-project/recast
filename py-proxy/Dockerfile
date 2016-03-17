from gerasim13/alpine-pypy
RUN pip install --upgrade pip falcon gunicorn
COPY proxy.py /
EXPOSE 8080:8000
ENTRYPOINT ["pypy", "proxy.py"]
