"""
Unit tests for the files module
"""
import mock
import pytest

from pyproxy.metadata import BlockType, Files, MetaBlock, MetaDocument


################################################################################
# Testing helper classes and functions
class FakeRedisPipeline(object):
    def __init__(self):
        self.counter = 0

    def exists(self, path):
        self.counter += 1

    def hgetall(self, path):
        self.counter += 1

    def execute(self):
        data = [False for _ in xrange(self.counter)]
        self.counter = 0
        return data

def get_me_a_fake_redis_pipeline():
    return FakeRedisPipeline()

BLOCK_HASH = {
    "key": "key",
    "creation_date": "2017-01-01 00:00:00.42",
    "block_type": BlockType.DATA.name,
    "providers": "",
    "checksum": "0xCAFEBABE",
    "entangled_with": "[one]"
}

def mock_pipeline_get_block(path):
    return [BLOCK_HASH]
################################################################################

def test_files_get_raises_valueerror_when_path_is_None():
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    with pytest.raises(ValueError, match="path argument must be a valid non-empty string"):
        files.get(None)

def test_files_get_raises_valueerror_when_path_is_empty():
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    with pytest.raises(ValueError, match="path argument must be a valid non-empty string"):
        files.get("")

def test_files_get_raises_keyerror_when_path_not_in_files(monkeypatch):
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    monkeypatch.setattr(files.redis, "pipeline", get_me_a_fake_redis_pipeline)
    with pytest.raises(KeyError, match="path NonExistingKey not found"):
        files.get("NonExistingKey")

def test_files_get(monkeypatch):
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    def mock_pipeline_get(path):
        return [{
            "path": "path",
            "original_size": "0",
            "creation_date": "2017-01-01 00:00:00.42",
            "blocks": "",
            "providers": "",
            "block_type": BlockType.DATA.name,
            "entangling_blocks": "[]"
        }]
    monkeypatch.setattr(FakeRedisPipeline, "execute", mock_pipeline_get)
    monkeypatch.setattr(files.redis, "pipeline", get_me_a_fake_redis_pipeline)
    metadata = files.get("path")
    assert metadata.path == "path"

def test_files_put_raises_ValueError_if_metadata_is_None():
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    with pytest.raises(ValueError, match="metadata argument must be a valid Metadata object"):
        files.put("path", None)

def test_files_put_raises_ValueError_if_path_is_None():
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    with pytest.raises(ValueError, match="path argument must be a valid non-empty string"):
        files.put(None, MetaDocument("path"))

def test_files_put_raises_ValueError_if_path_is_empty():
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    with pytest.raises(ValueError, match="path argument must be a valid non-empty string"):
        files.put("", MetaDocument("path"))

def test_files_has_been_entangled_enough_raises_ValueError_if_block_key_is_None():
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    with pytest.raises(ValueError, match="path argument must be a valid non-empty string"):
        files.has_been_entangled_enough(None, 1)

def test_files_has_been_entangled_enough_raises_ValueError_if_block_key_is_empty():
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    with pytest.raises(ValueError, match="path argument must be a valid non-empty string"):
        files.has_been_entangled_enough("", 1)

def test_files_has_been_entangled_enough_raises_ValueError_if_pointers_is_lower_than_0():
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    with pytest.raises(ValueError, match="pointers argument must be a valid integer greater or equal to 0"):
        files.has_been_entangled_enough("path", -1)

def test_files_has_been_entangled_enough_raises_KeyError_if_block_key_does_not_match_any_existing_key(monkeypatch):
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    monkeypatch.setattr(files.redis, "pipeline", get_me_a_fake_redis_pipeline)
    with pytest.raises(KeyError, match="key {:s} not found".format("NonExistingKey")):
        files.has_been_entangled_enough("NonExistingKey", 2)

def test_files_has_been_entangled_enough(monkeypatch):
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    monkeypatch.setattr(FakeRedisPipeline, "execute", mock_pipeline_get_block)
    monkeypatch.setattr(files.redis, "pipeline", get_me_a_fake_redis_pipeline)
    assert files.has_been_entangled_enough("path", 0) is True
    assert files.has_been_entangled_enough("path", 1) is True
    assert files.has_been_entangled_enough("path", 2) is False

def test_files_list_blocks(monkeypatch):
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    def get_block_range(my_range, start, end):
        return ["block1", "block2", "block3"]
    monkeypatch.setattr(files.redis, "zrange", get_block_range)
    blocks = files.list_blocks()
    assert isinstance(blocks, list)
    assert len(blocks) == 3
    assert blocks == ["block1", "block2", "block3"]

def test_files_get_provider_with_None_as_provider():
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    with pytest.raises(ValueError, match="provider argument must be a non empty string"):
        files.get_blocks_from_provider(None)

def test_files_get_provider_with_empty_string_as_provider():
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    with pytest.raises(ValueError, match="provider argument must be a non empty string"):
        files.get_blocks_from_provider("")

def test_files_get_provider_returns_empty_list_if_no_blocks(monkeypatch):
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    def return_empty_list():
        return []
    monkeypatch.setattr(files, "list_blocks", return_empty_list)
    result = files.get_blocks_from_provider("NonExistingProvider")
    assert isinstance(result, list)
    assert not result

def test_files_get_provider_returns_empty_list_if_no_match(monkeypatch):
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    def return_block_names():
        return ["doc-00"]
    monkeypatch.setattr(files, "list_blocks", return_block_names)
    def return_fake_blocks(block_list):
        return [MetaBlock(key, providers=["FakeProvider"]) for key in block_list]
    monkeypatch.setattr(files, "get_blocks", return_fake_blocks)
    result = files.get_blocks_from_provider("NonExistingProvider")
    assert isinstance(result, list)
    assert not result

def test_files_get_provider(monkeypatch):
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        files = Files()
    def return_block_names():
        return ["doc-00"]
    monkeypatch.setattr(files, "list_blocks", return_block_names)
    def return_fake_blocks(block_list):
        return [MetaBlock(key, providers=["FakeProvider"]) for key in block_list]
    monkeypatch.setattr(files, "get_blocks", return_fake_blocks)
    result = files.get_blocks_from_provider("FakeProvider")
    assert isinstance(result, list)
    assert len(result) == 1
