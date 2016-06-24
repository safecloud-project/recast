FROM vyolin/alpine-maven:latest
RUN apk update && apk add bash git python && git clone https://github.com/dburihabwa/YCSB YCSB --quiet
WORKDIR /YCSB
ENV YCSB_HOME="/YCSB"
RUN mvn -pl com.yahoo.ycsb:playcloud-binding -am clean package
COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
