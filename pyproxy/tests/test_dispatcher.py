import copy
import os

import mock
import pytest

from pyproxy.metadata import MetaDocument
from pyproxy.playcloud_pb2 import File
from pyproxy.safestore.providers.dispatcher import place, Dispatcher
from pyproxy.safestore.providers.dispatcher import ProviderFactory
from pyproxy.safestore.providers.redis_provider import RedisProvider

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

def test_dispatcher_store_returns_a_Metadata_object():
    conf = copy.deepcopy(VALID_DISPATCHER_CONF)
    del conf["providers"]["redis"]
    dispatcher = Dispatcher(conf)
    encoded_file = File()
    encoded_file.original_size = 0
    meta = dispatcher.put(DEFAULT_PATH, encoded_file)
    assert isinstance(meta, MetaDocument)
    assert meta.path == DEFAULT_PATH


def test_ProdiverFactory_get_factory_raises_execption_if_no_type_in_configuration():
    configuration_without_type = {}
    factory = ProviderFactory()
    try:
        factory.get_provider(configuration_without_type)
    except Exception as error:
        assert error.message == "configuration parameter must have a type key-value pair"


def test_ProdiverFactory_get_factory_raises_execption_if_type_not_supported():
    configuration_with_unsupported_type = {"type": "anUnsupportedType"}
    factory = ProviderFactory()
    try:
        factory.get_provider(configuration_with_unsupported_type)
    except Exception as error:
        assert error.message == "configuration type is not supported by the factory"


def test_ProdiverFactory_get_factory_returns_a_provider_if_supported():
    valid_provider_conf = {"type": "redis", "host": "127.0.0.1", "port": 6379}
    factory = ProviderFactory()
    provider = factory.get_provider(valid_provider_conf)
    assert isinstance(provider, RedisProvider)


def test_place_raises():
    with pytest.raises(ValueError):
        place(-1, ["a"], 1)

    with pytest.raises(ValueError):
        place(2, None, 1)

    with pytest.raises(ValueError):
        place(2, ["a"], -1)


def test_Dispatcher_list_files():
    conf = copy.deepcopy(VALID_DISPATCHER_CONF)
    del conf["providers"]["redis"]
    dispatcher = Dispatcher(conf)
    with mock.patch("pyproxy.safestore.providers.dispatcher.Files.values", return_value=[]):
        result = dispatcher.list()
    assert isinstance(result, list)
    assert len(result) == 0
    path = "key"
    metadata = MetaDocument(path)
    with mock.patch("pyproxy.safestore.providers.dispatcher.Files.values", return_value=[metadata]):
        result = dispatcher.list()
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], MetaDocument)
    assert result[0].path == path
