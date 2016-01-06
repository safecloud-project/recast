# Java proxy

An HTTP server for the playcloud project that receives request to get, store or delete files.

## Requirements

* Java 8
* Maven 3

## Build
To build a runnable jar, package the application using maven.
```bash
mvn package
```

## Run
Once the runnable jar has been packaged, the server can be started with the followning command:

```bash
mvn spring-boot:run
```

This command will start the server listening on port 8080 for HTTP requests.

