"""
Tests for the proxy_service module
"""
import mock
import pytest

from pyproxy.files import BlockType, Files, MetaBlock, Metadata
from pyproxy.proxy_service import get_random_blocks

class MockDispatcher(object):
    def __init__(self):
        pass

    def get_random_blocks(self, blocks):
        return [(MetaBlock, "0xCAFE") for i in range(blocks)]

@mock.patch("pyproxy.proxy_service.get_dispatcher_instance")
def test_get_random_blocks_lower_than_zero(mock_get_dispatcher_instance):
    """
    Test if the function expectedly raises an error of the number of blocks is below 0
    """
    with pytest.raises(ValueError) as error:
        get_random_blocks(-1)
    mock_get_dispatcher_instance.assert_not_called()
    assert "argument blocks cannot be lower or equal to 0" in error.value

@mock.patch("pyproxy.proxy_service.get_dispatcher_instance")
def test_get_random_blocks_equal_to_zero(mock_get_dispatcher_instance):
    """
    Test if the function expectedly raises an error of the number of blocks is equal to 0
    """
    with pytest.raises(ValueError) as error:
        get_random_blocks(0)
    mock_get_dispatcher_instance.assert_not_called()
    assert "argument blocks cannot be lower or equal to 0" in error.value

@mock.patch("pyproxy.proxy_service.get_dispatcher_instance")
def test_get_random_blocks_returns_a_list_of_length_blocks(mock_get_dispatcher_instance):
    """
    Test if the function expectedly returns the appropriate number of blocks
    """
    mock_get_dispatcher_instance.return_value = MockDispatcher()
    result = get_random_blocks(1)
    mock_get_dispatcher_instance.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
