import pytest
from autoprotocol_utilities.resource_helpers import ResourceIDs


class TestResources:

    _res = ResourceIDs()

    def test_bacteria(self):
        assert self._res.bacteria("nothing") is None
        assert self._res.bacteria("Zymo 10B") == "rs16pbjc4r7vvz"

    def test_diluents(self):
        assert self._res.diluents("Water") is None
        assert self._res.diluents("water") == "rs17gmh5wafm5p"

    def test_transformation_controls(self):
        assert self._res.transformation_controls("lb_miller_50ug_ml") is None
        assert self._res.transformation_controls(
            "lb_miller_50ug_ml_kan") == "rs18rx6a44qss7"

    def test_t4_ligase(self):
        assert self._res.t4_ligase("lifetech") is None
        assert self._res.t4_ligase("neb") == {"buffer": "rs17sh5rzz79ct",
                                              "ligase": "rs16pc8krr6ag7"}

    def test_restriction_enzyme_buffers(self):
        result = self._res.restriction_enzyme_buffers("no_enzyme")
        assert len(result.errors) == 2

        result = self._res.restriction_enzyme_buffers("dpni_neb")
        assert result.enzyme_id == "rs18kfcmf5xvxz"
        assert result.buffer_id == "rs17ta93g3y85t"
