import pytest
from collections import namedtuple
from autoprotocol_utilities.rectangle import area, area2rect, chop_list, binary_list, max_histogram_area, max_rectangle, \
    get_well_in_quadrant, get_quadrant_indices, get_quadrant_binary_list


@pytest.mark.parametrize("wells, chop_length, r", [
    ([0, 1, 2, 3, 4, 5], 3, 2),
    ([0, 1, 2, 3, 4, 5], 2, 3),
    ([0, 1, 2, 3], 3, 2)
])
def test_chop(wells, chop_length, r):
    mylist = chop_list(wells, chop_length)
    assert len(mylist) == r
    for l in mylist:
        assert len(l) == chop_length


@pytest.mark.parametrize("wells, length, r", [
    ([0, 1, 2, 6], None, [1, 1, 1, 0, 0, 0, 1]),
    ([0, 1, 2, 6], 7, [1, 1, 1, 0, 0, 0, 1]),
    ([0, 1, 2, 6], 8, [1, 1, 1, 0, 0, 0, 1, 0]),
    ([2, 3, 12, 13], None, [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1])
])
def test_binary_list(wells, length, r):
    mylist = [bnry for bnry in binary_list(wells, length=length)]
    assert mylist == r


@pytest.mark.parametrize("wells, r", [
    ([5, 3, 1], [2, 3, 0]),
    ([1, 3, 5], [2, 3, 1]),
    ([3, 1, 5], [1, 5, 2]),
    ([4, 8, 3, 2, 0], [3, 3, 0]),
    ([4, 8, 3, 1, 1, 0], [3, 3, 0]),
    ([1, 2, 1], [3, 1, 0])
])
def test_max_histogram_area(wells, r):
    area = max_histogram_area(wells)
    assert area.width == r[0]
    assert area.height == r[1]
    assert area.x == r[2]


@pytest.mark.parametrize("wells, value, r", [
    ([[1, 0, 0], [1, 0, 0]], 1, [1, 2, 0, 0]),
    ([[1, 0, 0], [1, 0, 0]], 0, [2, 2, 1, 0]),
    ([[1, 1, 0, 1], [1, 1, 0, 1]], 1, [2, 2, 0, 0])
])
def test_max_rectangle(wells, value, r):
    rect = max_rectangle(wells, value)
    assert rect.width == r[0]
    assert rect.height == r[1]
    assert rect.x == r[2]
    assert rect.y == r[3]


@pytest.mark.parametrize("well, quad, r", [
    ([0], 0, 0),
    ([0], 1, 1),
    ([0], 2, 24),
    ([0], 3, 25)
])
def test_get_well_in_quadrant(well, quad, r):
    assert (get_well_in_quadrant(well, quad)[0] == r)


@pytest.mark.parametrize("quad, r", [
    (0, 0),
    (1, 1),
    (2, 24),
    (3, 25)
])
def test_get_quadrant_indices(quad, r):
    test_quad = get_quadrant_indices(quad)
    assert ((r in test_quad) is True)


def test_area_area2rect():
    Rect = namedtuple('Rect', 'width height x y')
    Area = namedtuple('Area', 'width height x')
    test_rect = Rect(width=15, height=15, x=0, y=0)
    assert (area(test_rect) == 15 * 15)
    test_area = Area(width=15, height=15, x=0)
    assert (area2rect(test_area, 14) == test_rect)


@pytest.mark.parametrize("list, quad", [
    ([0, 4, 8, 12], 0),
    ([2, 6, 10, 14, 18, 22], 1),
    ([96, 100, 104, 108, 112, 116], 2),
    ([98, 102, 106, 110, 114, 118], 3)
])
def test_get_quadrant_binary_list(list, quad):
    temp_list = []
    for x in [0, 1, 2, 3]:
        temp_list += get_quadrant_indices(x)
    binary_list(temp_list, 384)
    for item in list:
        assert (
            (item in get_quadrant_binary_list(temp_list, [quad])[0]) is True)


@pytest.mark.parametrize("quadwells, quad, actual_wells", [  # NOQA
    ([0, 1, 2, 3], 0, [0, 2, 4, 6]),
    ([0, 1, 2, 3], 1, [1, 3, 5, 7]),
    ([0, 1, 2, 3], 2, [24, 26, 28, 30]),
    ([0, 1, 2, 3], 3, [25, 27, 29, 31])
])
def test_get_well_in_quadrant(quadwells, quad, actual_wells):
    assert (actual_wells == get_well_in_quadrant(quadwells, quad))
