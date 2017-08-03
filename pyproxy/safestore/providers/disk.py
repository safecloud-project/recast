"""
A storage provider that writes blocks to the filesystem
"""
import errno
import os
import shutil

def mkdir_p(path):
    """
    Recursively creates a directory tree.
    Shamelessly copied from https://stackoverflow.com/a/600612
    Args:
        path(str): Tree to create
    Returns:
        bool: True if the directory was created, False otherwise
    Raises:
        OSError: If an error occurs during the creation of the directories
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
    return os.path.isdir(path)

def clean_path(path):
    """
    Removes extra space and leading slash at the beginning of a path
    Args:
        path(str): Path to clean
    Returns:
        str: A cleaned up path
    """
    clean_key = path.strip()
    if clean_key[0] == '/':
        clean_key = clean_key[1:]
    return clean_key

class Disk(object):
    """
    A storage provider for playcloud that stores blocks on the disk
    """
    def __init__(self, folder="/data"):
        self.root_folder = folder

    def get(self, key):
        """
        Retrieves a block from the disk. Returns None if nothing found
        Args:
            key(str): Path to the block from the filsystem
        Returns:
            (byte|None): The data or None if the block does not exist
        """
        clean_key = clean_path(key)
        path = os.path.join(self.root_folder, clean_key)
        if not os.path.isfile(path):
            return None
        with open(path, "r") as handle:
            data = handle.read()
        return data

    def put(self, value, key):
        """
        Saves a block on the disk
        Args:
            value(bytes): The data to store
            key(str): Path to the block from the filsystem
        """
        clean_key = clean_path(key)
        path = os.path.join(self.root_folder, clean_key)
        mkdir_p(os.path.dirname(path))
        with open(path, "w") as handle:
            handle.write(value)

    def delete(self, key):
        """
        Deletes a block from the filesytem
        Args:
            key(str): Path to the block from the filsystem
        Returns:
            bool: True if the block was deleted, False otherwise.
        """
        clean_key = clean_path(key)
        path = os.path.join(self.root_folder, clean_key)
        if not os.path.exists(path):
            return False
        os.unlink(path)
        return not os.path.exists(path)

    def clear(self):
        """
        Removes all blocks from the filesystem
        Returns:
            bool: True if all data was deleted, False otherwise
        """
        for entry in os.listdir(self.root_folder):
            path = os.path.join(self.root_folder, entry)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

        return len(os.listdir(self.root_folder)) == 0
