from autoprotocol.container import Container, WellGroup, Well
from autoprotocol.unit import Unit
from misc_helpers import flatten_list
from rectangle import binary_list, chop_list, max_rectangle
from collections import namedtuple
from operator import itemgetter
import math
import sys

if sys.version_info[0] >= 3:
    string_type = str
else:
    string_type = basestring


def list_of_filled_wells(wells, empty=False):
    """
    For the container given, determine which wells are filled

    Parameters
    ----------
    wells : Container, WellGroup, List
        Takes a container (uses all wells), a WellGroup or a List of wells
    empty : bool
        If True return empty wells instead of filled

    Returns
    -------
    return_wells : list
        list of wells

    """
    assert isinstance(wells, (Container, WellGroup, list))
    if isinstance(wells, Container):
        wells = wells.all_wells()

    return_wells = []
    for well in wells:
        if not empty:
            if well.volume is not None:
                return_wells.append(well)
        if empty:
            if well.volume is None:
                return_wells.append(well)
    return return_wells


def first_empty_well(wells, return_index=True):
    """
    Get the first empty well of a container followed by only empty wells

    Parameters
    ----------
    wells : Container, WellGroup, List
        Can accept a container, WellGroup or list of wells
    return_index : bool, optional
        Default true, if true returns the index of the well, if false the
        well itself

    Returns
    -------
    well : well or int
        Either the first empty well or the index of the first empty well.
        None when no empty well was found.

    """
    assert isinstance(wells, (Container, WellGroup, list))
    if isinstance(wells, Container):
        wells = list(wells.all_wells())
    else:
        assert len(unique_containers(wells)) == 1
        wells = list(sort_well_group(wells))

    last_well = max(wells, key=lambda x: x.index if x.volume else 0)
    next_index = wells.index(last_well) + 1
    if len(wells) > next_index:
        well = wells[next_index]
    else:
        well = None

    if return_index and well:
        well = well.index

    return well


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


def set_pipettable_volume(well, use_safe_vol=False):
    """Remove dead volume from pipettable volume.

    In one_tip true pipetting operations the volume of the well is used to
    determine who many more wells can be filled from this source well. Thus
    it is useful to remove the dead_volume (default), or the safe minimum from
    the set_volume of the well.
    It is recommeneded to remove the dead_volume only and check for safe_vol
    later.

    Parameters
    ----------
    well : Well, List, WellGroup, Container
    use_safe_vol : bool, optional
        Instead of removing the indicated dead_volume, remove the safe minimum
        volume

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

    correction_vol = cont.container_type.dead_volume_ul
    if use_safe_vol:
        correction_vol = cont.container_type.safe_min_volume_ul

    for x in well:
        x.set_volume(Unit(x.volume.value - correction_vol, "microliter"))

    if r == 'cont':
        return cont
    elif r == 'well':
        return well[0]
    else:
        return well


def volume_check(aliquot, usage_volume=0, use_safe_vol=False,
                 use_safe_dead_diff=False):
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
    use_safe_vol : bool, optional
        Use safe minimum volume instead of dead volume
    use_safe_dead_diff : bool, optional
        Use the safe_minimum_volume - dead_volume as the required amount.
        Useful if `set_pipettable_volume()' was used before to correct the
        well_volume to not include the dead_volume anymore'

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

    correction_vol = aliquot.container.container_type.dead_volume_ul
    message_string = "dead volume"
    volume = aliquot.volume.value
    if use_safe_vol:
        correction_vol = aliquot.container.container_type.safe_min_volume_ul
        message_string = "safe minimum volume"
        volume = aliquot.volume.value
    elif use_safe_dead_diff:
        correction_vol = aliquot.container.container_type.safe_min_volume_ul - \
            aliquot.container.container_type.dead_volume_ul
        message_string = "safe minimum volume"
        volume = aliquot.volume.value + \
            aliquot.container.container_type.dead_volume_ul
    test_vol = correction_vol + usage_volume

    error_message = None
    if test_vol > aliquot.volume.value:
        if usage_volume == 0:
            error_message = ("You want to pipette from a container with %s uL"
                             " %s. However, you aliquot only has "
                             "%s uL.") % (
                correction_vol, message_string, volume)
        else:
            error_message = ("You want to pipette %s uL from a container with"
                             " %s uL %s (%s uL total). However, your"
                             " aliquot only has %s uL.") % (
                usage_volume, correction_vol, message_string,
                usage_volume + correction_vol, volume)
    return error_message


def well_name(well, alternate_name=None):
    """
    Determine the a name that a new well is getting based on old well
    information

    Parameters
    ----------
    well: Well
        well in question
    alternate_name: str, optional
        If this parameter is passed and the well does not have a name, this
        name will be returned instead of the container name, appended with
        the well index

    Returns
    -------
    base_name: str
        well name in the format `name` if the well had a name or `name-index`
        if the name is derived from the container name or alternate_name

    """

    assert isinstance(well, Well)
    if alternate_name:
        assert isinstance(alternate_name, string_type)

    if well.name is not None:
        base_name = well.name
    elif alternate_name:
        base_name = "%s-%s" % (alternate_name, well.index)
    else:
        base_name = "%s-%s" % (well.container.name, well.index)

    return base_name
