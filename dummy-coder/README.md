# Playcloud dummy coder

A dummy encoding/decoding server for the playcloud project.
This server is built on the protocol defined in protocol.proto receiving a sequence of bytes and returning the same sequence of bytes to the client.
 
## Requirements

* Java 8
* Maven +3.x


## Build
To build a runnable jar, package the application using maven.
```bash
    mvn package
```
This command will produce a "fat jar" with all the project's dependencies.

## Run
Once the runnable jar has been packaged, the server can be started with the followning command:

```bash
   java -jar target/dummy-coder-1.0-SNAPSHOT-jar-with-dependencies.jar
```

This command will start the server listening on port 1234 for RPC calls defined in playcloud.proto.