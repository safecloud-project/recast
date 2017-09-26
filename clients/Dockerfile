FROM alpine
RUN apk update && apk add apache2-utils bash gcc git make musl-dev openssl-dev wget && \
    git clone https://github.com/giltene/wrk2 /wrk2 &&\
    cd /wrk2 &&\
    make &&\
    cp /wrk2/wrk /usr/local/bin && chmod +x /usr/local/bin/wrk
COPY ab_playcloud.sh gen_random_data.sh simple_bench.sh /
