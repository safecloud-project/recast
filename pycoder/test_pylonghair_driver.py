from pylonghair_driver import split_and_number

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
