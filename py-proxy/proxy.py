# Simple Python-based PlayCloud proxy.py
from wsgiref import simple_server
import falcon

class FileResource(object):

    @staticmethod
    def on_get(req, resp):
        resp.status = falcon.HTTP_200
        resp.body = req.path
        return resp

    @staticmethod
    def on_put(req, resp):
        """Handles PUT requests"""
        try:
            data = req.stream.read()
            resp.status = falcon.HTTP_200
            resp.body = str(len(data)) + " bytes received"
            return resp
        except Exception as error:
            resp.status = falcon.HTTP_500
            resp.body = str(error)
            return resp

API = falcon.API(media_type="application/octet-stream")
API.add_route("/", FileResource())

if __name__ == "__main__":
    HTTPD = simple_server.make_server("0.0.0.0", 8000, API)
    HTTPD.serve_forever()
