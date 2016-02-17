import pytest
from autoprotocol import Protocol
from autoprotocol_utilities.helpers import list_of_filled_wells, first_empty_well, unique_containers, sort_well_group, stamp_shape, is_columnwise, volume_check


class TestContainefunctions:
    p = Protocol()
    c = p.ref("testplate_pcr", id=None, cont_type="96-pcr", discard=True)
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
