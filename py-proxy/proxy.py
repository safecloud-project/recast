from bottle import route, run, request
import bottle

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 * 1024

@route("/<path>", method = "PUT")
def read_data(path):
    data = b""
    if request.body.readable():
        data = request.body.getvalue()
    return str(len(data))

run(host="0.0.0.0", port=8000)
