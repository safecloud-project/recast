"""
Unit tests for pylonghair_driver
"""
import os

import pytest

from pylonghair_driver import compute_block_size, split_and_number
from pylonghair_driver import PylonghairDriver

def test_remap_no_indices():
    data = [1, 2, 3, 4]
    expected = [(0, 1), (1, 2), (2, 3), (3, 4)]
    missing_indices = []
    assert expected == split_and_number(data, missing_indices)


def test_remap_first_missing():
    data = [2, 3, 4]
    expected = [(1, 2), (2, 3), (3, 4)]
    missing_indices = [0]
    assert expected == split_and_number(data, missing_indices)

def test_remap_first_and_second_missing():
    data = [3, 4]
    expected = [(2, 3), (3, 4)]
    missing_indices = [0, 1]
    assert expected == split_and_number(data, missing_indices)

def test_remap_second_and_third_missing():
    data = [1, 4]
    expected = [(0, 1), (3, 4)]
    missing_indices = [1, 2]
    assert expected == split_and_number(data, missing_indices)

def test_remap_third_and_fourth_missing():
    data = [1, 2]
    expected = [(0, 1), (1, 2)]
    missing_indices = [2, 3]
    assert expected == split_and_number(data, missing_indices)

def test_remap_first_and_fourth_missing():
    data = [2, 3]
    expected = [(1, 2), (2, 3)]
    missing_indices = [0, 3]
    assert expected == split_and_number(data, missing_indices)

def test_remap_first_and_third_missing():
    data = [2, 4]
    expected = [(1, 2), (3, 4)]
    missing_indices = [0, 2]
    assert expected == split_and_number(data, missing_indices)

# Test compute block size
def test_compute_block_size_throws_error_if_k_equals_zero():
    with pytest.raises(AssertionError):
        compute_block_size(8, 0)

def test_compute_block_size_throws_error_if_k_is_lower_than_zero():
    with pytest.raises(AssertionError):
        compute_block_size(8, -1)

def test_compute_block_size_returns_8_if_block_size_is_lower_than_8():
    block_size = compute_block_size(8, 3)
    assert block_size == 8

def test_compute_block_size_returns_a_multiple_of_8_if_initial_block_size_is_higher_than_8():
    block_size = compute_block_size(1024, 10)
    assert block_size == 104

# Test PylonghairDriver encode
DATA = os.urandom(1024)

def test_encode():
    k, m = 10, 4
    expected_block_size = compute_block_size(len(DATA), k)
    driver = PylonghairDriver(k=k, m=m)
    strips = driver.encode(DATA)
    assert isinstance(strips, list)
    assert len(strips) == 14
    # Test parity blocks have expected block size
    expected_parity_strips = strips[len(strips) - m:]
    assert m == len(expected_parity_strips)
    for strip in expected_parity_strips:
        assert expected_block_size == len(strip)

def test_encode_less_than_k_data_blocks():
    little_data = os.urandom(70)
    k, m = 10, 4
    expected_block_size = compute_block_size(len(little_data), k)
    driver = PylonghairDriver(k=k, m=m)
    strips = driver.encode(little_data)
    assert isinstance(strips, list)
    assert len(strips) == 13
    # Test parity blocks have expected block size
    expected_parity_strips = strips[len(strips) - m:]
    assert m == len(expected_parity_strips)
    for strip in expected_parity_strips:
        assert expected_block_size == len(strip)
