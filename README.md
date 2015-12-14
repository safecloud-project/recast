# Playcloud

An early repository for Safecloud's storage component.

## Requirements

* docker
* docker-compose

## Run the server

In order to start the server, run the following command in your terminal:
```bash
docker-compose up -d

```

This command will launch two containers. One named *proxy*, containing the web application accepting HTTP requests on port 3000. An the other named *redis* containing a redis server.

## API

The server currently accepts 3 types of requests.

### GET /file

Retrieves a file from the storage component.
```bash
curl -X GET my-server:3000/my-file.txt -o my-file.txt
```

### PUT /file

Sends a file to the storage component.
```bash
curl -X PUT my-server:3000/my-file.txt -T my-file.txt
```

### DELETE /file

DELETES a filef rom the storage component.
```bash
curl -X DELETE my-server:3000/my-file.txt
```