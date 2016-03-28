# py-proxy

A python implementation of the playcloud proxy.

## Build

Build with:
```bash
docker build -t playcloud/py-proxy .
```
## Run
Run with:
```bash
docker run --rm -ti -p 8080:8000 playcloud/py-proxy
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

## Benchmark
You can benchmark the proxy using [apache bench](https://httpd.apache.org/docs/2.2/programs/ab.html).
To send 10 PUT requests to the server save cdf data (-e completion.tsv) and some gnuplot data (-g gnuplot_data.csv), run:  
```bash
ab -v 5 -n 10 -u <my-file-to-upload> -e <completion.tsv> -g <gnuplot_data.csv> http://<host>:<port>
```
