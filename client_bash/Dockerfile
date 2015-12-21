FROM alpine
RUN apk update && apk add bash wget
COPY gen_random_data.sh /
COPY simple_bench.sh /
COPY random*.dat /
ENTRYPOINT /bin/bash /simple_bench.sh 10 1 "$PROXY_PORT_3000_TCP_ADDR:$PROXY_PORT_3000_TCP_PORT"
