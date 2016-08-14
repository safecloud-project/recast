"""
Tests for the proxy_client module
"""
import mock

import pytest

from proxy_client import ProxyClient
from playcloud_pb2 import BlockReply, Strip

class FakeProxyStub():
    def __init__(self, channel=None):
        pass

    def GetRandomBlocks(self, request, context):
        reply = BlockReply()
        strips = [Strip() for i in range(request.blocks)]
        reply.strips.extend(strips)
        return reply

@mock.patch("proxy_client.beta_create_Proxy_stub", return_value=FakeProxyStub())
def test_get_random_blocks_lower_than_zero(mock_beta_create_proxy_stub):
    """
    Test if GetRandomBlocks method raises an error when given a negative blocks argument
    """
    client = ProxyClient()
    with pytest.raises(ValueError) as e:
        client.get_random_blocks(-1)
    assert "argument blocks cannot be lower or equal to 0" in e.value

@mock.patch("proxy_client.beta_create_Proxy_stub", return_value=FakeProxyStub())
def test_get_random_blocks_equal_to_zero(mock_beta_create_proxy_stub):
    """
    Test if GetRandomBlocks method raises an error when given 0 as a blocks argument
    """
    client = ProxyClient()
    with pytest.raises(ValueError) as e:
        client.get_random_blocks(0)
    assert "argument blocks cannot be lower or equal to 0" in e.value

@mock.patch("proxy_client.beta_create_Proxy_stub", return_value=FakeProxyStub())
def test_get_random_blocks_returns_a_list_of_strips(mock_beta_create_proxy_stub):
    """
    Test if the proxy returns the expected number of blocks when receiving a valid reply from the service
    """
    client = ProxyClient()
    result = client.get_random_blocks(1)
    assert isinstance(result, list)
    assert len(result) == 1
    first_element = result[0]
    assert isinstance(first_element, Strip)
