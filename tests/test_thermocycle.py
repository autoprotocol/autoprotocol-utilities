import pytest
from autoprotocol_utilities.thermocycle_helpers import melt_curve, \
    thermocycle_ramp


class TestThermocycleHelpers:
    @pytest.mark.parametrize("arg", [
        (["string", 95, 0.5, 5]),
        ([65, "string", 0.5, 5]),
        ([65, 95, "string", 5]),
        ([65, 95, 0.5, "string"])
    ])
    def test_melt_curve_exceptions(self, arg):
        with pytest.raises(Exception):
            melt_curve(*arg)

    def test_melt_curve(self):
        resp = melt_curve()
        assert resp == {"melting_start": "65.00:celsius",
                        "melting_end": "95.00:celsius",
                        "melting_increment": "0.50:celsius",
                        "melting_rate": "5.00:second"}

    @pytest.mark.parametrize("arg", [
        ([["95:celcius"], "65:celcius", "1:hour", "15:second"]),
        (["95:celcius", ["65:celcius"], "1:hour", "15:second"]),
        (["95:celcius", "65:celcius", 1, "15:second"]),
        (["95:celcius", "65:celcius", "1:hour", 15])
    ])
    def test_thermocycle_ramp_exceptions(self, arg):
        with pytest.raises(Exception):
            thermocycle_ramp(*arg)

    def test_thermocycle_ramp(self):
        resp = thermocycle_ramp("95:celsius", "65:celsius", "30:minute",
                                "1:minute")
        print(resp)
        assert resp == [
            {'duration': '1.0:minute', 'temperature': '95.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '94.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '93.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '92.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '91.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '90.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '89.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '88.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '87.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '86.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '85.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '84.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '83.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '82.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '81.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '80.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '79.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '78.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '77.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '76.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '75.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '74.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '73.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '72.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '71.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '70.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '69.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '68.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '67.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '66.0:celsius'},
            {'duration': '1.0:minute', 'temperature': '65.0:celsius'}]
