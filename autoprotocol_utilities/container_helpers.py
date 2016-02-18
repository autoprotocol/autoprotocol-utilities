from autoprotocol.container import Container, WellGroup, Well
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
        raise RuntimeError("needs a container as input")
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
    Response : namedtuple
        `success` is true if there is an empty well left on the container in
        question
        `well` is the first index that was found to be without volume. May be
        beyond the number of available wells - in that case `success` is false

    """
    r = namedtuple('Response', 'success well')
    well = max(cont.all_wells(),
               key=lambda x: x.index if x.volume else 0).index + 1
    if well < cont.container_type.well_count:
        success = True
    else:
        success = False
    return r(success=success, well=well)


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


def sort_well_group(wells, columnwise=False):
    """Sort a well group in rowwise or columnwise format.

    This function sorts first by container id and name, then by row or
    column, as needed. When the webapp returns aliquot+ inputs, it
    usually does so as a rowwise sorted well group, so this function
    can be useful for re-sorting when necessary.

    Parameters
    ----------
    wells : list, WellGroup
        List of wells to sort
    columnwise : bool, optional

    Returns
    -------
    sorted_well_group : WellGroup
        Sorted list of wells

    """
    if isinstance(wells, list):
        wells = WellGroup(wells)
    assert isinstance(wells, WellGroup), "wells must be an instance"
    " of the WellGroup class or of type list"
    well_list = [(
        well,
        well.container.id,
        well.container.name,
        well.container.decompose(well)[0],
        well.container.decompose(well)[1]
    ) for well in wells
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
    stamp_shape : namedtuple
        `start_well` is the top left well for the source stamp group
        `shape` is a dict of rows and columns describing the stamp shape
        `remainging_wells` is a list of wells that are not included in the
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
    wells_remaining = [x for x in wells if x.index not in wells_included]

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
        next_well = y.start_well + y.shape["columns"]
        z = stamp_shape(y.remaining_wells)
        if len(z.remaining_wells) == 0 and z.start_well == next_well:
            consecutive = True

    shape = False
    if y.shape["rows"] == rows and consecutive:
        shape = True

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


def set_pipettable_volume(well):
    """Remove dead volume from pipettable volume.

    In one_tip true pipetting operations the volume of the well is used to
    determine who many more wells can be filled from this source well. Thus
    it is useful to remove the dead_volume from the set_volume of the well.

    Parameters
    ----------
    well : Well, List, WellGroup, Container

    Returns
    -------
    well : Well, List, WellGroup, Container
        Will return the same type as was received
    """

    if isinstance(well, (list, WellGroup)):
        cont = unique_containers(well)
        if len(cont) > 1:
            raise RuntimeError("Wells can only be from one container")
        else:
            cont = cont[0]
        r = 'list'
    elif isinstance(well, Container):
        cont = well
        well = list_of_filled_wells(cont)
        r = 'cont'
    elif isinstance(well, Well):
        cont = well.container
        well = [well]
        r = 'well'

    dead_volume = cont.container_type.dead_volume_ul
    for x in well:
        x.set_volume(Unit(x.volume.value - dead_volume, "microliter"))

    if r == 'cont':
        return cont
    elif r == 'well':
        return well[0]
    else:
        return well


def volume_check(aliquot, usage_volume=0):
    """
    Takes an aliquot and if usaage_volume is 0 checks if that aliquot
    is above the dead volume for its well type.
    If the usage_volume is set it will check if there is enough volume
    above the dead_volume to execute the pipette.

    Parameters
    ----------
    aliquot : Well
        Well to test
    usage_volume : Unit, str, int, optional
        Volume to test for. If 0 the aliquot will be tested against the
        container dead volume.

    Returns
    -------
    error_message : str or None
        String if volume check failed

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

    error_message = None
    if test_vol > aliquot.volume.value:
        if usage_volume == 0:
            error_message = ("You want to pipette from a container with %s uL"
                             " dead volume. However, you aliquot only has "
                             "%s uL.") % (dead_vol, aliquot.volume.value)
        else:
            error_message = ("You want to pipette %s uL from a container with"
                             " %s uL dead volume (%s uL total). However, your"
                             " aliquot only has %s uL.") % (
                usage_volume, dead_vol, usage_volume + dead_vol,
                aliquot.volume.value)
    return error_message


# Misc helpers

def user_errors_group(error_msgs):
    """Takes a list error messages and neatly displays as a single UserError

    Parameters
    ----------
    error_msgs : list
        List of strings that are the error messages

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


def char_limit(label, length=22, trunc=False, clip=False):
    """Enforces a string limit on the label provided

    Parameters
    ----------
    label : str
        String to test
    length : int, optional
        Maximum label length for this string. Default: 22
    trunc : bool, optional
        Truncate the label if it is too long. Default off.
    clip : bool, optional
        Clip the label (remove from beginning of the string) if it is too long
        Default off. If both trunc and clip are True, trunc will take effect
        and not clip.

    Returns
    -------
    Response : namedtuple
        `label` (str) and `error_message` (string) that is empty on success
        `label` is the unmodified, truncated to clipped label as indicated

    """
    assert isinstance(label, string_type), "Label has to be of type string"

    r = namedtuple('Response', 'label error_message')
    if trunc and len(label) > length:
        label = label[0: length]
    if clip and len(label) > length:
        label = label[len(label) - length: len(label)]

    error_message = None
    if len(label) > length:
        error_message = """The specified label, '%s', has too many
                         characters. Please enter a label of %s
                         or less characters.""" % (label, length)

    return r(label=label, error_message=error_message)
