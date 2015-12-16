FROM progrium/busybox
RUN opkg-install bash wget
COPY gen_random_data.sh /
COPY random*.dat /
COPY simple_bench.sh /
CMD /bin/bash /simple_bench.sh 10 1 "$PROXY_PORT_3000_TCP_ADDR:$PROXY_PORT_3000_TCP_PORT"
