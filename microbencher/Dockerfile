FROM pycoder-micro


VOLUME results/microbench/encode/env/shamir

COPY * /usr/local/src/app/

WORKDIR /usr/local/src/app/

ENV DRIVER shamir
ENV NBLOCKS 3
ENV THRESHOLD 2

ENTRYPOINT /usr/bin/python /usr/local/src/app/microbench_local_encode.py "16777216"  "1" > /results/microbench/encode/env/shamir/microbench-encode-16MB-1.dat