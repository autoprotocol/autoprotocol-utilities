import pytest
from random import sample
from autoprotocol import Protocol
from autoprotocol.container import Well, WellGroup
from autoprotocol_utilities.helpers import list_of_filled_wells, first_empty_well, unique_containers, sort_well_group, stamp_shape, is_columnwise, volume_check


class TestContainefunctions:
    p = Protocol()
    c = p.ref("testplate_pcr", id=None, cont_type="96-pcr", discard=True)
    c.wells_from(0, 30).set_volume("20:microliter")
    ws = c.wells_from(0, 8)

    def test_asserts(self):
        with pytest.raises(Exception):
            list_of_filled_wells(self.ws)
            first_empty_well(self.ws)
            unique_containers(self.c)
            sort_well_group(self.c)
            stamp_shape(self.c)
            is_columnwise(self.c)
            volume_check(self.ws)
            volume_check(self.c)

    def test_filled_wells(self):
        assert len(list_of_filled_wells(self.c)) == 30
        assert len(list_of_filled_wells(self.c, empty=True)) == 66
        assert isinstance(list_of_filled_wells(self.c)[0], Well)

    def test_first_empty_well(self):
        assert first_empty_well(self.c).well == 30
        assert first_empty_well(self.c).success is True
        self.c.all_wells().set_volume("20:microliter")
        assert first_empty_well(self.c).success is False

    def test_unique_containers(self):
        wells = self.ws
        assert len(unique_containers(wells)) == 1
        for i in range(4):
            cont = self.p.ref("unique%s" % i, id=None,
                              cont_type="micro-1.5", discard=True)
            wells.append(cont.well(0))
        assert len(unique_containers(wells)) == 5

    def test_sort_well_group(self):
        wells = self.c.all_wells()
        random_wells = sample(wells, len(wells))
        assert list(random_wells) != list(wells)
        assert list(sort_well_group(random_wells)) == list(wells)

    # def test_shape(self):

    @pytest.mark.parametrize("len_wells, columnwise, r", [
        (8, True, True),
        (8, False, False),
        (17, True, True)
    ])
    def test_is_columnwise(self, len_wells, columnwise, r):
        wells = self.c.wells_from(0, len_wells, columnwise=columnwise)
        assert is_columnwise(wells) is r

    def test_is_columnwise_uneven(self):
        wells = self.c.wells_from(0, 8, columnwise=True)
        wells.append(self.c.well(14))
        assert is_columnwise(wells) is False

