#! /usr/bin/env python
"""
A FUSE translation of the playcloud proxy API.
"""

import copy
import errno
import json
import stat
import sys
import time
import urllib3

import dateutil.parser
import requests

import fuse

class HTTPClient(object):
    """
    An HTTP client to store and retrieve files from playcloud's proxy
    """
    def __init__(self, host="127.0.0.1", port=3000, protocol="http"):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.http = urllib3.PoolManager()

    def get(self, filename):
        """
        Retrieves a file from the playcloud's proxy.
        Args:
            filename(str): Name of the file to retrieve
        Returns:
            str: The content of the file requested
        """
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

    def put(self, path, data):
        """
        Send data to the playcloud proxy
        Args:
            path(str): key under which the file should be stored
            data(str): Data to store
        Args:
            str: The key under which the file was stored
        """
        url = self.protocol + "://" + self.host + ":" + str(self.port) + path
        response = requests.put(url, data=data)
        return response.text

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

def convert_list_entry_to_stat(entry):
    """
    Converts a list entry from the proxy API to a dictionary that would be
    returned by the unix stat command.
    Args:
        entry(dict): A dictionary returned from the proxy API containing a
                     file's metadata
    Returns:
        dict: A mapping of API list entry to a stat dictionary
    """
    creation_date = int(dateutil.parser.parse(entry["creation_date"]).strftime("%s"))
    stat_entry = copy.deepcopy(ROOT_STAT)
    stat_entry["st_atime"] = time.time()
    stat_entry["st_ctime"] = creation_date
    stat_entry["st_mtime"] = creation_date
    stat_entry["st_size"] = entry["original_size"]
    stat_entry["st_mode"] = ST_MODES["OTHER_FILES"]
    return stat_entry

def prepare_path(path):
    """
    Takes a path given by FUSE and trims it properly
    Args:
        path(str): Original path
    Returns:
        str: Trimmed path
    """
    if path.startswith("/"):
        return path
    return "/" + path


class FileNotOpenException(Exception):
    """
    An exception to raise when a request to read a file is sent on a file that is not opened
    """
    pass

class FuseClient(fuse.Operations):
    """
    A FUSE translation of the playcloud's proxy API
    """
    def __init__(self):
        self.client = HTTPClient(host="127.0.0.1", port=3000)
        self.files = {"/": ROOT_STAT}
        self.file_counter = 1000
        self.files_open = set()
        self.read_buffers = {}
        self.write_buffers = {}

    def readdir(self, path, fh):
        """
        Reads the content of a directory and returns the list of filenames
        Args:
            path(str): Path to the file
            fh(int): File descriptor
        Yields:
            list(str): A list of filenames for the files present in the document
        """
        entries = self.client.list()
        dirents = [".", ".."]
        for entry in entries:
            path = entry["path"]
            self.files[prepare_path(path)] = convert_list_entry_to_stat(entry)
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
        # If the file has been entered in self.files
        clean_path = prepare_path(path)
        if self.files.has_key(clean_path):
            return self.files[clean_path]
        # Otherwise try to get fresh metadata from the system
        metadata = self.client.get_metadata(path)
        # If the file does not exist return an empty dictionary
        if metadata is None:
            raise fuse.FuseOSError(errno.ENOENT)
        stat_entry = convert_list_entry_to_stat(metadata)
        self.files[clean_path] = stat_entry
        return stat_entry

    def open(self, path, flags):
        """
        Returns a file descriptor if the requested file exists and is not black
        listed.
        Args:
            path(str): Path to the file that has to be open
        Returns:
            int: A positive integer if the file could be opened or a negative one otherwise
        """
        if self.client.get_metadata(prepare_path(path)) is None:
            raise fuse.FuseOSError(errno.ENOENT)
        fd = self.file_counter
        self.files_open.add(fd)
        self.file_counter += 1
        return fd

    def release(self, path, fh):
        """
        Releases a file
        Args:
            path(str): Path to the file
            fh(int): File descriptor
        """
        key = str(fh)
        if key in self.read_buffers:
            self.read_buffers.pop(key)
        if key in self.write_buffers:
            data = self.write_buffers[key]
            self.client.put(prepare_path(path), data)
            self.write_buffers.pop(key)
        self.files_open.remove(fh)
        self.files.pop(path)


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
        if fh not in self.files_open:
            raise FileNotOpenException(path + " (fh = " + str(fh) + ") is not open")
        key = str(fh)
        if key not in self.read_buffers:
            self.read_buffers[key] = self.client.get(prepare_path(path))
        data_buffer = self.read_buffers[key][offset: offset + size]
        return data_buffer

    def create(self, path, mode):
        """
        Creates a new file entry in self.files and "opens" a new file for writing.
        Args:
            path(str): Path to the new file
            mode(int): Flags describing the open mode
        Returns:
            int: a file descriptor for the new file
        """
        creation_date = time.time()
        self.files[prepare_path(path)] = {
            "st_mode": (stat.S_IFREG | mode),
            "st_nlink": 1,
            "st_size": 0,
            "st_ctime": creation_date,
            "st_mtime": creation_date,
            "st_atime": creation_date
        }
        fd = self.file_counter
        self.files_open.add(fd)
        self.file_counter += 1
        return fd

    def getxattr(self, path, name, position=0):
        """
        Returns a special attribute from the stat structure. Mostly here for
        compatibility reasons.
        Args:
            path(str): Path to the file
            name(str): Name of the attribute to recover
        Returns:
            str: the value behind the attribute
        """
        attrs = self.files[prepare_path(path)].get("attrs", {})
        if attrs.has_key(name):
            return attrs[name]
        return ""       # Should return ENOATTR

    def write(self, path, data, offset, fh):
        """
        Write data to a buffer for to store in the system.
        Args:
            path(str): Path of the file
            size(int): Amount of data to write to the file in bytes
            offset(int): Position of the first byte to write in the file
        Returns:
            int: Number of bytes written to the buffer
        """
        key = str(fh)
        if self.write_buffers.has_key(key):
            self.write_buffers[key] += data
        else:
            self.write_buffers[key] = data
        return len(data)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: %s <mountpoint>" % sys.argv[0])
        exit(0)
    CLIENT = FuseClient()
    MOUNT_POINT = sys.argv[1]
    fuse.FUSE(CLIENT, MOUNT_POINT, nothreads=True, foreground=True)
