import pytest
from autoprotocol_utilities.resource_helpers import ResourceIDs, oligo_scale_default, \
    oligo_dilution_table, return_agar_plates, ref_kit_container
from autoprotocol import Protocol, Container, ContainerType

@pytest.mark.parametrize("length, scale, label, output", [
    (50, "10nm", "sample", True),
    (115, "100nm", "sample", False),
    (4, "1um", "sample", False)
])
def test_oligo_scale_default(length, scale, label, output):
    assert (oligo_scale_default(length, scale, label)[0] == output)


@pytest.mark.parametrize("conc, sc, dilution_table", [
    ("100uM", "10nm", 60),
    ("100uM", "100nm", 1000),
    ("1mM", "1um", 1000),
    ("1mM", "1um", 1000)
])
def test_oligo_dilution_table(conc, sc, dilution_table):
    assert (oligo_dilution_table(conc, sc) == dilution_table)


@pytest.mark.parametrize("wells, plates", [
    (6, {"lb_miller_50ug_ml_kan": "ki17rs7j799zc2",
                  "lb_miller_100ug_ml_amp": "ki17sbb845ssx9",
                  "lb_miller_100ug_ml_specto": "ki17sbb9r7jf98",
                  "lb_miller_100ug_ml_cm": "ki17urn3gg8tmj",
                  "lb_miller_noAB": "ki17reefwqq3sq"}),
    (1, {"lb_miller_50ug_ml_kan": "ki17t8j7kkzc4g",
                  "lb_miller_100ug_ml_amp": "ki17t8jcebshtr",
                  "lb_miller_100ug_ml_specto": "ki17t8jaa96pw3",
                  "lb_miller_100ug_ml_cm": "ki17urn592xejq",
                  "lb_miller_noAB": "ki17t8jejbea4z"})
])
def test_return_agar_plates(wells, plates):
    assert(return_agar_plates(wells) == plates)


class TestResources:
    _res = ResourceIDs()

    def test_bacteria(self):
        assert self._res.bacteria("nothing") is None
        assert self._res.bacteria("Zymo 10B") == "rs16pbjc4r7vvz"

    def test_diluents(self):
        assert self._res.diluents("Water") is None
        assert self._res.diluents("water") == "rs17gmh5wafm5p"

    def test_exoassembly_kits(self):
        assert self._res.exoassembly_kits("Gibson")["name"] == "Gibson"
        assert self._res.exoassembly_kits("Water") is None

    def test_transformation_controls(self):
        assert self._res.transformation_controls("lb_miller_50ug_ml") is None
        assert self._res.transformation_controls(
            "lb_miller_50ug_ml_kan") == "rs18rx6a44qss7"

    def test_growth_media(self):
        assert self._res.growth_media("lb_miller_50ug_ml_kan") == "rs18s8x88zz9ee"
        assert self._res.growth_media("tb_100ug_ml_amp") == "rs18xr22jq7vtz"

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
