# Playcloud

An early repository for Safecloud's storage solution.

## Architecture

Playcloud is split in components:

* proxy - A web server taking requests on port 3000
* encoder-decoder - A enconding/decoding component
* storage - A database to saved the encoded data

## Requirements

* docker
* docker-compose

## Run the server

In order to start the server, run the following command in your terminal:

```bash
docker-compose up -d

```

This command will launch three containers. One named *proxy*, containing the web application accepting HTTP requests on port 3000, a second one named *dummy-coder* in charge of encoding/decoding and a last one name *redis* for storage.

## API

The server currently accepts 2 types of requests.

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


## Configuration

### Encoder/Decoder

The encoder/decoder's configuration can be overloaded by environment variables. These values can be added/modified in the erasure.env file which is loaded when starting the server up.
