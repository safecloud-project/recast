FROM java:8

# Install maven
RUN wget http://mirror.easyname.ch/apache/maven/maven-3/3.3.9/binaries/apache-maven-3.3.9-bin.tar.gz
RUN tar xf apache-maven-3.3.9-bin.tar.gz
RUN rm apache-maven-3.3.9-bin.tar.gz
RUN mv apache-maven-3.3.9 /usr/share/maven
RUN ln -s /usr/share/maven/bin/mvn /usr/local/bin/mvn

# Copy and build the sources
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN mvn package

# Launch the server on container start-up
EXPOSE 1234
ENTRYPOINT ["/usr/bin/java", "-jar", "/usr/src/app/target/dummy-coder-1.0-SNAPSHOT-jar-with-dependencies.jar"]
