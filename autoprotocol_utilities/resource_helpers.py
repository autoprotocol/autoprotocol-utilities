from autoprotocol.container import Container
from autoprotocol.protocol import Ref
from collections import namedtuple
import sys


if sys.version_info[0] >= 3:
    string_type = str
else:
    string_type = basestring

# ## Returning containers or data


def oligo_scale_default(length, scale, label):
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


def oligo_dilution_table(conc=None, sc=None):
    """Return dilution table

    Determine the amount of diluent to add to an oligo based on
    concentration wanted and scale ordered. This function can return the
    entire dilution table or slices and values as needd

    Parameters
    ----------
    conc : str, optional
        The concentration you wish to select for. Currently 100uM or 1mM.
    sc : str, optional
        The scale you wish to select for. Currently '10nm', '25nm',
        '100nm', '250nm' or '1um'.

    Returns
    -------
    dilution_table : dict
        This is a dict of dicts to determine the volume to add for each
        concentration (level 1) and scale (level 2).

    Raises
    ------
    ValueError
        If conc is not a valid concentration: '100uM', '1mM'
    ValueError
        If sc is is not a valid scale: '10nm', '25nm', '100nm', '250nm', '1um'

    """
    concentration = '100uM', '1mM'
    scale = '10nm', '25nm', '100nm', '250nm', '1um'
    volumes = [60, 250, 1000, 2500, 10000, 6, 25, 100, 250, 1000]

    if conc:
        assert conc in concentration, ("conc has to be in %s " % concentration)
    if sc:
        assert sc in scale, ("sc has to be in %s " % scale)

    dilution_table = {}
    for i, y in enumerate(concentration):
        dilution_table[y] = dict(
            zip(scale, volumes[i*len(scale):i*len(scale)+len(scale)]))

    if conc and sc:
        return dilution_table[conc][sc]
    elif conc:
        return dilution_table[conc]
    elif sc:
        for x in scale:
            if sc != x:
                for c in dilution_table:
                    dilution_table[c].pop(x, None)
        return dilution_table
    else:
        return dilution_table


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

    Raises
    ------
    ValueError
        If wells is not a integer equaling to 1 or 6

    """
    if wells == 6:
        plates = {"lb-broth-50ug-ml-kan": "ki17rs7j799zc2",
                  "lb-broth-100ug-ml-amp": "ki17sbb845ssx9",
                  "lb-broth-100ug-ml-specto": "ki17sbb9r7jf98",
                  "lb-broth-100ug-ml-cm": "ki17urn3gg8tmj",
                  "lb-broth-noAB": "ki17reefwqq3sq"}
    elif wells == 1:
        plates = {"lb-broth-50ug-ml-kan": "ki17t8j7kkzc4g",
                  "lb-broth-100ug-ml-amp": "ki17t8jcebshtr",
                  "lb-broth-100ug-ml-specto": "ki17t8jaa96pw3",
                  "lb-broth-100ug-ml-cm": "ki17urn592xejq",
                  "lb-broth-noAB": "ki17t8jejbea4z"}
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

    def bacteria(self, bact=None):
        bacteria = {"Zymo 10B": self.zymo_10b,
                    "Zymo DH5a": self.zymo_dh5a,
                    "Zymo JM109": self.zymo_jm109}
        return bacteria.get(bact)
