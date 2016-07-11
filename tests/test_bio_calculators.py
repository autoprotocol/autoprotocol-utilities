from autoprotocol_utilities.bio_calculators import dna_mass_to_mole, dna_mole_to_mass, \
    molar_to_mass_conc, mass_conc_to_molar, ligation_insert_ng, ligation_insert_volume, \
    ligation_insert_amount
from autoprotocol.unit import Unit
import pytest


class TestBiocalculators:

    def test_dna_mass_to_mole(self):
        assert "0.1:picomole" == str(dna_mass_to_mole(10, "660:pg"))
        assert "200.0:picomole" == str(dna_mass_to_mole(500, "33:ug", False))
        with pytest.raises(ValueError):
            dna_mass_to_mole(100, 100)
        with pytest.raises(ValueError):
            dna_mass_to_mole(100, "12:uL")

    def test_dna_mole_to_mass(self):
        assert "0.2112:microgram" == str(
            dna_mole_to_mass(10, Unit(32, "pmol")))
        assert "19.8:microgram" == str(
            dna_mole_to_mass(3000, Unit(20, "pmol"), False))
        with pytest.raises(ValueError):
            dna_mole_to_mass("1", 100)
        with pytest.raises(ValueError):
            dna_mole_to_mass(100, "1:mm")

    def test_molar_to_mass_conc(self):
        assert "33.0:nanogram/microliter" == str(
            molar_to_mass_conc(10, "10:pmol/uL", False))
        with pytest.raises(ValueError):
            molar_to_mass_conc(5000, 100)
        with pytest.raises(ValueError):
            molar_to_mass_conc(100, "5:ng/uL")

    def test_mass_conc_to_molar(self):
        assert "10.0:micromolar" == str(
            mass_conc_to_molar(10, Unit(33, "ug/mL"), False))
        with pytest.raises(ValueError):
            mass_conc_to_molar(600, Unit(1, "uM"))
        with pytest.raises(ValueError):
            mass_conc_to_molar(100, "12:uL", 4)

    def test_ligation_insert_ng(self):
        assert "50.0:nanogram" == str(
            ligation_insert_ng(1000, Unit(100, "ng"), 500))
        assert "2.0:nanogram" == str(
            ligation_insert_ng(5000, Unit(100, "ng"), 50, "2:1"))
        assert "4.0:nanogram" == str(
            ligation_insert_ng(3000, Unit(100, "ng"), 48, 2.5))
        with pytest.raises(ValueError):
            ligation_insert_ng(1000, 100, 600, 3)
        with pytest.raises(ValueError):
            ligation_insert_ng(1000, "12:uL", 500)

    def ligation_insert_volume(self):
        assert "2.0202020202:microliter" == str(
            ligation_insert_volume(1000, "100:ng", 500,
                                   Unit(0.15, "uM"), False))
        assert "0.1875:microliter" == str(
            ligation_insert_volume(200, "66:ng", 100,
                                   Unit(4, "uM"), True, 1.5))
        with pytest.raises(ValueError):
            ligation_insert_volume(
                500, "1: ng", 300, Unit(50, "mm"), True, "2:1")
        with pytest.raises(ValueError):
            ligation_insert_volume(20, "12: uL", 10, Unit(33, "M"))

    def test_ligation_insert_amount(self):
        assert "5.0:microliter" == str(
            ligation_insert_amount(1, "1:ng/uL", "10:uL", 1, "2:ng/uL"))
        assert "1.98:microliter" == str(
            ligation_insert_amount(1, "1:uM", "10:uL", 1, "2:ng/uL",
                                   True, "3:5"))
        with pytest.raises(ValueError):
            dna_mass_to_mole(100, 100)
        with pytest.raises(ValueError):
            dna_mass_to_mole(100, "12:uL")
