# Simple Python-based PlayCloud proxy.py
from wsgiref import simple_server
import falcon

class Proxy:
    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status

    def on_post(self, req, resp):
        """Handles POST requests"""
        resp.status = falcon.HTTP_201  # This is the default status        


# falcon.API instances are callable WSGI apps
app = falcon.API()
proxy = Proxy()
# proxy will handle all requests to the '/' URL path
app.add_route('/', proxy)

# Useful for debugging problems in your API; works with pdb.set_trace()
if __name__ == '__main__':
    httpd = simple_server.make_server('0.0.0.0', 8000, app)
    httpd.serve_forever()