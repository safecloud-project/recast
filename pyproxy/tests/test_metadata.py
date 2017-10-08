"""
Unit tests for the files module
"""
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

def test_files_get_raises_valueexception_when_path_is_None():
    files = Files()
    with pytest.raises(ValueError) as excinfo:
        files.get(None)
    assert excinfo.match("path argument must be a valid non-empty string")

def test_files_get_raises_valueexception_when_path_is_empty():
    files = Files()
    with pytest.raises(ValueError) as excinfo:
        files.get("")
    assert excinfo.match("path argument must be a valid non-empty string")

def test_files_get_raises_keyerror_when_path_not_in_files(monkeypatch):
    files = Files(host="127.0.0.1", port=6379)
    monkeypatch.setattr(files.redis, "pipeline", get_me_a_fake_redis_pipeline)
    with pytest.raises(KeyError) as excinfo:
        files.get("NonExistingKey")
    assert excinfo.match("path NonExistingKey not found")

def test_files_get(monkeypatch):
    files = Files(host="127.0.0.1", port=6379)
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
    files = Files()
    with pytest.raises(ValueError) as excinfo:
        files.put("path", None)
    assert excinfo.match("metadata argument must be a valid Metadata object")

def test_files_put_raises_ValueError_if_path_is_None():
    files = Files()
    with pytest.raises(ValueError) as excinfo:
        files.put(None, MetaDocument("path"))
    assert excinfo.match("path argument must be a valid non-empty string")

def test_files_put_raises_ValueError_if_path_is_empty():
    files = Files()
    with pytest.raises(ValueError) as excinfo:
        files.put("", MetaDocument("path"))
    assert excinfo.match("path argument must be a valid non-empty string")

def test_files_has_been_entangled_enough_raises_ValueError_if_block_key_is_None():
    files = Files()
    with pytest.raises(ValueError) as excinfo:
        files.has_been_entangled_enough(None, 1)
    assert excinfo.match("path argument must be a valid non-empty string")

def test_files_has_been_entangled_enough_raises_ValueError_if_block_key_is_empty():
    files = Files()
    with pytest.raises(ValueError) as excinfo:
        files.has_been_entangled_enough("", 1)
    assert excinfo.match("path argument must be a valid non-empty string")

def test_files_has_been_entangled_enough_raises_ValueError_if_pointers_is_lower_than_0():
    files = Files()
    with pytest.raises(ValueError) as excinfo:
        files.has_been_entangled_enough("path", -1)
    assert excinfo.match("pointers argument must be a valid integer greater or equal to 0")

def test_files_has_been_entangled_enough_raises_KeyError_if_block_key_does_not_match_any_existing_key(monkeypatch):
    files = Files()
    monkeypatch.setattr(files.redis, "pipeline", get_me_a_fake_redis_pipeline)
    with pytest.raises(KeyError) as excinfo:
        files.has_been_entangled_enough("NonExistingKey", 2)
    assert excinfo.match("key {:s} not found".format("NonExistingKey"))

def test_files_has_been_entangled_enough(monkeypatch):
    files = Files()
    monkeypatch.setattr(FakeRedisPipeline, "execute", mock_pipeline_get_block)
    monkeypatch.setattr(files.redis, "pipeline", get_me_a_fake_redis_pipeline)
    assert files.has_been_entangled_enough("path", 0) is True
    assert files.has_been_entangled_enough("path", 1) is True
    assert files.has_been_entangled_enough("path", 2) is False

def test_files_list_blocks(monkeypatch):
    files = Files()
    def get_block_range(my_range, start, end):
        return ["block1", "block2", "block3"]
    monkeypatch.setattr(files.redis, "zrange", get_block_range)
    blocks = files.list_blocks()
    assert type(blocks) is list
    assert len(blocks) == 3
    assert blocks == ["block1", "block2", "block3"]

def test_files_get_provider_with_None_as_provider():
    files = Files()
    with pytest.raises(ValueError) as excinfo:
        files.get_blocks_from_provider(None)
    assert excinfo.match("provider argument must be a non empty string")

def test_files_get_provider_with_empty_string_as_provider():
    files = Files()
    with pytest.raises(ValueError) as excinfo:
        files.get_blocks_from_provider("")
    assert excinfo.match("provider argument must be a non empty string")

def test_files_get_provider_returns_empty_list_if_no_blocks(monkeypatch):
    files = Files()
    def return_empty_list():
        return []
    monkeypatch.setattr(files, "list_blocks", return_empty_list)
    result = files.get_blocks_from_provider("NonExistingProvider")
    assert isinstance(result, list)
    assert len(result) == 0

def test_files_get_provider_returns_empty_list_if_no_match(monkeypatch):
    files = Files()
    def return_block_names():
        return ["doc-00"]
    monkeypatch.setattr(files, "list_blocks", return_block_names)
    def return_fake_blocks(block_list):
        return [MetaBlock(key, providers=["FakeProvider"]) for key in block_list]
    monkeypatch.setattr(files, "get_blocks", return_fake_blocks)
    result = files.get_blocks_from_provider("NonExistingProvider")
    assert isinstance(result, list)
    assert len(result) == 0

def test_files_get_provider(monkeypatch):
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
