import json
import time

import urllib3
from fuse import FUSE, Operations

class HTTPClient(object):
    """
    An HTTP client to store and retrieve files from playcloud
    """
    def __init__(self, host="127.0.0.1", port=3000, protocol="http"):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.http = urllib3.PoolManager()

    def get(self, filename):
        if filename is None or len(filename) == 0:
            raise ValueError("filename argument must have a value")
        url = self.protocol + "://" + self.host + ":" + str(self.port) + filename
        response = self.http.request("GET", url)
        return response.data

    def list(self):
        """
        List files stored in playcloud
        Returns:
            list(string): A list of the files stored in the system
        """
        url = self.protocol + "://" + self.host + ":" + str(self.port) + "/"
        response = self.http.request("GET", url)
        files = json.loads(response.data)['files']
        return files

ST_MODES = {
    "OTHER_FILES": 33188,
    "ROOT_DIRECTORY": 16893
}

class FuseClient(Operations):

    def __init__(self):
        self.client = HTTPClient(host="127.0.0.1", port=3000)
        self.files = {}

    def readdir(self, path, fh):
        entries = self.client.list()
        dirents = [".", ".."]
        for entry in entries:
            path = entry["path"]
            self.files[path] = entry
            dirents.append(path)
        for ent in dirents:
            yield ent

    def getattr(self, path, fh=None):
        stat = {}
        stat["st_atime"] = time.time()
        stat["st_ctime"] = time.time()
        stat["st_mtime"] = time.time()
        stat["st_nlink"] = 1
        stat["st_size"] = 4096
        stat["st_uid"] = 1000
        stat["st_gid"] = 1000
        if path == "/":
            stat["st_mode"] = ST_MODES["ROOT_DIRECTORY"]
        else:
            stat["st_mode"] = ST_MODES["OTHER_FILES"]
        return stat

if __name__ == "__main__":
    CLIENT = FuseClient()
    FUSE(CLIENT, "/tmp/fuse", nothreads=True, foreground=True)
