import pytest

from ..proxy_service import get_random_blocks

def test_get_random_blocks_lower_than_zero():
    with pytest.raises(ValueError) as e:
        get_random_blocks(-1)
    assert "argument blocks cannot be lower or equal to 0" in e.value

def test_get_random_blocks_equal_to_zero():
    with pytest.raises(ValueError) as e:
        get_random_blocks(0)
    assert "argument blocks cannot be lower or equal to 0" in e.value


def test_get_random_blocks_returns_a_list_of_length_blocks():
    result = get_random_blocks(1)
    assert isinstance(result, list)
    assert len(result) == 1
