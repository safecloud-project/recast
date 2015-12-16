FROM progrium/busybox
RUN opkg-install bash wget
COPY gen_random_data.sh .
COPY random*.dat .
COPY simple_bench.sh .
CMD ["/bin/bash"]
