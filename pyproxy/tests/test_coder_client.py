"""
Unit tests for the pyproxy.coder_client module
"""
import mock
import pytest

from pyproxy.coder_client import CoderClient
from pyproxy.playcloud_pb2 import FragmentsNeededReply

def test_coder_client_fragments_needed_raises_ValueError_if_not_list():
    client = CoderClient()
    with pytest.raises(ValueError) as excinfo:
        client.fragments_needed(None)
    assert str(excinfo.value) == "missing_indices argument must be of type list"

    client = CoderClient()
    with pytest.raises(ValueError) as excinfo:
        client.fragments_needed({})
    assert str(excinfo.value) == "missing_indices argument must be of type list"

    client = CoderClient()
    with pytest.raises(ValueError) as excinfo:
        client.fragments_needed(42)
    assert str(excinfo.value) == "missing_indices argument must be of type list"

    client = CoderClient()
    with pytest.raises(ValueError) as excinfo:
        client.fragments_needed(42.42)
    assert str(excinfo.value) == "missing_indices argument must be of type list"

    client = CoderClient()
    with pytest.raises(ValueError) as excinfo:
        client.fragments_needed("Hello, World!")
    assert str(excinfo.value) == "missing_indices argument must be of type list"

    client = CoderClient()
    with pytest.raises(ValueError) as excinfo:
        client.fragments_needed(client)
    assert str(excinfo.value) == "missing_indices argument must be of type list"

def test_coder_client_fragments_needed_returns_a_list():
    expected_reply = FragmentsNeededReply()
    expected_reply.needed.extend([1, 13, 42])
    client = CoderClient()
    with mock.patch.object(client.stub, "FragmentsNeeded", return_value=expected_reply):
        needed = client.fragments_needed([])
    assert expected_reply.needed == needed
