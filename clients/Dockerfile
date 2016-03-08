FROM alpine
RUN apk update && apk add bash wget apache2-utils
COPY gen_random_data.sh /
COPY simple_bench.sh /
COPY ab_playcloud.sh /
