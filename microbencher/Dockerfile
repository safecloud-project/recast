FROM pycoder-micro

COPY * /usr/local/src/app/

WORKDIR /usr/local/src/app/

ENV DRIVER xor
ENV NBLOCKS 3

ENTRYPOINT /usr/bin/python /usr/local/src/app/microbench_local_encode.py "4194304"  "100" > /results/microbench/encode/xor/microbench-encode-4MB-1.dat