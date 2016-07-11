from autoprotocol.container import Container
from autoprotocol.protocol import Ref
from autoprotocol import Unit
from collections import namedtuple
import sys

if sys.version_info[0] >= 3:
    string_type = str
else:
    string_type = basestring


def oligo_scale_default(length, scale, label):
    """Detects if the oligo length matches the selected scale

    Every oligo provider has a length limit on the oligos based on the
    selected scale. The larger the scale, the longer or shorter the oligo
    can be.
    This function checks for IDT limits

    Parameters
    ----------
    length : int
        Length of the oligo in question.
    scale : str
        Scale of the oligo in question.
    label : str
        Name of the oligo.

    Returns
    -------
    namedtuple
        'success' (bool) and 'error_message' (string) that is empty upon
        success

    """

    r = namedtuple('Response', 'success error_message')
    ok = True
    error_message = None
    scale_ranges = {
        '10nm': [15, 60],
        '25nm': [15, 60],
        '100nm': [10, 90],
        '250nm': [5, 100],
        '1um': [5, 100]
    }

    if scale not in scale_ranges.keys():
        error_message = ("The specified oligo, '{0!s}', does not have a "
                         "recognized scale of {0!s}".format(
                             ', '.join(scale_ranges.keys)))
    else:
        ok = True if ((length >= scale_ranges[scale][0]) & (
            length <= scale_ranges[scale][1])) else False

    if not ok:
        error_message = ("The specified oligo, '{0!s}', is {1!s} base pairs "
                         "long. This sequence length is invalid for the scale"
                         " of synthesis chosen ({2!s}). The acceptable range "
                         "for this scale is {3!s} - {4!s} base pairs "
                         "long".format(label, length, scale,
                                       scale_ranges[scale][0],
                                       scale_ranges[scale][1]))

    return r(success=ok, error_message=error_message)


def oligo_dilution_table(conc=None, sc=None):
    """Return dilution table

    Determine the amount of diluent to add to an oligo based on
    concentration wanted and scale ordered. This function can return the
    entire dilution table or slices and values as needd

    Example Usage:

    .. code-block:: python

        oligo_dilution_table(conc="100uM")
        oligo_dilution_table(conc="100uM", scale="25nm")

    Returns:

    .. code-block:: python

        {"100uM": {"10nm":60, "25nm": 250, "100nm": 1000, "250nm": 2500,
                   "1um": 10000}}
        250

    Parameters
    ----------
    conc : str, optional
        The concentration you wish to select for. Currently 100uM or 1mM.
    sc : str, optional
        The scale you wish to select for. Currently '10nm', '25nm',
        '100nm', '250nm' or '1um'.

    Returns
    -------
    int
        If concentration and scale are given this returns the dilution volume
        only
    dict
        If only one of concentration or scale is provided this function
        returns a dict. If a concentration is selected it returns a dict where
        scales are the keys and dilution volumes the values.
        If a scale is selected it returns a dict with concentrations as keys
        and dicts of scale (key) and dilution volume (value).
        If nothing is selected the full dict of concentrations with dicts of
        scales and dilution volumes is returned.



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
            zip(scale, volumes[i * len(scale):i * len(scale) + len(scale)]))

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
    """Returns a dict of all available agar plates.

    Parameters
    ----------
    wells : integer
        Integer of the number of wells in the plate, 1 or 6.
        Default: 6 for 6-well plate

    Returns
    -------
    dict
        plates with plate identity as key and kit_id as value

    Raises
    ------
    ValueError
        If wells is not a integer equal to 1 or 6

    """
    if wells == 6:
        plates = {"lb_miller_50ug_ml_kan": "ki17rs7j799zc2",
                  "lb_miller_100ug_ml_amp": "ki17sbb845ssx9",
                  "lb_miller_100ug_ml_specto": "ki17sbb9r7jf98",
                  "lb_miller_100ug_ml_cm": "ki17urn3gg8tmj",
                  "lb_miller_noAB": "ki17reefwqq3sq"}
    elif wells == 1:
        plates = {"lb_miller_50ug_ml_kan": "ki17t8j7kkzc4g",
                  "lb_miller_100ug_ml_amp": "ki17t8jcebshtr",
                  "lb_miller_100ug_ml_specto": "ki17t8jaa96pw3",
                  "lb_miller_100ug_ml_cm": "ki17urn592xejq",
                  "lb_miller_noAB": "ki17t8jejbea4z"}
    else:
        raise ValueError("Wells has to be an integer, either 1 or 6")
    return (plates)


def return_dispense_media():
    """Returns a dict of media for reagent dispenser.

    Example Usage:

    .. code-block:: python

        from autoprotocol.protocol import Protocol
        from autoprotocol-utilities import return_dispense_media

        p = Protocol()
        media = return_dispense_media()["50_ug/ml_Kanamycin"]
        plate = p.ref("myplate", cont_type="96-flat", discard=True)
        p.dispense_full_plate(plate, media, "200:microliter")

    Autoprotocol Output:
    -------

    .. code-block:: python

        {
            "refs": {
                "myplate": {
                    "new": "96-flat",
                    "discard": True
                }
            },
            "instructions": [
                {
                    "reagent": "lb_miller_50ug_ml_kan",
                    "object": "myplate",
                    "columns": [
                        {
                            "column": 0,
                            "volume": "200:microliter"
                        },
                        {
                            "column": 1,
                            "volume": "200:microliter"
                        },
                        {
                            "column": 2,
                            "volume": "200:microliter"
                        },
                        {
                            "column": 3,
                            "volume": "200:microliter"
                        },
                        {
                            "column": 4,
                            "volume": "200:microliter"
                        },
                        {
                            "column": 5,
                            "volume": "200:microliter"
                        },
                        {
                            "column": 6,
                            "volume": "200:microliter"
                        },
                        {
                            "column": 7,
                            "volume": "200:microliter"
                        },
                        {
                            "column": 8,
                            "volume": "200:microliter"
                        },
                        {
                            "column": 9,
                            "volume": "200:microliter"
                        },
                        {
                            "column": 10,
                            "volume": "200:microliter"
                        },
                        {
                            "column": 11,
                            "volume": "200:microliter"
                        }
                    ],
                    "op": "dispense"
                }
            ]
        }

    Returns
    -------
    dict
        Media with common `display_name` as key and identifier for code
        as value


    """
    media = {"50_ug/ml_Kanamycin": "lb_miller_50ug_ml_kan",
             "100_ug/ml_Ampicillin": "lb_miller_100ug_ml_amp",
             "100_ug/mL_Spectinomycin": "lb_miller_100ug_ml_specto",
             "30_ug/ml_Kanamycin": "lb_miller_30ug_ml_kan",
             "15_ug/ml_Tetracycline": "lb_miller_15ug_ml_tet",
             "50_ug/ml_Kanamycin_25_ug/ml_Chloramphenicol":
             "lb_miller_50ug_ml_kan_25ug_ml_cm",
             "25_ug/ml_Chloramphenicol": "lb_miller_25ug_ml_cm",
             "LB_miller": "lb_miller_noAB",
             "TB_100_ug/ml_Ampicillin": "tb_100ug_ml_amp",
             "TB_50_ug/ml_Kanamycin": "tb_50ug_ml_kan"}
    return (media)


def ref_kit_container(protocol, name, container, kit_id, discard=True,
                      store=None):
    """Reserve agar plates for use within a protocol.

    In use only to allow booking of agar plates within a protocol.

    Example Usage:

    .. code-block:: python

        from autoprotocol import Protocol
        from autoprotocol_utilities import return_dispense_media, \
            return_agar_plates, ref_kit_container

        p = Protocol()
        bacteria = p.ref(name="test_bact", id=None,
                         cont_type="micro-1.5", discard=True).well(0)
        media = return_dispense_media()["50_ug/ml_Kanamycin"]
        agar_id = return_agar_plates(1)[media]
        agar_plate = ref_kit_container(p, "my_agar_plate",
                                       "6-flat", agar_id, discard=False,
                                       store="cold_4")

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
        If the plate is not discarded, indicate valid storage condition.

    Returns
    -------
    Container


    """
    kit_item = Container(None, protocol.container_type(
        container), name, storage=store if store else None)
    if store:
        protocol.refs[name] = Ref(
            name, {"reserve": kit_id, "store": {"where": store}}, kit_item)
    else:
        protocol.refs[name] = Ref(
            name, {"reserve": kit_id, "discard": discard}, kit_item)
    return kit_item


class ResourceIDs(object):

    """Common resource ids

    A list of resource identification numbers used to provision
    resources using Autoprotocol.

    Example
    -------

    .. code-block:: python

        from autoprotocol-utilities import ResourceIDs

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
    str
        resource id of the reagent

    """

    def __init__(self):
        # diluent
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
        # media
        self.lb_miller_50ug_ml_kan = "rs18s8x88zz9ee"
        self.lb_miller_100ug_ml_amp = "rs18s8x4qbsvjz"
        self.lb_miller_noAB = "rs17bafcbmyrmh"
        self.tb_50ug_ml_kan = "rs18xqzy4ftdy3"
        self.tb_100ug_ml_amp = "rs18xr22jq7vtz"
        self.tb_100ug_ml_spec = "rs18xr25bpakgs"
        self.tb_25ug_ml_cm = "rs18xr28t3z8nx"
        # kunkel resources
        self.t7_poly = "rs16pca2urcz74"
        self.t4_pnk = "rs16pc9rd5hsf6"
        self.t4_pnk_buffer = "rs16pc9rd5sg5d"
        self.atp_100mM = "rs16pccshb6cb4"
        # SYBR green qPCR enzyme
        self.sensifast = "rs17knkh7526ha"
        self.itaq = "rs18fabf4h5se8"
        # mytaq dna polymerase resources
        self.mytaq_poly = "rs16pcbhquhaz3"
        self.mytaq_red_poly = "rs16r3h6umutcg"
        self.mytaq_hs_red_mix = "rs17kj4vnh5xm3"
        self.mytaq_red_mix = "rs17kj4j9vgh4x"
        self.mytaq_buffer = "rs16pcbhqurzpa"
        # phusion dna polymerase resources
        self.phusion_poly = "rs16pcc3mgay64"
        self.phusion_mgcl_50 = "rs16pcc3mgzy4r"
        self.phusion_gc_buffer = "rs16pcc3mgs9eh"
        self.phusion_hf_buffer = "rs16pcc3mgjnub"
        # kapa dna polymerase master mixes
        self.kapa_hifi_hs_mix = "rs18esg5hz25cm"
        self.kapa_2g_hs_mix = "rs18esfy3xqvut"
        # velocity dna polymerase resources
        self.velocity_poly = "rs16pcckjgaxdt"
        self.velocity_hifi_buffer = "rs16pcckjghhyz"
        self.velocity_mgcl = "rs16pcckjgs8p8"
        self.velocity_dmso = "rs16pcckjgyu9e"
        # la taq dna polymerase resources
        self.lataq_poly = "rs16pcbdc5dfw6"
        self.lataq_poly_gc1 = "rs16pcb53zwxjz"
        self.la_buffer_2_10x = "rs16pcbdc5n6kd"
        self.lataq_poly_gc = "rs16pcb53zp8vs"
        self.lataq_poly_gc2 = "rs16pcb5425j67"
        self.lataq_dntp25 = "rs16pcbdc5us6k"
        # pcr components
        self.dntps_25 = "rs16pcb542c5rd"
        self.dntps_10 = "rs186wj7fvknsr"
        self.mgcl = "rs16pca93rjwgq"
        self.dmso = "rs186hr8m38ntw"
        # restriction enzymes
        #  buffers
        self.cutsmart_buffer = "rs17ta93g3y85t"
        self.neb21_buffer = "rs17sh6krrzjqu"
        self.neb31_buffer = "rs18jwyqebdsdu"
        self.fastdigest_buffer = "rs18a8uvv7us8t"
        #  enzymes
        self.ncoi_hf = "rs183kfrjt4svz"
        self.psti_hf = "rs17usrub943jf"
        self.ecori_hf = "rs17ta8xftpdk6"
        self.bamhi_hf = "rs17ta8tz5ffby"
        self.bbsi = "rs17rrdaz88sz5"
        self.bsmbi = "rs17px7f9yg3kn"
        self.pvuii_hf = "rs17ta9v88fgpd"
        self.bsai = "rs17px78jjr2fq"
        self.ndei = "rs186h3y9nuqzb"
        self.xhoi = "rs186h4bcgjtyu"
        self.dpni_neb = "rs18kfcmf5xvxz"
        self.mfei_hf = "rs18nw6ta6d5bn"
        self.esp3i = "rs18a8ttpm8hxk"
        self.hindiii_hf = "rs18nw6kpnp44v"
        self.sali = "rs18trptum9gc4"
        self.smai = "rs18vvr4tgrghh"
        self.xbai = "rs18x6ja5k75ev"
        self.hincii = "rs18x6jrxfxtut"
        self.bbvCi = "rs18x6k25qmr6k"
        # orange g
        self.orange_g_100 = "rs17zw9zsaqd55"
        self.organge_g_500 = "rs17zwe6rux5b7"
        # control plasmids
        self.control_amp = "rs18rx59spw2t8"
        self.control_kan = "rs18rx6a44qss7"
        # ligases
        self.thermo_t4ligase_buffer = "rs16pc8u4dmsbg"
        self.thermo_t4ligase = "rs16pc8u4dd3n9"
        self.neb_t4ligase_buffer = "rs17sh5rzz79ct"
        self.neb_t4ligase = "rs16pc8krr6ag7"
        self.ligase_control = "rs18sfjf96tkwe"
        # other
        self.exosap = "rs18dnrskds4t6"
        # assembly reagents
        self.nebuilder2x = "rs18pc86ykcep6"
        self.nebuilderpc = "rs192pqa2jua9v"
        self.gibson2x = "rs16pfatkggmk5"
        self.gibsonpc = "rs1959tbv27xu2"
        self.infusion5x = "rs16pfv7qw5ytj"
        self.infusionpuc = "rs192pqw2nuef8"
        self.infusioninsert = "rs192pqxnx9gm2"
        # QuantIt
        self.quantItLambda = "rs18qstca8ksrt"
        self.quantItTE = "rs18qst9znacdy"
        self.quantItPico = "rs18qst83met3g"
        # MagJet
        self.lysozyme = "rs18u5sv3y8haj"
        self.dtt = "rs18umvdgu69su"
        self.MagJETRNALysisBuffer = "rs18umvv99scva"
        self.MagJETRNABeads = "rs18umvxjtubpw"
        self.MagJETRNAReactionBuffer = "rs18umwewhmmvr"
        self.MagJETRNADNase = "rs18umwj7mmmdc"
        # genotyping lysis buffers
        self.geno_lysis = "rs17krffpwfyrq"
        self.geno_neut = "rs17krfgz55nqq"

    def bacteria(self, bact=None):
        """Return competent bacteria id

        Parameters
        ----------
        bact: string
            Bacteria name, one of: 'Zymo 10B', 'Zymo DH5a', 'Zymo JM109'

        Returns
        -------
        string
            resource id for the bacteria requested, `None` if bact could not
            be found
        """
        bacteria = {"Zymo 10B": self.zymo_10b,
                    "Zymo DH5a": self.zymo_dh5a,
                    "Zymo JM109": self.zymo_jm109}
        return bacteria.get(bact)

    def diluents(self, dil=None):
        """Return diluent id

        Parameters
        ----------
        dil: string
            Diluent name, one of: 'water', 'TE'

        Returns
        -------
        string
            resource id for the diluent requested, `None` if dil could not
            be found
        """
        diluents = {"water": self.water,
                    "TE": self.te}
        return diluents.get(dil)

    def exoassembly_kits(self, kit=None):
        kit_dict = {"NEBuilder": {"name": "NEBuilder",
                                  "dil_fact": 2,
                                  "resource": self.nebuilder2x,
                                  "pc": {self.nebuilderpc: 2}},
                    "Gibson": {"name": "Gibson",
                               "dil_fact": 2,
                               "resource": self.gibson2x,
                               "pc": {self.gibsonpc: 2}},
                    "InFusion": {"name": "InFusion",
                                 "dil_fact": 5,
                                 "resource": self.infusion5x,
                                 "pc": {self.infusionpuc: Unit(1, "uL"),
                                        self.infusioninsert: Unit(2, "uL")}}}
        return kit_dict.get(kit)

    def transformation_controls(self, media=None):
        """Return transformation controls

        Parameters
        ----------
        media: string
            Media for which to select the control. One of:
            'lb_miller_50ug_ml_kan', 'lb_miller_100ug_ml_amp'

        Returns
        -------
        string
            resource id for the positive control requested, `None` if media
            could not be found
        """
        controls = {"lb_miller_50ug_ml_kan": self.control_kan,
                    "lb_miller_100ug_ml_amp": self.control_amp}
        return controls.get(media)

    def growth_media(self, media=None):
        """Return growth media resource id

        Parameters
        ----------
        media: string
            Media for which to select the media.

        Returns
        -------
        string
            resource id for the media requested, `None` if media
            could not be found
        """
        media_dict = {
            "lb_miller_50ug_ml_kan": self.lb_miller_50ug_ml_kan,
            "lb_miller_100ug_ml_amp": self.lb_miller_100ug_ml_amp,
            "lb_miller_noAB": self.lb_miller_noAB,
            "tb_50ug_ml_kan": self.tb_50ug_ml_kan,
            "tb_100ug_ml_amp": self.tb_100ug_ml_amp,
            "tb_100ug_ml_specto": self.tb_100ug_ml_spec,
            "tb_25ug_ml_cm": self.tb_25ug_ml_cm,
        }
        return media_dict.get(media)

    def t4_ligase(self, ligase_type=None):
        """Return T4 ligase reagents

        Parameters
        ----------
        media: string
            Vendor to use. 'neb' or 'thermo'.

        Returns
        -------
        dict
            'buffer' - resource id for the buffer
            'ligase' - resource id for the ligase

        """
        ligases = {"neb": {"buffer": self.neb_t4ligase_buffer,
                           "ligase": self.neb_t4ligase},
                   "thermo": {"buffer": self.thermo_t4ligase_buffer,
                              "ligase": self.thermo_t4ligase}}
        return ligases.get(ligase_type)

    def restriction_enzyme_buffers(self, enzyme):
        """Returns a tuple of enzyme_id and buffer_id for a given enzyme

        Restriction enzymes need to be digested with a certain buffer.
        This function returns the correct resource id for the enzyme as well
        as for the matching buffer.

        Parameters
        ----------
        enzyme: string
            name of enzyme, all lower caps such as `dpni_neb` or `ncoi_hf`

        Returns
        -------
        namedtuple
            enzyme_id, buffer_id, errors
        """
        em = []
        resset = namedtuple('RestrictionSet', 'enzyme_id buffer_id errors')

        enzymes = {"ncoi_hf": self.ncoi_hf,
                   "psti_hf": self.psti_hf,
                   "ecori_hf": self.ecori_hf,
                   "bamhi_hf": self.bamhi_hf,
                   "bbsi": self.bbsi,
                   "bsmbi": self.bsmbi,
                   "pvuii_hf": self.pvuii_hf,
                   "bsai": self.bsai,
                   "ndei": self.ndei,
                   "xhoi": self.xhoi,
                   "dpni_neb": self.dpni_neb,
                   "mfei_hf": self.mfei_hf,
                   "esp3i": self.esp3i,
                   "hindiii_hf": self.hindiii_hf,
                   "sali": self.sali,
                   "smai": self.smai,
                   "bbvCi": self.bbvCi,
                   "xbai": self.xbai,
                   "hincii": self.hincii}

        buffer_map = {}
        buffer_map["cutsmart"] = {
            "buffer_id": self.cutsmart_buffer, "enzymes": [
                "pvuii_hf", "ecori_hf", "hindiii_hf",
                "bamhi_hf", "psti_hf", "ncoi_hf", "xbai",
                "bsai", "ndei", "xhoi", "smai", "bbvCi",
                "dpni_neb", "mfei_hf"]}
        buffer_map["neb_21"] = {
            "buffer_id": self.neb21_buffer, "enzymes": ["bbsi"]}
        buffer_map["new_31"] = {
            "buffer_id": self.neb31_buffer, "enzymes": [
                "bsmbi", "sali", "hincii"]}
        buffer_map["fast_digest"] = {
            "buffer_id": self.fastdigest_buffer, "enzymes": ["esp3i"]}

        enzyme_id = enzymes.get(enzyme, None)
        if not enzyme_id:
            em.append("The enzyme (%s) cannot be found." % enzyme)
        buffer_id = None
        for resbuffer in buffer_map.values():
            if enzyme in resbuffer["enzymes"]:
                buffer_id = resbuffer["buffer_id"]
        if not buffer_id:
            em.append("The enzyme specified (%s) doesn't have a corresponding"
                      " buffer." % enzyme)

        em = [_f for _f in em if _f]
        if len(em) == 0:
            em = None

        return resset(enzyme_id=enzyme_id, buffer_id=buffer_id, errors=em)
