from autoprotocol.container import Container, WellGroup, Well
from autoprotocol.protocol import Ref
from autoprotocol.unit import Unit
from autoprotocol import UserError
from itertools import groupby
from operator import itemgetter
import datetime
import math
import sys

if sys.version_info[0] >= 3:
    string_type = str
else:
    string_type = basestring


def list_of_filled_wells(cont, empty=False):
    '''
        For the container given, determine which wells are filled

        Parameters
        ----------
        cont  = container
        empty = bool, if True return empty wells instead of filled

        Returns
        -------
        list of wells
    '''
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
    '''
        Get the first empty well of a container followed by only empty wells

        Parameters
        ----------
        cont = container

        Returns
        -------
        on success: well
        on failure: string
    '''
    well = max(cont.all_wells(),
               key=lambda x: x.index if x.volume else 0).index + 1
    if well < cont.container_type.well_count:
        return well
    else:
        return "The container has no empty wells left"


def unique_containers(wells):
    '''
        Get a list of unique containers for a list of wells

        Parameters
        ----------
        wells = list of wells

        Returns
        -------
        Container
    '''
    assert isinstance(wells, (list, WellGroup)), "unique_containers requires"
    " a list of wells or a WellGroup"
    wells = flatten_list(wells)
    cont = list(set([well.container for well in wells]))
    return cont


def sort_well_group(well_group, columnwise=False):
    '''
        Sort a well group in rowwise or columnwise format.
        This function sorts first by container id and name, then by row or
        column, as needed. When the webapp returns aliquot+ inputs, it
        usually does so as a rowwise sorted well group, so this function
        can be useful for re-sorting when necessary.
    '''
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


# detect stamp shape

# def primer_index(wells):

#     if wells[0].index < 12 and wells[-1].index > 83:
#         row_check = False
#     else:
#         row_check = True

#     if row_check:
#         num_primers = 12
#     else:
#         num_primers = 8

#     if len(wells) % num_primers != 0:
#         raise UserError("Error with %s: Must include multiple of %s primers" % (wells[0], num_primers))
#     for w in wells:
#         if w.container != wells[0].container:
#             raise UserError("Error with %s: Primers of a set must be in the same container" % w)
#     well_index = [w.index for w in wells]
#     if row_check:
#         if well_index != range(well_index[0], well_index[0]+len(wells)):
#             raise UserError("Error with %s: Primers must be in the same row" % wells[0])
#         if well_index[0] % 12 != 0:
#             raise UserError("Error with %s: First primer must be in the first column" % wells[0])
#     else:
#         if [(w - well_index[0]) % 12 for w in well_index] != [x/8 for x in range(len(well_index))]:
#             raise UserError("Error with %s: Primers must be in the same colume" % wells[0])
#         if well_index[0] > 12:
#             raise UserError("Error with %s: First primer must be in the first row" % wells[0])

#     if row_check:
#         shape = {"rows": len(wells)/12, "columns": 12}
#     else:
#         shape = {"rows": 8, "columns": len(wells)/8}

#     return wells[0], shape


def stamp_shape(wells):
    """
        Find biggest reactangle that can be stamped. Consequtive columns and
        rows.

        Returns
        -------
        dict of:
            start_well
            shape
            wells not included
    """
    assert len(unique_containers(wells)) == 1, "stamp shape can only take"
    "wells from one container"
    wells = sort_well_group(wells)
    indices = [x.index for x in wells]
    start_well = wells[0]

    cols = 0
    rows = 0

    idx = start_well.index + 1
    for well in wells:
        if idx == well.index:
            cols += 1
            idx += 1
        else:
            idx -= 1
            break
        # what happens if i use this with the sort key itemgetter function from above

    # return start_well, shape, wells not included


def detect_well_shape(wells):
    assert isinstance(wells, (list, WellGroup)), "Detect_well_shape: wells"
    "has to be a list or a WellGroup"
    assert len(unique_containers(wells)) == 1, "Detect_well_shape: wells have"
    " to come from one container"
    indices = []
    for well in wells:
        assert isinstance(well, (Well)), "Detect_well_shape: elements of "
        "wells have to be of type Well"
        indices.append(well.index)

    well_groups = []
    for k, g in groupby(enumerate(indices), lambda ix: ix[0] - ix[1]):
        well_groups.append(map(itemgetter(1), g))
    # this is not sufficient yet - need to check that the first elements are 12 consecutive
    if len(well_groups) == 8:
        shape = "column"
    else:
        shape = "row"

    return shape


def plates_needed(wells_needed, wells_available):
    '''
        Takes wells needed as a numbers (int or float)
        and wells_available as a container or a well number
        (int or float) and calculates how many plates are
        needed to accomodate the wells_needed.
    '''
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
    '''
        Takes an aliquot and if usaage_volume is 0 checks if that aliquot
        is above the dead volume for its well type.
        If the usage_volume is set it will check if there is enough volume
        above the dead_volume to execute the
        pipette.
        Usage volume can be a Unit, a string of type "3:microliter" or an
        integer
    '''
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
    '''
        Takes a list error messages and neatly displays as a single UserError
    '''
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
    printdate = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    return printdate


def printdate():
    printdate = datetime.datetime.now().strftime('%Y-%m-%d')
    return printdate


def make_list(my_str, integer=False):
    '''
        Sometimes you need a list of a type that is not supported.

        Parameters
        ----------
        my_str   = string with individual elements separated by comma
        interger = bool, if true list of integers instead of list of strings
                   is returned.
    '''
    assert isinstance(my_str, string_type), "Input needs to be of type string"
    if integer:
        my_str = [int(x.strip()) for x in my_str.split(",")]
    else:
        my_str = [x.strip() for x in my_str.split(",")]
    return my_str


def flatten_list(l):
    '''
        Flatten a list recursively without for loops or additional modules

        Parameters
        ---------
        l = list to flatten

        Returns
        -------
        flat list
    '''
    if l == []:
        return l
    if isinstance(l[0], list):
        return flatten_list(l[0]) + flatten_list(l[1:])
    return l[:1] + flatten_list(l[1:])


def thermocycle_ramp(start_temp, end_temp, total_duration, step_duration):
    '''
        Create a ramp instruction for the thermocyler. Used in annealing
        protocols.
    '''
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


def det_new_group(i, base=0):
    '''
        Helper to determine if new_group should be added. Returns true when
        i matches the base, which defaults to 0.
    '''
    assert isinstance(i, int), "Needs an integer."
    assert isinstance(base, int), "Base has to be an integer"
    if i == base:
        new_group = True
    else:
        new_group = False
    return new_group


def return_agar_plates(wells=6):
    '''
        Dicts of all plates available that can be purchased.
    '''
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
    '''
        Dict of media for reagent dispenser
    '''
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


def melt_curve(start=65, end=95, inc=0.5, rate=5):
    '''
        Generate a melt curve on the fly. No inputs neded for standard
    '''
    melt_params = {"melting_start": "%f:celsius" % start,
                   "melting_end": "%f:celsius" % end,
                   "melting_increment": "%f:celsius" % inc,
                   "melting_rate": "%f:second" % rate}
    return melt_params


def ref_kit_container(protocol, name, container, kit_id, discard=True,
                      store=None):
    '''
        Still in use to allow booking of agar plates on the fly
    '''
    kit_item = Container(None, protocol.container_type(container), name)
    if store:
        protocol.refs[name] = Ref(
            name, {"reserve": kit_id, "store": {"where": store}}, kit_item)
    else:
        protocol.refs[name] = Ref(
            name, {"reserve": kit_id, "discard": discard}, kit_item)
    return(kit_item)
