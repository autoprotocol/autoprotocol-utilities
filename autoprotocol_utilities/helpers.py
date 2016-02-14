from autoprotocol.container import Container, WellGroup, Well
from autoprotocol.protocol import Ref
from autoprotocol.unit import Unit
from autoprotocol import UserError
from rectangle import binary_list, chop_list, max_rectangle
from collections import namedtuple
from operator import itemgetter
import datetime
import math
import sys

if sys.version_info[0] >= 3:
    string_type = str
else:
    string_type = basestring


def list_of_filled_wells(cont, empty=False):
    """
    For the container given, determine which wells are filled

    Parameters
    ----------
    cont : Container
    empty : bool
        If True return empty wells instead of filled

    Returns
    -------
    wells : list
        list of wells
    """
    if not isinstance(cont, Container):
        raise RuntimeError("list_of_filled_wells needs a container as input")
    wells = []
    for well in cont.all_wells():
        if not empty:
            if well.volume is not None:
                wells.append(well)
        if empty:
            if well.volume is None:
                wells.append(well)
    return wells


def first_empty_well(cont):
    """
    Get the first empty well of a container followed by only empty wells

    Parameters
    ----------
    cont : container

    Returns
    -------
    on success: well
    on failure: string

    """
    well = max(cont.all_wells(),
               key=lambda x: x.index if x.volume else 0).index + 1
    if well < cont.container_type.well_count:
        return well
    else:
        return "The container has no empty wells left"


def unique_containers(wells):
    """
    Get a list of unique containers for a list of wells

    Parameters
    ----------
    wells : list
        List of wells

    Returns
    -------
    cont : list
        List of Containers

    """
    assert isinstance(wells, (list, WellGroup)), "unique_containers requires"
    " a list of wells or a WellGroup"
    wells = flatten_list(wells)
    cont = list(set([well.container for well in wells]))
    return cont


def sort_well_group(well_group, columnwise=False):
    """
        Sort a well group in rowwise or columnwise format.
        This function sorts first by container id and name, then by row or
        column, as needed. When the webapp returns aliquot+ inputs, it
        usually does so as a rowwise sorted well group, so this function
        can be useful for re-sorting when necessary.
    """
    assert isinstance(well_group, WellGroup), "well_group must be an instance"
    " of the WellGroup class"
    well_list = [(
        well,
        well.container.id,
        well.container.name,
        well.container.decompose(well)[0],
        well.container.decompose(well)[1]
        ) for well in well_group
    ]

    if columnwise:
        sorted_well_list = sorted(well_list, key=itemgetter(1, 2, 4, 3))
    else:
        sorted_well_list = sorted(well_list, key=itemgetter(1, 2, 3, 4))

    sorted_well_group = WellGroup([well[0] for well in sorted_well_list])
    return sorted_well_group


def stamp_shape(wells):
    """
    Find biggest reactangle that can be stamped from a list of wells.

    Parameters
    ----------
    wells: list, WellGroup
        List of wells or well_group containing the wells in question.

    Returns
    -------
    stamp_shape : named tuple
        start_well is the top left well for the source stamp group
        shape is a dict of rows and columns describing the stamp shape
        remainging_wells is a list of wells that are not included in the
        stamp shape.

    """
    assert isinstance(wells, (list, WellGroup)), "Stamp_shape: wells has to "
    "be a list or a WellGroup"
    assert len(unique_containers(wells)) == 1, "Stamp_shape: wells have to"
    " come from one container"
    for well in wells:
        assert isinstance(well, (Well)), "Stamp_shape: elements of wells"
        " have to be of type Well"

    stamp_shape = namedtuple('Stamp', 'start_well shape remaining_wells')
    wells = sort_well_group(wells)
    cont = unique_containers(wells)[0]
    rows = cont.container_type.row_count()
    cols = cont.container_type.col_count
    # rows = 8
    # cols = 12
    indices = [x.index for x in wells]

    bnry_list = [bnry for bnry in binary_list(indices, length=rows*cols)]
    bnry_mat = chop_list(bnry_list, cols)
    r = max_rectangle(bnry_mat, value=1)

    # Determine start_well and wells not included in the rectangle
    wells_included = []
    start_well = (r.y*cols) + r.x
    for y in range(r.height):
        for z in range(r.width):
            wells_included.append(start_well + y*cols + z)
    wells_remaining = [x for x in wells if x not in wells_included]

    return stamp_shape(start_well=start_well,
                       shape=dict(rows=r.height, columns=r.width),
                       remaining_wells=wells_remaining)


def is_columnwise(wells):
    """
    Goal: Detect if input wells are in a columnwise format. This will only
    trigger if the first column is full and only consecutive fractionally
    filled columns exist.

    Patterns detected (4x6 plate):

    .. code-block:: none

        x x x | x x x  | x
        x     | x x x  | x
        x     | x x x  | x
        x     | x x x  | x

    Patterns NOT detected (4x6 plate):

    .. code-block:: none

        x x x  | x      | x
          x x  | x      | x
          x x  | x      | x
          x x  | x x x  |

    Parameters
    ----------
    wells: list, WellGroup
        List of wells or well_group containing the wells in question.

    Returns
    -------
    shape : bool
        True if columnwise
    """
    assert isinstance(wells, (list, WellGroup)), "is_columnwise: wells has to"
    " be a list or a WellGroup"
    assert len(unique_containers(wells)) == 1, "is_columnwise: wells have to"
    " come from one container"
    for well in wells:
        assert isinstance(well, (Well)), "is_columnwise: elements of wells"
        " have to be of type Well"

    cont = unique_containers(wells)[0]
    rows = cont.container_type.row_count()
    y = stamp_shape(wells)

    consecutive = False
    if len(y.remaining_wells) == 0:
        consecutive = True
    else:
        next_well = y.start_well + y.shape["columns"] + 1
        z = stamp_shape(y.remaining_wells)
        if len(z.remaining_wells) == 0 and z.start_well == next_well:
            consecutive = True

    if y.shape["rows"] == rows and consecutive:
        shape = True
    else:
        shape = False

    return shape


def plates_needed(wells_needed, wells_available):
    """
    Takes wells needed as a numbers (int or float)
    and wells_available as a container or a well number
    (int or float) and calculates how many plates are
    needed to accomodate the wells_needed.

    Parameters
    ----------
    wells_needed: float, int
        How many you need
    wells_available: Container, float, int
        How many you have available per unit

    Returns
    -------
    i : int
        How many of unit you will need to accomodate all wells_needed

    """
    if not isinstance(wells_needed, (float, int)):
        raise RuntimeError("wells_needed has to be an int or a float")
    if isinstance(wells_available, Container):
        wells_available = float(wells_available.container_type.well_count)
    elif isinstance(wells_available, int):
        wells_available = float(wells_available)
    elif not isinstance(wells_available, (float, int, Container)):
        raise RuntimeError("wells_available has to be a container,"
                           "int or float")
    return int(math.ceil(wells_needed / wells_available))


def volume_check(aliquot, usage_volume=0):
    """
    Takes an aliquot and if usaage_volume is 0 checks if that aliquot
    is above the dead volume for its well type.
    If the usage_volume is set it will check if there is enough volume
    above the dead_volume to execute the
    pipette.
    Usage volume can be a Unit, a string of type "3:microliter" or an
    integer

    Parameters
    ----------
    aliquot : Well
        Well to test
    usage_volume : Unit, str, int, optional
        Volume to test for. If 0 the aliquot will be tested against the
        container dead volume.

    Returns
    -------
    message : str
        If volume passes check message will be empty. Otherwise it reports
        how much volume is available vs needed.

    """
    if isinstance(aliquot, Container):
        raise RuntimeError("volume check accepts only aliquots, "
                           "not containers")
    if isinstance(usage_volume, Unit):
        usage_volume = usage_volume.value
    if isinstance(usage_volume, string_type):
        usage_volume = int(usage_volume.split(":microliter")[0])

    dead_vol = aliquot.container.container_type.dead_volume_ul
    test_vol = dead_vol + usage_volume

    if test_vol > aliquot.volume.value:
        if usage_volume == 0:
            return ("You want to pipette from a container with %s uL"
                    " dead volume. However, you aliquot only has "
                    "%s uL." % (dead_vol, aliquot.volume.value))
        else:
            return ("You want to pipette %s uL from a container with "
                    "%s uL dead volume (%s uL total). However, your"
                    " aliquot only has %s uL." % (usage_volume,
                                                  dead_vol,
                                                  usage_volume + dead_vol,
                                                  aliquot.volume.value))


def user_errors_group(error_msgs):
    """
        Takes a list error messages and neatly displays as a single UserError
    """
    assert isinstance(error_msgs, list), ("Error messages must be in the form"
                                          " of a list to properly format the "
                                          "grouped message.")
    if len(error_msgs) != 0:
        raise UserError(
            "%s error(s) found in this protocol: " % len(error_msgs) +
            " ".join(["<Error " +
                      string_type(i + 1) + "> " +
                      string_type(m) for i, m in enumerate(error_msgs)]))


def printdatetime():
    """
    Generate a datetime string

    Returns
    -------
    printdate : str

    """
    printdate = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    return printdate


def printdate():
    """
    Generate a date string

    Returns
    -------
    printdate : str

    """
    printdate = datetime.datetime.now().strftime('%Y-%m-%d')
    return printdate


def make_list(my_str, integer=False):
    """
    Sometimes you need a list of a type that is not supported.

    Parameters
    ----------
    my_str : string
        String with individual elements separated by comma
    interger : bool
        If true list of integers instead of list of strings
        is returned.

    Returns
    -------
    my_str : list
        List of strings or integers

    """
    assert isinstance(my_str, string_type), "Input needs to be of type string"
    if integer:
        my_str = [int(x.strip()) for x in my_str.split(",")]
    else:
        my_str = [x.strip() for x in my_str.split(",")]
    return my_str


def flatten_list(l):
    """
    Flatten a list recursively without for loops or additional modules

    Parameters
    ---------
    l : list
        List to flatten

    Returns
    -------
    list : list
        Flat list

    """
    if l == []:
        return l
    if isinstance(l[0], list):
        return flatten_list(l[0]) + flatten_list(l[1:])
    return l[:1] + flatten_list(l[1:])


def det_new_group(i, base=0):
    """Determine if new_group should be added to pipetting operation.

    Helper to determine if new_group should be added. Returns true when
    i matches the base, which defaults to 0.

    Parameters
    ----------
    i : int
        The iteration you are on
    base : int, optional
        The value at which you want to trigger

    Returns
    -------
    new_group : bool

    """
    assert isinstance(i, int), "Needs an integer."
    assert isinstance(base, int), "Base has to be an integer"
    if i == base:
        new_group = True
    else:
        new_group = False
    return new_group

# ## Returning containers or data


def return_agar_plates(wells=6):
    """Dicts of all plates available that can be purchased.

    Parameters
    ----------
    wells : integer
        Optional, default 6 for 6-well plate

    Returns
    -------
    plates : dict
        plates with plate identity as key and kit_id as value

    """
    if wells == 6:
        plates = {"lb-broth-50ug-ml-kan": "ki17rs7j799zc2",
                  "lb-broth-100ug-ml-amp": "ki17sbb845ssx9",
                  "lb-broth-100ug-ml-specto": "ki17sbb9r7jf98",
                  "lb-broth-100ug-ml-cm": "ki17urn3gg8tmj",
                  "noAB": "ki17reefwqq3sq"}
    elif wells == 1:
        plates = {"lb-broth-50ug-ml-kan": "ki17t8j7kkzc4g",
                  "lb-broth-100ug-ml-amp": "ki17t8jcebshtr",
                  "lb-broth-100ug-ml-specto": "ki17t8jaa96pw3",
                  "lb-broth-100ug-ml-cm": "ki17urn592xejq",
                  "noAB": "ki17t8jejbea4z"}
    else:
        raise ValueError("Wells has to be an integer, either 1 or 6")
    return(plates)


def return_dispense_media():
    """Dict of media for reagent dispenser.

    Returns
    -------
    media : dict
        Media with common display_name as key and identifier for code
    as value

    """
    media = {"50_ug/ml_Kanamycin": "lb-broth-50ug-ml-kan",
             "100_ug/ml_Ampicillin": "lb-broth-100ug-ml-amp",
             "100_ug/mL_Spectinomycin": "lb-broth-100ug-ml-specto",
             "30_ug/ml_Kanamycin": "lb-broth-30ug-ml-kan",
             "50_ug/ml_Kanamycin_25_ug/ml_Chloramphenicol":
             "lb-broth-50ug-ml-kan-25ug-ml-cm",
             "15_ug/ml_Tetracycline": "lb-broth-15ug-ml-tet",
             "25_ug/ml_Chloramphenicol": "lb-broth-25ug-ml-cm",
             "LB_broth": "lb-broth-noAB"}
    return(media)


def ref_kit_container(protocol, name, container, kit_id, discard=True,
                      store=None):
    """Reserve agar plates on the fly

    In use only to allow booking of agar plates on the fly.

    Parameters
    ----------
    protocol : Protocol
        instance of protocol.
    name : str
        Name for the plate.
    container : str
        Container type name.
    kit_id : str
        Kit item to be created.
    discard : bool
        Determine if plate is discarded after use.
    store : str
        If the plate is not discarded, indicate storage condition.

    Returns
    -------
    kit_item : Container

    """
    kit_item = Container(None, protocol.container_type(container), name)
    if store:
        protocol.refs[name] = Ref(
            name, {"reserve": kit_id, "store": {"where": store}}, kit_item)
    else:
        protocol.refs[name] = Ref(
            name, {"reserve": kit_id, "discard": discard}, kit_item)
    return(kit_item)

# ## Thermocycling helpers


def melt_curve(start=65, end=95, inc=0.5, rate=5):
    """Generate a melt curve on the fly

    No inputs neded for standard.

    Example Usage:

    .. code-block:: python

        temp = melt_params()
        protocol.thermocycle(dest_plate,
                             therm,
                             volume="15:microliter",
                             dataref="data",
                             dyes={"SYBR":dest_plate.all_wells().
                                    indices()},
                             **melt_params)

    Parameters
    ----------
    start : Temperature
        Temperature to start at
    end : Temperature
        Temperature to end at
    inc : Temperature
        Temperature increment during the melt_curve
    rate : seconds
        After x seconds the temperature is incremented by inc

    Returns
    -------
    melt_params : dict
        containing melt_params

    """
    melt_params = {"melting_start": "%f:celsius" % start,
                   "melting_end": "%f:celsius" % end,
                   "melting_increment": "%f:celsius" % inc,
                   "melting_rate": "%f:second" % rate}
    return melt_params


def thermocycle_ramp(start_temp, end_temp, total_duration, step_duration):
    """Create a ramp instruction for the thermocyler.

    Used in annealing protocols.

    Returns
    -------
    thermocycle_steps : dict
        containing thermocycling steps

    """
    assert Unit.fromstring(
        total_duration).unit == Unit.fromstring(
        step_duration).unit, ("Thermocycle_ramp durations"
                              " must be specified using the"
                              " same unit of time.")
    thermocycle_steps = []
    start_temp = Unit.fromstring(start_temp).value
    num_steps = int(
        Unit.fromstring(total_duration).value // Unit.fromstring(
            step_duration).value)
    step_size = (Unit.fromstring(end_temp).value - start_temp) // num_steps
    for i in xrange(0, num_steps):
        thermocycle_steps.append({
            "temperature": "%d:celsius" % (start_temp + i * step_size),
                           "duration": step_duration
        })
    return thermocycle_steps
