from autoprotocol_utilities import list_of_filled_wells
from autoprotocol.container import Container
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

    Example Usage:

    .. code-block:: python

        from autoprotocol import Protocol
        from autoprotocol_utilities.magnetic_helpers import get_mag_amplicenter

        p = Protocol()
        example_plate = p.ref(name="Example", id=None, cont_type="96-pcr",
                              storage="ambient")
        p.dispense(ref=example_plate, reagent="water",
                   columns=[{"column": 4, "volume": "100:microliters"},])

        get_mag_amplicenter(example_plate)

    Returns:

    .. code-block:: json

        {'center': 0.3125, 'amplitude': 0.3125}

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

    assert isinstance(plate, Container)
    assert isinstance(amplitude_fraction, float)
    assert amplitude_fraction <= 1.0
    max_cont_vol = plate.container_type.well_volume_ul
    max_vol = max([x.volume for x in list_of_filled_wells(plate)])

    ratio = float(max_vol.to_base_units() / max_cont_vol.to_base_units())

    return {"center": ratio / 2, "amplitude": ratio / 2 / amplitude_fraction}


def get_mag_frequency(plate, speed):
    """Determine frequency for KF operation

    Based on plate type and the desired KF speed, determine the frequency for
    the KF operation. Needed for `mix` and `release` operations.

    Example Usage:

    .. code-block:: python

        from autoprotocol import Protocol
        from autoprotocol_utilities.magnetic_helpers import get_mag_frequency

        p = Protocol()
        example_plate = p.ref(name="Example", id=None, cont_type="96-pcr",
                              storage="ambient")
        get_mag_frequency(plate=example_plate, speed="slow")

    Returns:

    .. code-block:: none

        0.4:hertz

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

    frequencies = {"96-deep-kf": {"slow": "0.15:hertz", "medium": "1.5:hertz",
                                  "fast": "2.5:hertz"},
                   "96-deep": {"slow": "0.15:hertz", "medium": "1.5:hertz",
                               "fast": "2.5:hertz"},
                   "96-v-kf": {"slow": "0.5:hertz", "medium": "4.5:hertz",
                               "fast": "9.5:hertz"},
                   "96-flat": {"slow": "0.5:hertz", "medium": "5.5:hertz",
                               "fast": "11.5:hertz"},
                   "96-pcr": {"slow": "0.4:hertz", "medium": "4:hertz",
                              "fast": "8.5:hertz"}}
    assert isinstance(plate, Container)
    assert speed in ['slow', 'medium', 'fast']
    assert name in frequencies.keys()

    return frequencies[name][speed]
