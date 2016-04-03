FROM pycoder-micro


COPY * /usr/local/src/app/

WORKDIR /usr/local/src/app/

ENV DRIVER xor
ENV NBLOCKS 3

ENTRYPOINT /usr/bin/python /usr/local/src/app/microbench_local_decode.py "4194304"  "1" > /results/microbench/decode/xor/microbench-decode-4MB-1.dat