"""
A module with entanglement utilities
"""
import hashlib
import json
import math
import os
import struct

from pyproxy.metadata import compute_block_key, Files
from pyproxy.coder_client import CoderClient

HEADER_DELIMITER = chr(29)

class FragmentHeader(object):
    """
    Native python representation of a fragment_header_t struct used by liberasurecode
    """
    HEADER_FORMAT = "=IIIxxxxxxxxx"
    def __init__(self, blob):
        self.metadata = FragmentMetadata(blob[:59])
        extracted = struct.unpack(FragmentHeader.HEADER_FORMAT, blob[59:])
        self.magic = extracted[0]
        self.libec_version = extracted[1]
        self.metadata_checksum = extracted[2]

    def pack(self):
        """
        Returns a binary representation of the fragment header
        Return:
            bytes: A representation of the fragment header
        """
        blob = self.metadata.pack()
        blob += struct.pack(FragmentHeader.HEADER_FORMAT,
                            self.magic,
                            self.libec_version,
                            self.metadata_checksum)
        return blob

    def __repr__(self):
        return "FragmentHeader(" +\
        "metadata=" + str(self.metadata) +\
        ", magic=" + str(self.magic) +\
        ", libec_version=" + str(self.libec_version) +\
        ", metadata_checksum=" + str(self.metadata_checksum) +\
        ")"

    def __eq__(self, other):
        return isinstance(other, FragmentHeader) and \
               self.metadata == other.metadata and \
               self.magic == other.magic and \
               self.libec_version == other.libec_version and \
               self.metadata_checksum == other.metadata_checksum

class FragmentMetadata(object):
    """
    Native python representation of a fragment_metadata_t struct used by liberasurecode
    """
    METADATA_FORMAT = "=IIIQBIIIIIIIIBBI"
    def __init__(self, blob):
        extracted = struct.unpack(FragmentMetadata.METADATA_FORMAT, blob)
        self.index = extracted[0]
        self.size = extracted[1]
        self.fragment_backend_metadata_size = extracted[2]
        self.orig_data_size = extracted[3]
        self.checksum_type = extracted[4]
        self.checksum = [extracted[i] for i in xrange(5, 13, 1)]
        self.checksum_mismatch = extracted[13]
        self.backend_id = extracted[14]
        self.backend_version = extracted[15]

    def pack(self):
        """
        Returns a binary representation of the fragment metadata
        Return:
            bytes: A representation of the fragment metadata
        """
        return struct.pack(FragmentMetadata.METADATA_FORMAT,
                           self.index,
                           self.size,
                           self.fragment_backend_metadata_size,
                           self.orig_data_size,
                           self.checksum_type,
                           self.checksum[0],
                           self.checksum[1],
                           self.checksum[2],
                           self.checksum[3],
                           self.checksum[4],
                           self.checksum[5],
                           self.checksum[6],
                           self.checksum[7],
                           self.checksum_mismatch,
                           self.backend_id,
                           self.backend_version)

    def __repr__(self):
        return "FragmentMetadata(" + \
        "index=" + str(self.index) + \
        ", size=" + str(self.size) + \
        ", fbmds=" + str(self.fragment_backend_metadata_size) +\
        ", orig_data_size=" + str(self.orig_data_size) + \
        ", checksum_type=" + str(self.checksum_type) + \
        ", checksum=" + str(len(self.checksum)) + \
        ", checksum_mismatch=" + str(self.checksum_mismatch) + \
        ", backend_id=" + str(self.backend_id) + \
        ", backend_version=" + str(self.backend_version) + \
        ")"

    def __eq__(self, other):
        """
        Checks the equality of two FragmentMetadata objects
        """
        return isinstance(other, FragmentMetadata) and \
               self.index == other.index and \
               self.size == other.size and \
               self.fragment_backend_metadata_size == other.fragment_backend_metadata_size and \
               self.orig_data_size == other.orig_data_size and \
               self.checksum_type == other.checksum_type and \
               self.checksum_mismatch == other.checksum_mismatch and \
               self.backend_id == other.backend_id and \
               self.backend_version == other.backend_version

def get_block_metadata(path, index):
    """
    Returns the block metadata
    Args:
        path(str): Path to the file
        index(int): Index of the block in the file
    Returns:
        MetaBlock: Block metadata
    """
    files = Files()
    key = compute_block_key(path, index)
    return files.get_block(key)


def find_pointing_documents(path, index):
    """
    Returns the Metadata of the documents that use a given block as a pointer.
    Args:
        path(str): Path to the file
        index(int): Index of the block in the file
    Returns:
        list(Metadata): List of documents that used the block as a pointer
    """
    block_metadata = get_block_metadata(path, index)
    files = Files()
    pointing_documents = files.get_files(block_metadata.entangled_with)
    return pointing_documents


def get_position_in_codeword(file_metadata, block_metadata):
    """
    Retrieves the position of the block in the file's complete codeword in
    relation with the index of the parity being 0
    Args:
        file_metadata(Metadata): File metadata
        block_metadata(MetaBlock): Block metadata
    Returns:
        int: Position of the block in the file's codeword considering that the
             first parity block is located at 0
    """
    for index, block in enumerate(file_metadata.entangling_blocks):
        key = compute_block_key(block[0], block[1])
        if key == block_metadata.key:
            return index - len(file_metadata.entangling_blocks)
    raise Exception("Could not find the block in the list of entangling blocks")


def split_strip_header(strip_data):
    """
    Breaks down a strip returned by the coder in 3 parts:
     * the entanglement header
     * the original size of the data
     * the pyeclib fragment header
    Args:
        strip_data(bytes): The full strip as returned by the coder
    Returns:
        (list((str, int)), int, FragmentHeader): The strip's header
    """
    start = strip_data.find(HEADER_DELIMITER)
    end = strip_data.find(HEADER_DELIMITER, start + 1)
    return (
        strip_data[:start],
        int(strip_data[start + len(HEADER_DELIMITER):end]),
        FragmentHeader(strip_data[end + len(HEADER_DELIMITER):end + len(HEADER_DELIMITER) + 80])
    )

def get_fragment(strip_data):
    """
    Returns the actual data part of the pyeclib fragment
    Args:
        strip_data(bytes): The full strip as returned by the coder
    Returns:
        bytes: The data part of the fragment
    """
    start = strip_data.find(HEADER_DELIMITER) + len(HEADER_DELIMITER)
    end = strip_data.find(HEADER_DELIMITER, start) + len(HEADER_DELIMITER)
    data = strip_data[end + 80:]
    return data

def reconstruct_with_RS(path, indices):
    """
    Args:
        path(str): Path of the file the blocks belongs to
        indices(list(int)): Indices of the blocks to repair
    Returns:
        dict(int, bytes): The reconstructed blocks
    """
    if not isinstance(path, str) or not path:
        raise ValueError("path argument must be a non empty string")
    if not isinstance(indices, list):
        raise ValueError("indices argument must be a list")
    client = CoderClient()
    reconstructed_blocks = client.reconstruct(path, indices)
    return {index: reconstructed_blocks[index].data for index in reconstructed_blocks}

def reconstruct_as_pointer(path, index):
    """
    Reconstruct a block by reassembling a codeword it was part of and plucking it
    from the result.
    Args:
        path(str): Path to the file the block belongs to
        index(int): Index of the block
    Returns:
        bytes: The constructed block
    Raises:
        ValueError: If path is not a string or is empty or if the index is
                    negative
        RuntimeError: If the block has never been pointed at
    """
    if not isinstance(path, str) or not path:
        raise ValueError("path argument must be a non empty string")
    if not isinstance(index, int) or index < 0:
        raise ValueError("index argument must be an integer greater or equal to 0")
    metablock = get_block_metadata(path, index)
    documents = find_pointing_documents(path, index)
    if not documents:
        raise RuntimeError("Could not find any pointing document")
    with open(os.path.join(os.path.dirname(__file__), "..", "dispatcher.json"), "r") as handle:
        entanglement_configuration = json.load(handle)["entanglement"]["configuration"]
    source_blocks = entanglement_configuration["s"]
    pointer_blocks = entanglement_configuration["t"]
    offset = source_blocks  + pointer_blocks
    files = Files()
    for document in documents:
        index_to_reconstruct = get_position_in_codeword(document, metablock)
        coder_client = CoderClient()
        reconstructed_block = coder_client.reconstruct(document.path, [index_to_reconstruct])[index_to_reconstruct].data
        elements = split_strip_header(reconstructed_block)
        fragment_header = elements[2]
        metadata = files.get(path)
        fragment_header.metadata.index = offset + index
        fragment_size = int(math.ceil(metadata.original_size / float(source_blocks)))
        if (fragment_size % 2) == 1:
            fragment_size += 1
        fragment_header.metadata.size = fragment_size
        fragment_header.metadata.orig_data_size = fragment_size * (offset)
        brand_new = json.dumps(metadata.entangling_blocks) + HEADER_DELIMITER + \
                    str(metadata.original_size) + HEADER_DELIMITER + \
                    fragment_header.pack() + \
                    get_fragment(reconstructed_block)
        brand_new = brand_new[:metablock.size]
        computed_checksum = hashlib.sha256(brand_new).digest()
        if computed_checksum == metablock.checksum:
            return brand_new
    raise RuntimeError("Could not reconstruct {:s} from pointing documents".format(metablock.key))
