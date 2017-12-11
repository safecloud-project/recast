import copy
import os

import mock
import pytest

import pyproxy.metadata as metadata
import pyproxy.playcloud_pb2 as playcloud_pb2
import pyproxy.safestore.providers.dispatcher as dsp
import pyproxy.safestore.providers.redis_provider as redis

DEFAULT_PATH = "hello"
LENGTH = 128
DATA = os.urandom(LENGTH)
BLOCKS = []
STEP = LENGTH / 8
for i in range(0, LENGTH, STEP):
    BLOCKS.append(DATA[i:i + STEP])

VALID_DISPATCHER_CONF = {
    "entanglement": {
        "enabled": False
    },
    "providers": {"redis": {"type": "redis", "host": "127.0.0.1", "port": 6379}}
}

## Dispatcher tests
def test_dispatcher_store_returns_a_Metadata_object():
    conf = copy.deepcopy(VALID_DISPATCHER_CONF)
    del conf["providers"]["redis"]
    with mock.patch("socket.gethostbyname", return_value="127.0.0.1"):
        dispatcher = dsp.Dispatcher(conf)
    encoded_file = playcloud_pb2.File()
    encoded_file.original_size = 0
    meta = dispatcher.put(DEFAULT_PATH, encoded_file)
    assert isinstance(meta, metadata.MetaDocument)
    assert meta.path == DEFAULT_PATH

@mock.patch("socket.gethostbyname", return_value="127.0.0.1")
def test_Dispatcher_list_files(mocked_socket):
    conf = copy.deepcopy(VALID_DISPATCHER_CONF)
    del conf["providers"]["redis"]
    dispatcher = dsp.Dispatcher(conf)
    with mock.patch("pyproxy.metadata.Files.values", return_value=[]):
        result = dispatcher.list()
    assert isinstance(result, list)
    assert len(result) == 0
    path = "key"
    expected_metadata = metadata.MetaDocument(path)
    with mock.patch("pyproxy.metadata.Files.values", return_value=[expected_metadata]):
        result = dispatcher.list()
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], metadata.MetaDocument)
    assert result[0].path == path

# ProviderFactory tests
def test_ProdiverFactory_get_factory_raises_exception_if_configuration_is_not_a_dict():
    non_valid_elements = [
        "string",
        "c",
        42,
        3.1419,
        [],
        None
    ]
    factory = dsp.ProviderFactory()
    for elt in non_valid_elements:
        try:
            factory.get_provider(elt)
            error_msg = "get_provider should have raise a ValueError for type {:s}".format(type(elt))
            pytest.fail(error_msg)
        except ValueError as e:
            assert e.message == "configuration parameter must be a non empty dictionary"

def test_ProdiverFactory_get_factory_raises_exception_if_no_type_in_configuration():
    configuration_without_type = {"key": "value"}
    factory = dsp.ProviderFactory()
    try:
        factory.get_provider(configuration_without_type)
    except ValueError as e:
        assert e.message == "configuration parameter must have a type key-value pair"

def test_ProdiverFactory_get_factory_raises_exception_if_type_not_supported():
    configuration_with_unsupported_type = {"type": "anUnsupportedType"}
    factory = dsp.ProviderFactory()
    try:
        factory.get_provider(configuration_with_unsupported_type)
    except ValueError as e:
        assert e.message == "configuration type 'anUnsupportedType' is not supported by the factory"

def test_ProdiverFactory_get_factory_returns_a_provider_if_supported():
    valid_provider_conf = {"type": "redis", "host": "127.0.0.1", "port": 6379}
    factory = dsp.ProviderFactory()
    provider = factory.get_provider(valid_provider_conf)
    assert isinstance(provider, redis.RedisProvider)

## place tests
def test_place_raises():
    with pytest.raises(ValueError):
        dsp.place(-1, ["a"], 1)

    with pytest.raises(ValueError):
        dsp.place(2, None, 1)

    with pytest.raises(ValueError):
        dsp.place(2, ["a"], -1)

