from safestore.providers.dispatcher import ProviderFactory
from safestore.providers.redis_provider import RedisProvider

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
    valid_configuration = {"type": "redis", "host": "127.0.0.1", "port": 6379}
    factory = ProviderFactory()
    provider = factory.get_provider(valid_configuration)
    assert isinstance(provider, RedisProvider)
