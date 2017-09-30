"""
Tests for the entanglement classes and functions of the entangled_driver module
"""
import hashlib
import os

import pytest
from pyeclib.ec_iface import ECDriverError

from pyproxy.coder.entangled_driver import StepEntangler, FragmentHeader
from pyproxy.coder.playcloud_pb2 import Strip


ENTANGLEMENT_HEADER = "[]"
with open(os.path.join("test_data", "header.pack"), "rb") as handle:
    FRAGMENT_HEADER = FragmentHeader(handle.read())
FAKE_BLOCK = ENTANGLEMENT_HEADER + StepEntangler.HEADER_DELIMITER + str(FRAGMENT_HEADER.metadata.orig_data_size) + StepEntangler.HEADER_DELIMITER + FRAGMENT_HEADER.pack() + "".join([str(i % 10) for i in xrange(FRAGMENT_HEADER.metadata.size)])
FAKE_HASH = hashlib.sha256(FAKE_BLOCK).digest()

class SourceWithoutRandomBlocks(object):
    def get_block(self, path, index):
        pass

class SourceWithoutGetBlock(object):
    @staticmethod
    def get_random_blocks(elements):
        pass

class MockSource(object):
    @staticmethod
    def get_random_blocks(elements):
        strips = []
        for index in xrange(elements):
            strip = Strip()
            strip.id = "block-{:d}".format(index)
            strip.data = FAKE_BLOCK[:]
            strip.checksum = FAKE_HASH[:]
            strips.append(strip)
        return strips

    @staticmethod
    def get_block(path, index, reconstruct_if_missing=True):
        strip = Strip()
        strip.id = "{:s}-{:d}".format(path, index)
        strip.data = FAKE_BLOCK[:]
        strip.checksum = FAKE_HASH[:]
        return strip

def test_constructor_raises_value_error_if_source_is_None():
    with pytest.raises(ValueError) as excinfo:
        StepEntangler(None, 1, 10, 3)
    assert str(excinfo.value) == "source argument must implement a get_random_blocks and a get_block method"


def test_constructor_raises_value_error_if_source_does_not_implement_GetBlock():
    with pytest.raises(ValueError) as excinfo:
        StepEntangler(SourceWithoutGetBlock(), 1, 10, 3)
    assert str(excinfo.value) == "source argument must implement a get_random_blocks and a get_block method"


def test_constructor_raises_value_error_if_s_negative():
    with pytest.raises(ValueError) as excinfo:
        StepEntangler(MockSource(), -1, 5, 1)
    assert str(excinfo.value) == "s(-1) must be greater or equal to 1"


def test_constructor_raises_value_error_if_s_zero():
    with pytest.raises(ValueError) as excinfo:
        StepEntangler(MockSource(), 0, 5, 1)
    assert str(excinfo.value) == "s(0) must be greater or equal to 1"


def test_constructor_raises_value_error_if_t_negative():
    with pytest.raises(ValueError) as excinfo:
        StepEntangler(MockSource(), 1, -1, 1)
    assert str(excinfo.value) == "t(-1) must be greater or equal to 0"


def test_constructor_raises_value_error_if_s_greter_than_p():
    with pytest.raises(ValueError) as excinfo:
        StepEntangler(MockSource(), 2, 0, 1)
    assert str(excinfo.value) == "p(1) must be greater or equal to s(2)"


def test_constructor():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    assert driver.s == 1
    assert driver.t == 10
    assert driver.p == 3


def test_fragments_needed_all_available():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    assert driver.fragments_needed([]) == [11]


def test_fragments_needed_one_parity_missing():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    assert driver.fragments_needed([11]) == [12]


def test_fragments_needed_two_parities_missing():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    assert driver.fragments_needed([11, 12]) == [13]


def test_fragments_needed_all_parities_missing():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    with pytest.raises(ECDriverError) as excinfo:
        driver.fragments_needed([10, 11, 12])
    assert str(excinfo.value) == "Configuration of Step (s=1, t=10, e=2, p=3) does not allow for reconstruction of 3 missing blocks"

def test_fragments_needed_raises_ValueError_when_index_out_of_scope():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    with pytest.raises(ValueError) as excinfo:
        driver.fragments_needed([-1])
    assert str(excinfo.value) == "Index -1 is out of range(0 <= index < 14)"
    
    assert driver.fragments_needed([0]) == [11]
    assert driver.fragments_needed([13]) == [11]

    with pytest.raises(ValueError) as excinfo:
        driver.fragments_needed([14])
    assert str(excinfo.value) == "Index 14 is out of range(0 <= index < 14)"

def test_encode():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    data = "".join(["0xCAFEBABE" for _ in xrange(128)])
    encoded = driver.encode(data)
    assert len(encoded) == 3


def test_decode():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    data = "".join(["0xCAFEBABE" for _ in xrange(128)])
    encoded = driver.encode(data)
    decoded = driver.decode(encoded)
    assert len(decoded) == len(data)
    assert data == decoded


def __get_data_from_strip(strip):
    first_pos = strip.find(StepEntangler.HEADER_DELIMITER) +\
                len(StepEntangler.HEADER_DELIMITER)
    pos = strip.find(StepEntangler.HEADER_DELIMITER, first_pos) +\
          len(StepEntangler.HEADER_DELIMITER)
    return strip[pos:]


def test_reconstruct():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    data = "".join(["0xCAFEBABE" for _ in xrange(128)])
    encoded = driver.encode(data)
    reconstructed = driver.reconstruct(encoded[1:], [0])
    assert len(reconstructed) == 1
    reconstructed_block = reconstructed[0]
    expected_block = encoded[0]
    assert len(reconstructed_block) == len(expected_block)
    # Check the entanglement header
    pos = reconstructed_block.find(StepEntangler.HEADER_DELIMITER)
    entanglement_header = reconstructed_block[:pos]
    expected_entanglement_header = expected_block[:pos]
    assert entanglement_header == expected_entanglement_header
    # Check the original size
    pos += 1
    second_pos = reconstructed_block.find(StepEntangler.HEADER_DELIMITER, pos)
    original_size = int(reconstructed_block[pos:second_pos])
    expected_original_size = int(expected_block[pos:second_pos])
    assert original_size == expected_original_size
    # Check the liberasurecode header
    second_pos += 1
    ec_header = FragmentHeader(reconstructed_block[second_pos:second_pos + 80])
    expected_ec_header = FragmentHeader(expected_block[second_pos:second_pos + 80])
    assert ec_header == expected_ec_header
    assert reconstructed[0] == encoded[0]


def test_fetch_and_prep_pointer_blocks_raises_ValueError_if_pointers_not_list():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks(None, 42, 1000)
    assert str(excinfo.value) == "pointers argument must be of type list"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks(1, 42, 1000)
    assert str(excinfo.value) == "pointers argument must be of type list"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks("hello world", 42, 1000)
    assert str(excinfo.value) == "pointers argument must be of type list"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks({}, 42, 1000)
    assert str(excinfo.value) == "pointers argument must be of type list"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks(MockSource(), 42, 1000)
    assert str(excinfo.value) == "pointers argument must be of type list"


def test_fetch_and_prep_pointer_blocks_raises_ValueError_if_fragment_size_not_an_int():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], None, 1000)
    assert str(excinfo.value) == "fragment_size argument must be an integer greater than 0"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], 42.42, 1000)
    assert str(excinfo.value) == "fragment_size argument must be an integer greater than 0"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], "hello world", 1000)
    assert str(excinfo.value) == "fragment_size argument must be an integer greater than 0"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], {}, 1000)
    assert str(excinfo.value) == "fragment_size argument must be an integer greater than 0"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], [], 1000)
    assert str(excinfo.value) == "fragment_size argument must be an integer greater than 0"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], [], 1000)
    assert str(excinfo.value) == "fragment_size argument must be an integer greater than 0"


def test_fetch_and_prep_pointer_blocks_raises_ValueError_if_fragment_size_lower_or_equal_to_0():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], -1, 1000)
    assert str(excinfo.value) == "fragment_size argument must be an integer greater than 0"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], 0, 1000)
    assert str(excinfo.value) == "fragment_size argument must be an integer greater than 0"


def test_fetch_and_prep_pointer_blocks_raises_ValueError_if_original_data_size_not_an_int():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], 42, None)
    assert str(excinfo.value) == "original_data_size argument must be an integer greater than 0"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], 42, 42.42)
    assert str(excinfo.value) == "original_data_size argument must be an integer greater than 0"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], 42, "Hello, World!")
    assert str(excinfo.value) == "original_data_size argument must be an integer greater than 0"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], 42, {})
    assert str(excinfo.value) == "original_data_size argument must be an integer greater than 0"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], 42, [])
    assert str(excinfo.value) == "original_data_size argument must be an integer greater than 0"


def test_fetch_and_prep_pointer_blocks_raises_ValueError_if_original_data_size_not_lower_or_equal_to_0():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], 42, -1)
    assert str(excinfo.value) == "original_data_size argument must be an integer greater than 0"
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], 42, 0)
    assert str(excinfo.value) == "original_data_size argument must be an integer greater than 0"


def test_fetch_and_prep_pointer_blocks_raises_ValueError_if_original_data_size_is_lower_than_frangment_size():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    with pytest.raises(ValueError) as excinfo:
        driver.fetch_and_prep_pointer_blocks([], 43, 42)
    assert str(excinfo.value) == "original_data_size must be greater or equal to fragment_size"


def test_fetch_and_prep_pointer_blocks_returns_empty_list_for_empty_pointers():
    driver = StepEntangler(MockSource(), 1, 10, 3, ec_type="liberasurecode_rs_vand")
    prepped_pointers = driver.fetch_and_prep_pointer_blocks([], 42, 42)
    assert isinstance(prepped_pointers, list)
    assert len(prepped_pointers) == 0


class FailingSource(object):
    @staticmethod
    def get_random_blocks(elements):
        return [None for _ in xrange(elements)]

    @staticmethod
    def get_block(path, index, reconstruct_if_missing=True):
        return Strip()


def test_fetch_and_prep_pointer_blocks_returns_None_for_blocks_that_cannot_fetch():
    source = FailingSource()
    driver = StepEntangler(source, 1, 10, 3, ec_type="liberasurecode_rs_vand")
    prepped_pointers = driver.fetch_and_prep_pointer_blocks([["non-existing", 42]], 42, 42)
    assert isinstance(prepped_pointers, list)
    assert len(prepped_pointers) == 1
    assert prepped_pointers[0] is None

def test_step_entangler_compute_fragment_size_raises_ValueError_if_document_size_is_negative():
    with pytest.raises(ValueError) as excinfo:
        StepEntangler.compute_fragment_size(-1, 1)
    assert str(excinfo.value) == "document_size argument must be an integer greater or equal to 0"

def test_step_entangler_compute_fragment_size_raises_ValueError_if_fragments_is_negative():
    with pytest.raises(ValueError) as excinfo:
        StepEntangler.compute_fragment_size(1, -1)
    assert str(excinfo.value) == "fragments argument must be an integer greater than 0"

def test_step_entangler_compute_fragment_size_raises_ValueError_if_fragments_is_equal_to_0():
    with pytest.raises(ValueError) as excinfo:
        StepEntangler.compute_fragment_size(1, 0)
    assert str(excinfo.value) == "fragments argument must be an integer greater than 0"

def test_step_entangler_compute_fragment_size():
    assert StepEntangler.compute_fragment_size(100, 1) == 100
    assert StepEntangler.compute_fragment_size(101, 1) == 102
    assert StepEntangler.compute_fragment_size(100, 2) == 50
    assert StepEntangler.compute_fragment_size(100, 3) == 34