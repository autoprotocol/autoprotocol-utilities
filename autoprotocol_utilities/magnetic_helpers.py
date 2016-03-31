from autoprotocol_utilities import list_of_filled_wells
from autoprotocol.container import Container
from collections import namedtuple
import sys

if sys.version_info[0] >= 3:
    string_type = str
else:
    string_type = basestring


def get_mag_amplicenter(plate, amplitude_fraction=1.0):
    """Determine amplitude and center for KF operations

    Given the container this function determines the well type and fill volume.
    From that it calculates the center for the magnetic operation (1/2 the
    fill volume) and the amplitude to move around that from 0 to center +
    amplitude.

    Parameters
    ----------
    plate: Container
        Plate that is being used
    amplitude_fraction: float, optional
        By default the full available amplitude will be used (from center to
        bottom of well). Use this parameter to reduce the amplitude.

    Returns
    -------
    nametuple
        `center` and `amplitude` both of type float

    Raises
    ------
    ValueError
        If plate is not of type `Container`
    ValueError
        If `amplitude_fraction` is not a float or bigger than 1
    """
    Mag_mix = namedtuple('Mixparam', 'center amplitude')

    assert isinstance(plate, Container)
    assert isinstance(amplitude_fraction, float)
    assert amplitude_fraction <= 1.0
    max_cont_vol = plate.container_type.well_volume_ul
    max_vol = max([x.volume for x in list_of_filled_wells(plate)])

    ratio = float(max_vol.to_base_units()/max_cont_vol.to_base_units())

    return Mag_mix(center=ratio/2, amplitude=ratio/2/amplitude_fraction)


def get_mag_frequency(plate, speed):
    """Determine frequency for KF operation

    Based on plate type and the desired KF speed, determine the frequency for
    the KF operation. Needed for `mix` and `release` operations.

    Parameters
    ----------
    plate: Container
        Container that is being used
    speed: string
        String defining the speed - can be `slow`, `medium`, `fast`

    Returns
    -------
    string
        Frequency in the form of "2.5:Hz"

    Raises
    ------
    ValueError
        If `plate` is not of type `Container`
    ValueError
        If `speed` is not 'slow', 'medium', 'fast'
    ValueError
        If plate type is not a key in `frequencies`
    """
    name = plate.container_type.shortname

    frequencies = {"96-deep-kf": {"slow": "0.15:Hz", "medium": "1.5:Hz",
                                  "fast": "2.5:Hz"},
                   "96-deep": {"slow": "0.15:Hz", "medium": "1.5:Hz",
                               "fast": "2.5:Hz"},
                   "96-v-kf": {"slow": "0.5:Hz", "medium": "4.5:Hz",
                               "fast": "9.5:Hz"},
                   "96-flat": {"slow": "0.5:Hz", "medium": "5.5:Hz",
                               "fast": "11.5:Hz"},
                   "96-pcr": {"slow": "0.4:Hz", "medium": "4:Hz",
                              "fast": "8.5:Hz"}}
    assert isinstance(plate, Container)
    assert speed in ['slow', 'medium', 'fast']
    assert name in frequencies.keys()

    return frequencies[name][speed]
