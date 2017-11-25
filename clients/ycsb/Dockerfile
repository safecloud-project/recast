FROM vyolin/alpine-maven:latest
RUN apk update && apk add bash git python && git clone https://github.com/dburihabwa/YCSB YCSB --quiet
WORKDIR /YCSB
ENV YCSB_HOME="/YCSB"
RUN mvn -pl com.yahoo.ycsb:playcloud-binding -am clean package
COPY entrypoint.sh entrypoint_no_load.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/entrypoint_no_load.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
