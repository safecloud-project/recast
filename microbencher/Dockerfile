FROM pycoder-micro

COPY * /usr/local/src/app/

WORKDIR /usr/local/src/app/

ENV splitter  aes
ENV sec_measure  confd

ENTRYPOINT /usr/bin/python /usr/local/src/app/microbench_local_encode.py "67108864"  "1" > /results/microbench/encode/confd/aes/microbench-encode-64MB-1.dat