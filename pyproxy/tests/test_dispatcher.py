import os

from ..safestore.providers.dispatcher import Dispatcher, Metadata, ProviderFactory
from ..safestore.providers.redis_provider import RedisProvider

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
    "providers": [{"type": "redis", "host": "127.0.0.1", "port": 6379}]
}

def test_dispatcher_store_returns_a_Metadata_object():
    dispatcher = Dispatcher(VALID_DISPATCHER_CONF)
    meta = dispatcher.put(DEFAULT_PATH, BLOCKS)
    assert type(meta) == Metadata
    assert meta.path == DEFAULT_PATH


def test_dispatcher_store_saves_Metadata_object():
    dispatcher = Dispatcher(VALID_DISPATCHER_CONF)
    meta = dispatcher.put(DEFAULT_PATH, BLOCKS)
    assert DEFAULT_PATH in dispatcher.files
    assert meta == dispatcher.files.get(DEFAULT_PATH)

def test_ProdiverFactory_get_factory_raises_execption_if_no_type_in_configuration():
    configuration_without_type = {}
    factory = ProviderFactory()
    try:
        factory.get_provider(configuration_without_type)
    except Exception as e:
        assert(e.message == "configuration parameter must have a type key-value pair")

def test_ProdiverFactory_get_factory_raises_execption_if_type_not_supported():
    configuration_with_unsupported_type = { "type": "anUnsupportedType" }
    factory = ProviderFactory()
    try:
        factory.get_provider(configuration_with_unsupported_type)
    except Exception as e:
        assert(e.message == "configuration type is not supported by the factory")

def test_ProdiverFactory_get_factory_returns_a_provider_if_supported():
    VALID_DISPATCHER_CONF = {"type": "redis", "host": "127.0.0.1", "port": 6379}
    factory = ProviderFactory()
    provider = factory.get_provider(VALID_DISPATCHER_CONF)
    assert isinstance(provider, RedisProvider)
