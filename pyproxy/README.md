# pyproxy

A python implementation of the playcloud proxy.

## Build
To build a docker image of the pyproxy, move to the root of the playcloud project and type in the following command:
```bash
docker build -f pyproxy/Dockerfile -t pyproxy .
```
## Run
Run with:
```bash
docker run --rm -ti -p 8080:8000 pyproxy
```

You can test the proxy using an HTTP client such as [cURL](https://curl.haxx.se) using the following commands.
To feth a file from the proxy, run:
```bash
curl -X GET http://<host>:<port>/<key>
```
To send a file to be stored by playcloud using the proxy, run:
```bash
curl -X PUT http://<host>:<port>/<key> -T <my-file>
```
To get information about the file stored in the system, run:
```bash
curl -X GET http://<host>:<port>/<key>/__meta
```

## Benchmark
You can benchmark the proxy using [apache bench](https://httpd.apache.org/docs/2.2/programs/ab.html).
To send 10 PUT requests to the server save cdf data (-e completion.tsv) and some gnuplot data (-g gnuplot_data.csv), run:  
```bash
ab -v 5 -n 10 -u <my-file-to-upload> -e <completion.tsv> -g <gnuplot_data.csv> http://<host>:<port>
```
