import copy
import json
import time

import fuse
import dateutil.parser
import urllib3

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

    def get_metadata(self, filename):
        """
        Returns a dictionary with the file's metadata
        Args:
            filename(string): path to the file
        Returns:
            dict: A dictionary with files metadata
        """
        if filename is None or len(filename) == 0:
            raise ValueError("filename argument must have a value")
        url = self.protocol + "://" + self.host + ":" + str(self.port) + filename + "/__meta"
        response = self.http.request("GET", url)
        if response.status == 404:
            return None
        metadata = json.loads(response.data)
        return metadata

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


ROOT_STAT = {
    "st_atime": time.time(),
    "st_ctime": time.time(),
    "st_mtime": time.time(),
    "st_mode": ST_MODES["ROOT_DIRECTORY"],
    "st_nlink": 1,
    "st_size": 4096,
    "st_uid": 1000,
    "st_gid": 1000
}

# A list of files for which no access should ever be given
FILES_BLACKLIST = [
    "/.Trash",
    "/.Trash-1000"
]

class FuseClient(fuse.Operations):

    def __init__(self):
        self.client = HTTPClient(host="127.0.0.1", port=3000)
        self.files = {}
        self.file_counter = 1000

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
        """
        Returns metadata that can be used by unix's stat or ls.
        The function returns empty dictionary in the case where the path is ./Trash or ./Trash-1000
        Args:
            path(string): Path to the file
        Returns:
            dict: A dictionary with values matching the file requested
        """
        # Ignore the trash directory that fuse looks up on mount
        if path in FILES_BLACKLIST:
            return {}
        # If stat on root, then return the constant ROOT_STAT
        if path == "/":
            return ROOT_STAT
        #Otherwise try to get fresh metadata from the system
        metadata = self.client.get_metadata(path)
        # If the file does not exist return an empty dictionary
        if metadata is None:
            return {}
        creation_date = int(dateutil.parser.parse(metadata["creation_date"]).strftime("%s"))
        stat = copy.deepcopy(ROOT_STAT)
        stat["st_atime"] = time.time()
        stat["st_ctime"] = creation_date
        stat["st_mtime"] = creation_date
        stat["st_size"] = metadata["original_size"]
        stat["st_mode"] = ST_MODES["OTHER_FILES"]
        return stat

    def open(self, path, flags):
        """
        Returns a file descriptor if the requested file exists and is not black
        listed.
        Args:
            path(str): Path to the file that has to be open
        Returns:
            int: A positive integer if the file could be opened or a negative one otherwise
        """
        if path in FILES_BLACKLIST:
            return -1
        if self.client.get_metadata(path) is None:
            return -1
        fd = self.file_counter
        self.file_counter += 1
        return fd


    def read(self, path, size, offset, fh):
        """
        Read data from a file stored in the system.
        Args:
            path(str): Path of the file
            size(int): Amount of data to read from the file in bytes
            offset(int): Position of the first byte to read in the file
        Returns:
            str: Data read from the file
        """
        #TODO Cache data rather than reading the entire file on every call
        data = self.client.get(path)
        data_buffer = data[offset: offset + size]
        return data_buffer

if __name__ == "__main__":
    CLIENT = FuseClient()
    fuse.FUSE(CLIENT, "/tmp/fuse", nothreads=True, foreground=True)
