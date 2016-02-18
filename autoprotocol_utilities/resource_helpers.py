from autoprotocol.container import Container
from autoprotocol.protocol import Ref
from autoprotocol.unit import Unit
from collections import namedtuple
import sys


if sys.version_info[0] >= 3:
    string_type = str
else:
    string_type = basestring

# ## Returning containers or data


def scale_default(length, scale, label):
    """Detects if the oligo length matches the selected scale

    Parameters
    ----------
    length : int
        Length of the oligo in question
    scale : str
        Scale of the oligo in question
    label : str
        Name of the oligo

    Returns
    -------
    Response : namedtuple
        `success` (bool) and `error_message` (string) that is empty on success

    """

    r = namedtuple('Response', 'success error_message')
    ok = True
    error_message = None
    if scale == '25nm':
        ok = True if (length >= 15 and length <= 60) else False
    elif scale == '100nm':
        ok = True if (length >= 10 and length <= 90) else False
    elif scale == '250nm':
        ok = True if (length >= 5 and length <= 100) else False
    elif scale == '1um':
        ok = True if (length >= 5 and length <= 100) else False
    else:
        ok = False
    if not ok:
        error_message = """The specified oligo, '%s', is %s base pairs long.
                         This sequence length is invalid for the scale
                         of synthesis chosen (%s).""" % (label,
                                                         length,
                                                         scale)
    return r(success=ok, error_message=error_message)


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


class ResourceIDs(object):

    """
    A list of resource identification numbers used to provision
    resources using Autoprotocol.

    Example Usage:

    .. code-block:: python

        res = ResourceIDs()
        res.water
        res.te
        res.zymo_10b
        res.zymo_dh5a
        res.zymo_jm109
        res.ampicillin_100mg_ml
        res.chloramphenicol_34mg_ml
        res.kanamycin_50mg_ml
        res.mytaq_poly
        res.dpn_neb
        res.phusion_poly
        res.orange_g_100
        res.orange_g_500

    Returns
    -------
    resource_id: str

    """

    def __init__(self):
        self.water = "rs17gmh5wafm5p"
        self.te = "rs17pwyc754v9t"
        # competent cells
        self.zymo_10b = "rs16pbjc4r7vvz"
        self.zymo_dh5a = "rs16pbj944fnny"
        self.zymo_jm109 = "rs16pbjdhwkjxy"
        # antibiotics
        self.ampicillin_100mg_ml = "rs17msfk8ujkca"
        self.chloramphenicol_34mg_ml = "rs17p6t8ty2ny4"
        self.kanamycin_50mg_ml = "rs17msfpgpbqyv"
        # dna polymerases
        self.mytaq_poly = "rs16pcbhquhaz3"
        self.phusion_poly = "rs16pcc3mgay64"
        self.dpn_neb = "rs18kfcmf5xvxz"
        # orange g
        self.orange_g_100 = "rs17zw9zsaqd55"
        self.organge_g_500 = "rs17zwe6rux5b7"
