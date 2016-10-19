from autoprotocol.container import Container, WellGroup, Well
from autoprotocol.container_type import _CONTAINER_TYPES
from autoprotocol.unit import Unit
from .misc_helpers import flatten_list
from .rectangle import binary_list, chop_list, max_rectangle, \
    get_quadrant_binary_list, get_well_in_quadrant
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
    list
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
        Can accept a container, WellGroup or list of wells.
    return_index : bool, optional
        Default true, if true returns the index of the well, if false the
        well itself.

    Returns
    -------
    well
        The first empty well OR
    int
        The index of the first empty well when return_index=True OR
    None
        when no empty well was found.

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

    Example Usage:

    .. code-block:: python

        from autoprotocol import Protocol
        from autoprotocol_utilities import get_well_list_by_cont

        p = Protocol()

        wells_1 = p.ref("plate_1_96", None, "96-flat",
                        discard=True).wells_from("A1", 12)
        wells_2 = p.ref("plate_2_96", None, "96-flat",
                        discard=True).wells(0, 24, 49)
        wells_3 = p.ref("plate_3_96", None, "96-flat",
                        discard=True).well("D3")

        many_wells = wells_1 + wells_2 + wells_3
        unique_containers(many_wells)

    Returns:

    .. code-block:: python

        [Container(plate_1_96), Container(plate_3_96), Container(plate_2_96)]

    Parameters
    ----------
    wells : Well, list, WellGroup
        List of wells.

    Returns
    -------
    list
        List of Containers

    Raises
    ------
    ValueError
        If wells are not of type list or WellGroup

    """
    if isinstance(wells, Well):
        wells = [wells]
    assert isinstance(wells, (list, WellGroup)), "unique_containers requires"
    " a Well, list of wells or a WellGroup"
    if isinstance(wells, WellGroup):
        wells = list(wells)
    wells = flatten_list(wells)
    cont = list(set([well.container for well in wells]))
    return cont


def sort_well_group(wells, columnwise=False):
    """Sort a well group in rowwise or columnwise format.

    This function sorts first by container id and name, then by row or
    column, as needed. This function is useful to sort a list of wells
    passed in an unknown order (eg. user entered).

    Parameters
    ----------
    wells : list, WellGroup
        List of wells to sort.
    columnwise : bool, optional

    Returns
    -------
    WellGroup
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
    If a list of wells from a container that cannot be stamped is provided,
    all wells will be returned in `remaining_wells` of the stamp shape.

    Example Usage:

    .. code-block:: python

        from autoprotocol import Protocol
        from autoprotocol_utilities import stamp_shape, first_empty_well, \
            flatten_list

        p = Protocol()
        plate = p.ref("myplate", cont_type="96-pcr", storage="cold_4")
        dest_plate = p.ref("newplate", cont_type="96-pcr", storage="cold_4")
        src_wells = plate.wells_from(0, 40)
        shape = stamp_shape(src_wells)
        remaining_wells = []
        for s in shape:
            p.stamp(s.start_well, dest_plate.well(0),
                    "10:microliter", s.shape)
            remaining_wells.append(s.remaining_wells)
        next_dest = first_empty_well(dest_plate)
        remaining_wells = flatten_list(remaining_wells)
        p.transfer(remaining_wells,
                   dest_plate.wells_from(next_dest, len(remaining_wells)),
                   "10:microliter"
                   )

    Autoprotocol Output:

    .. code-block:: json

        {
            "refs": {
                "myplate": {
                    "new": "96-pcr",
                    "store": {
                        "where": "cold_4"
                    }
                },
                "newplate": {
                    "new": "96-pcr",
                    "store": {
                        "where": "cold_4"
                    }
                }
            },
            "instructions": [
                {
                    "groups": [
                        {
                            "transfer": [
                                {
                                    "volume": "10.0:microliter",
                                    "to": "newplate/0",
                                    "from": "myplate/0"
                                }
                            ],
                            "shape": {
                                "rows": 3,
                                "columns": 12
                            },
                            "tip_layout": 96
                        }
                    ],
                    "op": "stamp"
                },
                {
                    "groups": [
                        {
                            "transfer": [
                                {
                                    "volume": "10.0:microliter",
                                    "to": "newplate/36",
                                    "from": "myplate/36"
                                }
                            ]
                        },
                        {
                            "transfer": [
                                {
                                    "volume": "10.0:microliter",
                                    "to": "newplate/37",
                                    "from": "myplate/37"
                                }
                            ]
                        },
                        {
                            "transfer": [
                                {
                                    "volume": "10.0:microliter",
                                    "to": "newplate/38",
                                    "from": "myplate/38"
                                }
                            ]
                        },
                        {
                            "transfer": [
                                {
                                    "volume": "10.0:microliter",
                                    "to": "newplate/39",
                                    "from": "myplate/39"
                                }
                            ]
                        }
                    ],
                    "op": "pipette"
                }
            ]
        }

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
    list
        contains namedtuples where each tuple has the following parameters

    start_well: well
        is the top left well for the source stamp group
    shape: dict
        is a dict of `rows` and `columns` describing the stamp shape
    remainging_wells: list
        is a list of wells that are not included in the stamp shape
    included_wells: list
        is a list of wells that is included in the stamp shape


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
            assert isinstance(well, Well), "Stamp_shape: elements of wells"
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
        if width != 0 or height != 0:
            start_index = (r.y * cols) + r.x
        else:
            start_index = None
        wells_included = []
        for y in range(height):
            for z in range(width):
                wells_included.append(start_index + y * cols + z)
        if q is not None:
            wells_included = get_well_in_quadrant(wells_included, q)
            if width != 0 or height != 0:
                start_index = get_well_in_quadrant([start_index], q)[0]

        wells_idx_remaining = [x.index for x in wells if x.index not in
                               wells_included]
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

    if well_count not in (96, 384):
        shape = stamp_shape(start_well=None,
                            shape=dict(rows=0, columns=0),
                            remaining_wells=wells,
                            included_wells=[])
        return [shape]

    bnry_list = [bnry for bnry in binary_list(indices, length=well_count)]
    if well_count == 384 and quad:
        bnry_list_list = get_quadrant_binary_list(bnry_list)
        temp_shape = []
        temp_remaining_wells = []
        remaining_wells = []
        for i, bnry_list in enumerate(bnry_list_list):
            bnry_mat = chop_list(bnry_list, 12)
            r = max_rectangle(bnry_mat, value=1)
            temp_shape.append(make_stamp_tuple(r, rows / 2, cols / 2, i))
            temp_remaining_wells.append(temp_shape[i].remaining_wells)
        temp_remaining_wells = Counter(flatten_list(temp_remaining_wells))
        for k, v in temp_remaining_wells.items():
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

    This function only triggers if the first column is full and only a
    consecutive fractionally filled columns exist. It is used to determine
    whether `columnwise` should be used in a pipette operation.

    Only accepts wells that belong to 1 container. Use unique_containers or
    get_well_list_by_cont to assure you submit only wells from one container.

    Patterns detected (4x6 plate):

    .. code-block:: none

        x x   | x x x  | x | x
        x     | x x x  | x | x
        x     | x x x  | x | x
        x     | x x x  | x |

    Patterns NOT detected (4x6 plate):

    .. code-block:: none

        x x x  | x      |
          x x  | x      |
          x x  | x      |
          x x  | x x x  |

    Example Usage:

    .. code-block:: python

        from autoprotocol.protocol import Protocol
        from autoprotocol_utilities import is_columnwise

        p = Protocol()
        plate = p.ref("plate", None, cont_type="96-flat", storage="cold_4",
                      cover="standard")
        col_wells = plate.wells_from(start="A1", num=17, columnwise=True)
        col_wells_2 = plate.wells_from(start="A2", num=17, columnwise=True)
        row_wells = plate.wells_from(start="A1", num=17, columnwise=False)
        rand_wells = plate.wells("A2", "B12", "H7")

        is_columnwise(col_wells)
        is_columnwise(col_wells_2)
        is_columnwise(row_wells)
        is_columnwise(rand_wells)

    Returns:

    .. code-block:: python

        True
        True
        False
        False

    Parameters
    ----------
    wells: Well, list, WellGroup
        List of wells or well_group containing the wells in question.

    Returns
    -------
    bool
        True if columnwise. False if rowwise.
    list
        List of strings if errors were encountered.

    Raises
    ------
    ValueError
        If wells are not of type Well, list or WellGroup
    ValueError
        If elements of wells are not of type Well

    """

    em = []
    colwise = False
    if isinstance(wells, Well):
        colwise = False
    else:
        assert isinstance(wells, (list, WellGroup)), "is_columnwise: wells"
        " has to be a list or a WellGroup"
        for well in wells:
            assert isinstance(well, (Well)), "is_columnwise: elements of "
            "wells have to be of type Well"
        if len(unique_containers(wells)) != 1:
            em.append("is_columnwise: wells have to come from one container")

    cont = unique_containers(wells)[0]

    all_wells = list(cont.all_wells(columnwise=True))
    top_wells = list(cont.wells_from(0, cont.container_type.col_count))
    wells = sort_well_group(wells, columnwise=True)

    if wells[0] in top_wells:
        top_well = top_wells[top_wells.index(wells[0])]
        start = all_wells.index(top_well)
        for x in range(len(wells)):
            if wells[x] == all_wells[start]:
                colwise = True
                start += 1
            else:
                colwise = False
                break
    else:
        colwise = False

    em = [_f for _f in em if _f]
    if len(em) > 0:
        return em
    else:
        return colwise


def plates_needed(wells_needed, wells_available):
    """
    Takes wells needed as a numbers (int or float)
    and wells_available as a container, container type string or a well number
    (int or float) and calculates how many plates are
    needed to accomodate the wells_needed.

    Parameters
    ----------
    wells_needed: float, int
        How many you need
    wells_available: Container, float, int, string
        How many you have available per unit. If container or a string
        identifying a container type, then all wells of
        this container will be considered

    Returns
    -------
    int
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
    elif isinstance(wells_available, string_type):
        cont = _CONTAINER_TYPES.get(wells_available, None)
        if cont:
            wells_available = float(cont.well_count)
        else:
            raise RuntimeError("If `wells_available` is a string, it has to "
                               "match a valid `container_type`. %s does not "
                               "match any container type" % wells_available)
    elif isinstance(wells_available, int):
        wells_available = float(wells_available)
    elif not isinstance(wells_available, (float, int, Container, string_type)):
        raise RuntimeError("wells_available has to be a container, a string "
                           "uniquely identifying a container type, "
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
        Well to set.
    use_safe_vol : bool, optional
        Instead of removing the indicated dead_volume, remove the safe minimum
        volume.

    Returns
    -------
    Container, WellGroup, list, Well
        Will return the same type as was received

    """

    cont = {}
    if isinstance(well, (list, WellGroup)):
        cont = get_well_list_by_cont(well)
    elif isinstance(well, Container):
        cont[well] = list_of_filled_wells(well)
    elif isinstance(well, Well):
        cont[well.container] = [well]

    for c, w in cont.items():
        correction_vol = c.container_type.dead_volume_ul
        if use_safe_vol:
            correction_vol = c.container_type.safe_min_volume_ul
        for x in w:
            x.set_volume(x.volume - correction_vol)

    return well


def volume_check(well, usage_volume=0, use_safe_vol=False,
                 use_safe_dead_diff=False):
    """Basic Volume check

    Checks to see if the designated well has usage_volume above the well's
    dead volume. In other words, this method checks if usage_volume can be
    pipetted out of well.

    Example Usage:

    .. code-block:: python

            from autoprotocol import Protocol
            from autoprotocol_utilities.container_helpers import volume_check

            p = Protocol()
            example_container = p.ref(name="exampleplate", id=None,
                                      cont_type="96-pcr", storage="warm_37")
            p.dispense(ref=example_container, reagent="water",
                       columns=[{"column": 0, "volume": "10:microliters"}])

            #Checks if there are 5 microliters above the dead volume
            #available in well 0
            assert (volume_check(well=example_container.well(0),
                    usage_volume=5)) is None
            #Checks if the volume in well 0 is at least the safe minimum volume
            assert (volume_check(well=example_container.well(0),
                    usage_volume=0, use_safe_vol=True) is None

    Parameters
    ----------
    well : Well, WellGroup, list
        Well(s) to test
    usage_volume : Unit, str, int, float, optional
        Volume to test for. If 0 the aliquot will be tested against the
        container dead volume. If int or float is used, microliter will be
        assumed.
    use_safe_vol : bool, optional
        Use safe minimum volume instead of dead volume
    use_safe_dead_diff : bool, optional
        Use the safe_minimum_volume - dead_volume as the required amount.
        Useful if `set_pipettable_volume()` was used before to correct the
        well_volume to not include the dead_volume anymore

    Returns
    -------
    str
        string of errors if volume check failed OR
    None
        If no errors are detected

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
    # noinspection PyTypeChecker
    for aliquot in well:
        assert isinstance(aliquot, Well)
        if isinstance(usage_volume, (int, float)):
            usage_volume = Unit(usage_volume, "microliter")
        if isinstance(usage_volume, string_type):
            usage_volume = int(usage_volume.split(":microliter")[0])
        if not aliquot.volume:
            error_message.append(
                "Your aliquot does not have a volume. (%s) We assume 0 uL "
                "for this test." % aliquot)

        correction_vol = aliquot.container.container_type.dead_volume_ul
        message_string = "dead volume"
        volume = Unit(0, "microliter")
        if aliquot.volume:
            volume = aliquot.volume
        if use_safe_vol:
            correction_vol = \
                aliquot.container.container_type.safe_min_volume_ul
            message_string = "safe minimum volume"
        elif use_safe_dead_diff:
            correction_vol = \
                aliquot.container.container_type.safe_min_volume_ul - \
                aliquot.container.container_type.dead_volume_ul
            message_string = "safe minimum volume"
            volume = volume + aliquot.container.container_type.dead_volume_ul
        test_vol = correction_vol + usage_volume

        if test_vol > volume:
            if usage_volume == 0:
                error_message.append(
                    "You want to pipette from a container with {:~P} {!s}. "
                    "However, your aliquot: {!s}, only has {:~P}.".format(
                        correction_vol, message_string,
                        well_name(aliquot), volume))
            else:
                error_message.append(
                    "You want to pipette {:~P} from a container with {:~P} "
                    "{!s} ({:~P} total). However, your aliquot: {!s}, only has"
                    " {:~P}.".format(
                        usage_volume, correction_vol, message_string,
                        usage_volume + correction_vol,
                        well_name(aliquot), volume))
    if error_message:
        error_message = str(len(error_message)) + " volume errors: " + \
            ", ".join(error_message)
    else:
        error_message = None
    return error_message


def well_name(well, alternate_name=None, humanize=False):
    """Determine new well name

    Determine the name for a new well based on passed well.

    Parameters
    ----------
    well: Well
        Well to source original name, index properties.
    alternate_name: str, optional
        If this parameter is passed and the well does not have a name, this
        name will be returned instead of the container name, appended with
        the well index.

    Returns
    -------
    str
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

    if humanize:
        well_index = well.container.humanize(well.index)
    else:
        well_index = well.index

    if well.name is not None:
        base_name = well.name
    elif alternate_name:
        base_name = "%s-%s" % (alternate_name, well_index)
    else:
        base_name = "%s-%s" % (well.container.name, well_index)

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
    str
        String of containers failing container_type_check OR
    None
        If no container fails

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
                                                str(list(
                                                    _CONTAINER_TYPES.keys()))))
    elif isinstance(shortname, str):
        assert shortname in _CONTAINER_TYPES, ("container_type_check: unknown"
                                               " container shortname: %s , "
                                               "(known types: %s)" %
                                               (shortname,
                                                str(list(
                                                    _CONTAINER_TYPES.keys()))))
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

    error_containers = []
    error_message = None

    for cont in containers:
        if exclude:
            if cont.container_type.shortname in shortname:
                error_containers.append(str(cont))
        else:
            if cont.container_type.shortname not in shortname:
                error_containers.append(str(cont))

    if error_containers:
        message_ending = ' not of the required type(s): ' + \
                         ', '.join(shortname)
        if exclude:
            message_ending = ' of the excluded type(s): ' + \
                             ', '.join(shortname)
        error_message = "Incompatible container(s) found : " + \
                        ', '.join(error_containers) + message_ending

    return error_message


def get_well_list_by_cont(wells):
    """Get wells sorted by container

    Example Usage:

    .. code-block:: python

        from autoprotocol import Protocol
        from autoprotocol_utilities import get_well_list_by_cont

        p = Protocol()

        wells_1 = p.ref("plate_1_96", None, "96-flat",
                        discard=True).wells_from("A1", 12)
        wells_2 = p.ref("plate_2_96", None, "96-flat",
                        discard=True).wells(0, 24, 49)
        wells_3 = p.ref("plate_3_96", None, "96-flat",
                        discard=True).well("D3")

        many_wells = wells_1 + wells_2 + wells_3
        get_well_list_by_cont(many_wells)

    Returns:

    .. code-block:: python

        {
            Container(plate_1_96): [
                Well(Container(plate_1_96), 0, None),
                Well(Container(plate_1_96), 1, None),
                Well(Container(plate_1_96), 2, None)
                ],
            Container(plate_3_96): [
                Well(Container(plate_3_96), 38, None)
                ],
            Container(plate_2_96): [
                Well(Container(plate_2_96), 0, None),
                Well(Container(plate_2_96), 24, None),
                Well(Container(plate_2_96), 49, None)
                ]
        }

    Parameters
    ----------
    wells: list, WellGroup
        The list of wells to be sorted by the containers that they are in

    Returns
    -------
    dict
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


def next_wells(target, num=1, columnwise=False):
    '''
    Given a plate, a list of plates or a WellGroup, returns a generator
    function that can be used to iterate through the (container's) wells.

    Example Usage:

    .. code-block:: python

        from autoprotocol import Protocol
        from autoprotocol_utilities import next_wells

        p = Protocol()
        c1 = p.ref("c1", id=None, cont_type="96-pcr", discard=True)

        assay_wells = next_wells(c1, num=2, columnwise=False)
        my_wells = []
        your_wells = []
        my_wells.extend(next(assay_wells))
        your_wells.extend(next(assay_wells))
        your_wells.extend(next(assay_wells))
        your_wells

    Returns:

    .. code-block:: python

        [
            Well(Container(c1), 2, None),
            Well(Container(c1), 3, None),
            Well(Container(c1), 4, None),
            Well(Container(c1), 5, None)
        ]

    Parameters
    ----------

    target: Container, List of Containers, WellGroup
        The generator will iteratively return wells from these plate(s)
        or WellGroup, in order, from the first well in the list,
        based on the parameters below.
    num: int, optional
        The generator will produce this many wells with each iteration.
        Defaults to 1.
    columnwise: bool, optional
        Set to True if wells should be generated in columnwise
        format. Defaults to False. If a WellGroup is given this parameter is
        ignored.

    Returns
    -------

    generator:
        This function will iteratively generate the next set of
        wells from the plate. Get the next plates using
        `next(generator)`. Wells will be returned as a
        WellGroup.

    Raises
    ------
    ValueError
        If `target` is not a Container, a list of Containers or a WellGroup
    RumtimeError
        If all wells have been used
    '''
    next_index = 0
    assert isinstance(target, (list, Container, WellGroup)), (
        "target must be a Container or a list of Containers or WellGroup")

    well_list = []
    if isinstance(target, Container):
        well_list.extend(target.all_wells(columnwise=columnwise))
    if isinstance(target, list):
        for p in target:
            assert isinstance(p, Container), ("all elements of `target` "
                                              "must be Containers")
        for t in target:
            well_list.extend(t.all_wells(columnwise=columnwise))
    elif isinstance(target, WellGroup):
        well_list = list(target)
    while next_index <= len(well_list) - num:
        yield well_list[next_index:(next_index + num)]
        next_index += num
    else:
        raise RuntimeError("Want to generate {!s} wells, "
                           "but only have {!s} left.".format(
                               (num),
                               (len(well_list) - num)))
