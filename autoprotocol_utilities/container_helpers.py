from autoprotocol.container import Container, WellGroup, Well
from autoprotocol.container_type import _CONTAINER_TYPES
from autoprotocol.unit import Unit
from misc_helpers import flatten_list
from rectangle import binary_list, chop_list, max_rectangle, get_quadrant_binary_list, get_well_in_quadrant
from collections import namedtuple, Counter
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
    wells : Container, WellGroup, list
        Takes a container (uses all wells), a WellGroup or a List of wells
    empty : bool
        If True return empty wells instead of filled

    Returns
    -------
    return_wells : list
        list of wells

    Raises
    ------
    ValueError
        If wells are not of type list, WellGroup or Container

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
    wells : Container, WellGroup, list
        Can accept a container, WellGroup or list of wells
    return_index : bool, optional
        Default true, if true returns the index of the well, if false the
        well itself

    Returns
    -------
    well : well or int
        Either the first empty well or the index of the first empty well.
        None when no empty well was found.

    Raises
    ------
    ValueError
        If wells are not of type list, WellGroup or Container

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
    """Get unique containers

    Get a list of unique containers for a list of wells

    Parameters
    ----------
    wells : list, WellGroup
        List of wells

    Returns
    -------
    cont : list
        List of Containers

    Raises
    ------
    ValueError
        If wells are not of type list or WellGroup

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

    Raises
    ------
    ValueError
        If wells are not of type list or WellGroup
    ValueError
        If elements of wells are not of type well

    """
    if isinstance(wells, list):
        for well in wells:
            assert isinstance(well, Well)
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


def stamp_shape(wells, full=True, quad=False):
    """Determine if a list of wells is stampable

    Find biggest reactangle that can be stamped from a list of wells. Can be
    any rectangle, or enforce full row or column span.

    Parameters
    ----------
    wells: Container, WellGroup, list
        If Container - all filled wells will be used to determine the shape.
        If list of wells or well_group all provided wells will be analyzed.
    full: bool, optional
        If true will only return shapes that span either the full rows or
        columns of the container.
    quad: bool, optional
        Set to true if you want to get the stamp shape for a 384 well testing
        all quadrants. False is used for determining col- vs row-wise. True
        is used to initiate the correct stamping.

    Returns
    -------
    stamp_shape : list of namedtuple
        `start_well` is the top left well for the source stamp group
        `shape` is a dict of rows and columns describing the stamp shape
        `remainging_wells` is a list of wells that are not included in the
        stamp shape.
        If a 384 well plate is provided and quad is True this returns a list
        of 4 stamp shapes, one for each quadrant.

    Raises
    ------
    RuntimeError
        If wells are not of type list or WellGroup
    ValueError
        If elements of wells are not of type well
    ValueError
        If wells are not from one container only

    """
    if isinstance(wells, Container):
        cont = wells
        wells = list_of_filled_wells(wells)
    elif isinstance(wells, (list, WellGroup)):
        assert len(unique_containers(wells)) == 1, "Stamp_shape: wells have "
        "to come from one container"
        for well in wells:
            assert isinstance(well, (Well)), "Stamp_shape: elements of wells"
            " have to be of type Well"
        wells = sort_well_group(wells)
        cont = unique_containers(wells)[0]
    else:
        raise RuntimeError("Stamp_shape: wells has to be a list or a "
                           "WellGroup")

    def make_stamp_tuple(r, rows, cols, q=None):
        height = r.height
        width = r.width
        if full:
            if not (r.height == rows or r.width == cols):
                height = 0
                width = 0
        # Determine start_well and wells not included in the rectangle
        if width != 0 or height != 0:
            start_index = (r.y * cols) + r.x
        else:
            start_index = None
        # Determine wells_included
        wells_included = []
        for y in range(height):
            for z in range(width):
                wells_included.append(start_index + y*cols + z)
        # 384 well case
        if q is not None:
            wells_included = get_well_in_quadrant(wells_included, q)
            if width != 0 or height != 0:
                start_index = get_well_in_quadrant([start_index], q)[0]

        # Determine wells_idx_remaining
        wells_idx_remaining = [x.index for x in wells if x.index not in
                               wells_included]
        # Convert all indices to wells
        if start_index is not None:
            start_well = [x for x in wells if x.index == start_index][0]
        else:
            start_well = start_index
        wells_remaining = [x for x in wells if x.index in wells_idx_remaining]
        wells_included = [x for x in wells if x.index in wells_included]
        r = stamp_shape(start_well=start_well,
                        shape=dict(rows=height, columns=width),
                        remaining_wells=wells_remaining,
                        included_wells=wells_included)
        return r

    stamp_shape = namedtuple(
        'Stamp', 'start_well shape remaining_wells included_wells')
    rows = cont.container_type.row_count()
    cols = cont.container_type.col_count
    well_count = cont.container_type.well_count
    indices = [x.index for x in wells]

    bnry_list = [bnry for bnry in binary_list(indices, length=well_count)]
    if well_count == 384 and quad:
        bnry_list_list = get_quadrant_binary_list(bnry_list)
        temp_shape = []
        temp_remaining_wells = []
        remaining_wells = []
        for i, bnry_list in enumerate(bnry_list_list):
            bnry_mat = chop_list(bnry_list, 12)
            r = max_rectangle(bnry_mat, value=1)
            temp_shape.append(make_stamp_tuple(r, rows/2, cols/2, i))
            temp_remaining_wells.append(temp_shape[i].remaining_wells)
        temp_remaining_wells = Counter(flatten_list(temp_remaining_wells))
        for k, v in temp_remaining_wells.iteritems():
            if v == 4:
                remaining_wells.append(k)
        shape = []
        for s in temp_shape:
            shape.append(stamp_shape(start_well=s.start_well,
                                     shape=s.shape,
                                     remaining_wells=remaining_wells,
                                     included_wells=s.included_wells))
    else:
        bnry_mat = chop_list(bnry_list, cols)
        r = max_rectangle(bnry_mat, value=1)
        shape = [make_stamp_tuple(r, rows, cols)]

    return shape


def is_columnwise(wells):
    """Detect if input wells are in a columnwise format.

    This function only triggers if the first column is full and only
    consecutive fractionally filled columns exist. It is used to determine
    whether `columnwise` should be used in a pipette operation.

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

    Raises
    ------
    ValueError
        If wells are not of type list or WellGroup
    ValueError
        If elements of wells are not of type Well

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
    y = stamp_shape(wells, full=False)[0]

    consecutive = False
    if len(y.remaining_wells) == 0:
        consecutive = True
    else:
        next_well = y.start_well.index + y.shape["columns"]
        z = stamp_shape(y.remaining_wells, full=False)[0]
        if len(z.remaining_wells) == 0 and z.start_well.index == next_well:
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
        How many you have available per unit. If container, then all wells of
        this container will be considered

    Returns
    -------
    i : int
        How many of unit you will need to accomodate all wells_needed

    Raises
    ------
    RuntimeError
        If wells_needed is not of type integer or float
    RuntimeError
        If wells_available is not of type integer or float or Container

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
    well : Container, WellGroup, list, Well
    use_safe_vol : bool, optional
        Instead of removing the indicated dead_volume, remove the safe minimum
        volume

    Returns
    -------
    well : Container, WellGroup, list, Well
        Will return the same type as was received

    Raises
    ------
    RuntimeError
        If wells are spread across multiple containers

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


def volume_check(well, usage_volume=0, use_safe_vol=False,
                 use_safe_dead_diff=False):
    """Basic Volume check

    Takes an aliquot and if usaage_volume is 0 checks if that aliquot
    is above the dead volume for its well type.
    If the usage_volume is set it will check if there is enough volume
    above the dead_volume to execute the pipette.

    Parameters
    ----------
    well : Well, WellGroup, list
        Well(s) to test
    usage_volume : Unit, str, int, optional
        Volume to test for. If 0 the aliquot will be tested against the
        container dead volume.
    use_safe_vol : bool, optional
        Use safe minimum volume instead of dead volume
    use_safe_dead_diff : bool, optional
        Use the safe_minimum_volume - dead_volume as the required amount.
        Useful if `set_pipettable_volume()` was used before to correct the
        well_volume to not include the dead_volume anymore

    Returns
    -------
    error_message : str or None
        String if volume check failed

    Raises
    ------
    ValueError
        If well is not of type Well, list or WellGroup
    ValueError
        If elements of well are not of type Well

    """

    assert isinstance(well, (Well, WellGroup, list))
    if isinstance(well, Well):
        well = [well]

    error_message = []
    for aliquot in well:
        assert isinstance(aliquot, Well)
        if isinstance(usage_volume, Unit):
            usage_volume = usage_volume.value
        if isinstance(usage_volume, string_type):
            usage_volume = int(usage_volume.split(":microliter")[0])
        if not aliquot.volume:
            error_message.append(
                "Your aliquot does not have a volume. (%s) We assume 0 uL "
                "for this test." % aliquot)

        correction_vol = aliquot.container.container_type.dead_volume_ul
        message_string = "dead volume"
        volume = 0 if not aliquot.volume else aliquot.volume.value
        if use_safe_vol:
            correction_vol = aliquot.container.container_type.safe_min_volume_ul
            message_string = "safe minimum volume"
        elif use_safe_dead_diff:
            correction_vol = aliquot.container.container_type.safe_min_volume_ul - \
                aliquot.container.container_type.dead_volume_ul
            message_string = "safe minimum volume"
            volume = volume + aliquot.container.container_type.dead_volume_ul
        test_vol = correction_vol + usage_volume

        if test_vol > volume:
            if usage_volume == 0:
                error_message.append(
                    "You want to pipette from a container with %s uL %s. "
                    "However, you aliquot only has %s uL." %
                    (correction_vol, message_string, volume))
            else:
                error_message.append(
                    "You want to pipette %s uL from a container with %s uL %s"
                    " (%s uL total). However, your aliquot only has %s uL." %
                    (usage_volume, correction_vol, message_string,
                     usage_volume + correction_vol, volume))
    error_message = error_message if len(error_message) > 0 else None
    return error_message


def well_name(well, alternate_name=None):
    """Determine new well name

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

    Raises
    ------
    ValueError
        If well is not of type Well
    ValueError
        It alternate_name is not of type string
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


def container_type_checker(containers, shortname, exclude=False):
    """Verify container is of specified container_type.

    Parameters
    ----------
    containers : Container, list
        Single Container or list of Containers
    shortname : str, list of str
        Short name used to specify ContainerType.
    exclude: bool, optional
        Verify container is NOT of specified container_type.
    Returns
    -------
    error_message : list of strings or True
        List containing containers failing container_type_check or True.

    Raises
    ------
    ValueError
        If an unknown ContainerType shortname is passed.
    ValueError
        If an containers are not of type Container.
    """
    if isinstance(shortname, list):
        for short in shortname:
            assert short in _CONTAINER_TYPES, ("container_type_check: unknown"
                                               " container shortname: %s , "
                                               "(known types: %s)" %
                                               (short,
                                                str(_CONTAINER_TYPES.keys())))
    elif isinstance(shortname, str):
        assert shortname in _CONTAINER_TYPES, ("container_type_check: unknown"
                                               " container shortname: %s , "
                                               "(known types: %s)" %
                                               (shortname,
                                                str(_CONTAINER_TYPES.keys())))
    if isinstance(containers, list):
        for cont in containers:
            assert isinstance(cont, Container), ("container_type_check: "
                                                 "containers to check"
                                                 "must be of type Container")
    elif isinstance(containers, Container):
        containers = [containers]
    else:
        raise ValueError(
            "container_type_check: containers to check must be of type "
            "Container")

    error_messages = []

    for cont in containers:
        if exclude:
            if cont.container_type.shortname in shortname:
                error_messages.append(
                    "%s is of the excluded type %s" % (cont, shortname))

        else:
            if cont.container_type.shortname not in shortname:
                error_messages.append("%s not of type %s" % (cont, shortname))

    if len(error_messages) > 0:
        return error_messages
    else:
        return None


def get_well_list_by_cont(wells):
    """Get wells sorted by container

    Parameters
    ----------
    wells: list, WellGroup

    Returns
    -------
    well_map: dict
        Dict with containers as keys and List of wells as value

    Raises
    ------
    ValueError
        If wells is not of type list or WellGroup
    ValueError
        If elements of wells are not of type Well

    """
    assert isinstance(wells, (list, WellGroup))
    for well in wells:
        assert isinstance(well, Well)

    conts = unique_containers(wells)
    well_map = {}
    for cont in conts:
        well_map[cont] = []
        well_map[cont].extend(
            [well for well in wells if well.container == cont])

    return well_map
