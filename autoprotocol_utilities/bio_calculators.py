from autoprotocol.unit import Unit


def dna_mass_to_mole(length, mass, ds=True):
    """
    For the DNA Length and mass given, return the mole amount of DNA

    Example Usage:

    .. code-block:: python

        from autoprotocol_utilities import dna_mass_to_mole
        from autoprotocol.unit import Unit

        dna_length = 100
        dna_mass = Unit(33, 'ng')
        dna_mass_to_mole(dna_length, dna_mass)

    Returns:

    .. code-block:: python

        Unit(0.5, 'picomole')

    Parameters
    ----------
    length: int
        Length of DNA in bp
    mass: str, Unit
        Weight of DNA in prefix-g
    ds: bool, optional
        True for dsDNA, False for ssDNA

    Returns
    -------
    pmole_dna: Unit
        Mole amount of DNA in pmol

    Raises
    ------
    ValueError
        If inputs are not of specified types

    """
    if isinstance(mass, str):
        mass = Unit.fromstring(mass)

    if not isinstance(mass, Unit) or str(mass.dimensionality) != "[mass]":
        raise ValueError("Mass of DNA must be of type Unit in prefix-gram")

    if not isinstance(length, int):
        raise ValueError(
            "Length of DNA is of type %s, must be of type "
            "integer" % type(length))

    if not isinstance(ds, bool):
        raise ValueError(
            "ds is of type %s, must be of type bool: True for dsDNA, "
            "False for ssDNA" % type(ds))

    dna_pg = mass.to("pg")

    if ds:
        dna_pmol = dna_pg / (Unit(660, "pg/pmol") * length)
    else:
        dna_pmol = dna_pg / (Unit(330, "pg/pmol") * length)

    return dna_pmol


def dna_mole_to_mass(length, mole, ds=True):
    """
    For the DNA Length and mole amount given, return the mass of DNA

    Example Usage:

    .. code-block:: python

        from autoprotocol_utilities import dna_mole_to_mass
        from autoprotocol.unit import Unit

        dna_length = 5000
        dna_mole = "10:pmol"
        dna_mole_to_mass(dna_length, dna_mole)

    Returns:

    .. code-block:: python

        Unit(33.0, 'microgram')

    Parameters
    ----------
    length: int
        Length of DNA in bp
    mole: str, Unit
        Mole amount of DNA in prefix-mol
    ds: bool, optional
        True for dsDNA, False for ssDNA

    Returns
    -------
    dna_ug: Unit
        Weight of DNA in ug

    Raises
    ------
    ValueError
        If inputs are not of specified types

    """
    if isinstance(mole, str):
        mole = Unit.fromstring(mole)

    if not isinstance(mole, Unit) or str(mole.dimensionality) != "[substance]":
        raise ValueError(
            "Mole amount of DNA must be of type Unit in prefix-mol")

    if not isinstance(length, int):
        raise ValueError(
            "Length of DNA is of type %s, must be of type "
            "integer" % type(length))

    if not isinstance(ds, bool):
        raise ValueError(
            "ds is of type %s, must be of type bool: True for dsDNA, "
            "False for ssDNA" % type(ds))

    dna_pmol = mole.to("pmol")

    if ds:
        dna_ug = (
            Unit(660, "pg/pmol") * dna_pmol * Unit(10**(-6), "ug/pg") * length)
    else:
        dna_ug = (
            Unit(330, "pg/pmol") * dna_pmol * Unit(10**(-6), "ug/pg") * length)

    return dna_ug


def molar_to_mass_conc(length, molar, ds=True):
    """
    For the DNA molarity given, return the mass concentration of DNA

    Example Usage:

    .. code-block:: python

        from autoprotocol_utilities import molar_to_mass_conc
        from autoprotocol_utilities import dna_mole_to_mass
        from autoprotocol.unit import Unit

        dna_length = 5000
        dna_molarity = Unit(10, 'uM')
        molar_to_mass_conc(dna_length, dna_molarity)

    Returns:

    .. code-block:: python

        Unit(33000.0, 'nanogram / microliter')

    Parameters
    ----------
    length: int
        Length of DNA in bp
    molar: str, Unit
        Molarity of DNA in prefix-M
    ds: bool, optional
        True for dsDNA, False for ssDNA

    Returns
    -------
    mass_conc: Unit
        Mass concentration of DNA in ng/uL

    Raises
    ------
    ValueError
        If inputs are not of specified types

    """
    if not isinstance(length, int):
        raise ValueError(
            "Length of DNA is of type %s, must be of type "
            "integer" % type(length))

    if isinstance(molar, str):
        molar = Unit.fromstring(molar)

    if not (isinstance(molar, Unit) and
            str(molar.dimensionality) == '[substance] / [length] ** 3'):
        raise ValueError(
            "Molar concentration of DNA must be of type string or Unit")

    if not isinstance(ds, bool):
        raise ValueError(
            "ds is of type %s, must be of type bool: True for dsDNA, "
            "False for ssDNA" % type(ds))

    dna_umole = Unit((molar / Unit(1, "M")).magnitude, "umol")
    dna_ug = dna_mole_to_mass(length, dna_umole, ds)
    mass_conc = Unit(dna_ug.magnitude * 1000, "ng/uL")

    return mass_conc


def mass_conc_to_molar(length, mass_conc, ds=True):
    """
    For the DNA mass concentration given, return the molarity of DNA

    Example Usage:

    .. code-block:: python

        from autoprotocol_utilities import mass_conc_to_molar
        from autoprotocol_utilities import dna_mass_to_mole
        from autoprotocol.unit import Unit

        dna_length = 5000
        dna_mass_conc = Unit(33, 'ng/uL')
        mass_conc_to_molar(dna_length, dna_mass_conc)

    Returns:

    .. code-block:: python

        Unit(0.01, 'micromolar')

    Parameters
    ----------
    length: int
        Length of DNA in bp
    mass_conc: str, Unit
        Mass concentration of DNA
    ds: bool, optional
        True for dsDNA, False for ssDNA

    Returns
    -------
    molar: Unit
        Molarity of DNA in uM

    Raises
    ------
    ValueError
        If inputs are not of specified types

    """
    if not isinstance(length, int):
        raise ValueError(
            "Length of DNA is of type %s, must be of type "
            "integer" % type(length))

    if isinstance(mass_conc, str):
        mass_conc = Unit.fromstring(mass_conc)

    if not isinstance(mass_conc, Unit) or \
            str(mass_conc.dimensionality) != '[mass] / [length] ** 3':
        raise ValueError("Mass concentration of DNA must be of type Unit")

    if not isinstance(ds, bool):
        raise ValueError(
            "ds is of type %s, must be of type bool: True for dsDNA, "
            "False for ssDNA" % type(ds))

    dna_ng = Unit((mass_conc / Unit(1, "ng/uL")).magnitude, "ng")
    dna_pmol = dna_mass_to_mole(length, dna_ng, ds)
    dna_molar = Unit(round(dna_pmol.magnitude, 9), "uM")

    return dna_molar


def ligation_insert_ng(plasmid_size,  plasmid_mass,
                       insert_size, molar_ratio=1):
    """
    For the plasmid size, plasmid amount, insert size, and molar ratio given,
    return the mass of insert needed for ligation

    Different from ligation_insert_volume: no insert concentration is
    given -> returns mass of insert needed

    Example Usage:

    .. code-block:: python

        from autoprotocol_utilities import ligation_insert_ng
        from autoprotocol.unit import Unit

        plasmid_size = 3000
        plasmid_mass = Unit(100, 'ng')
        insert_size = 48
        ligation_insert_ng(plasmid_size, plasmid_mass, insert_size)

    Returns:

    .. code-block:: python

        Unit(1.6, 'nanogram')

    Parameters
    ----------
    plasmid_size : int
        Length of plasmid in bp.
    insert_size: int
        Length of insert in bp
    plasmid_mass : str, Unit
        Mass of plasmid in prefix-g
    molar_ratio : int, float, string, optional
        Ligation molar ratio of insert : vector.  By default it is 1 : 1.
        Generally ligations are tested at 1:3, 1:1, and 3:1

    Returns
    -------
    insert_amount: Unit
        Amount of insert solution needed in ng

    Raises
    ------
    ValueError
        If wells are not of type list, WellGroup or Container

    """

    # Check input types
    if not isinstance(plasmid_size, int):
        raise ValueError("Plasmid_size: must be an integer")

    if not isinstance(insert_size, int):
        raise ValueError("insert_size: must be an integer")

    if type(molar_ratio) == str:
        molar_ratio = float(
            molar_ratio.split(":")[0]) / float(molar_ratio.split(":")[1])

    if type(molar_ratio) not in (int, float):
        raise ValueError(
            "molar_ratio: must be an int, float, or string in the form "
            "of int:int")

    if isinstance(plasmid_mass, str):
        plasmid_mass = Unit.fromstring(plasmid_mass)

    if not (isinstance(plasmid_mass, Unit) and
            str(plasmid_mass.dimensionality) == "[mass]"):
        raise ValueError(
            "Plasmid amount must be of type str or Unit in prefix-g")

    length_ratio = float(insert_size) / float(plasmid_size)
    plasmid_ng = plasmid_mass.to("ng")
    insert_ng = plasmid_ng * length_ratio * molar_ratio

    return insert_ng


def ligation_insert_volume(plasmid_size,  plasmid_mass, insert_size,
                           insert_conc, ds=True, molar_ratio=1):
    """
    For the plasmid size, plasmid amount, insert size, insert concentration,
    and molar ratio given, return the volume of insert solution needed for
    ligation

    Different from ligation_insert_ng: insert concentration is given -> returns
    volume of insert solution needed

    Example Usage:

    .. code-block:: python

        from autoprotocol_utilities import ligation_insert_volume
        from autoprotocol_utilities import molar_to_mass_conc
        from autoprotocol.unit import Unit

        plasmid_size = 3000
        plasmid_mass = Unit(100, 'ng')
        insert_size = 48
        insert_conc = Unit(25, 'ng/uL')
        ligation_insert_volume(plasmid_size, plasmid_mass, insert_size,
                               insert_conc)

    Returns:

    .. code-block:: python

        Unit(0.064, 'microliter')

    Parameters
    ----------
    plasmid_size : int
        Length of plasmid in bp.
    plasmid_mass : str, Unit
        Mass of plasmid in prefix-g
    insert_size: int
        Length of insert in bp
    insert_conc: str, Unit
        Molar or mass concentration of insert
    ds: bool, optional
        True for dsDNA, False for ssDNA
    molar_ratio : int, float, string, optional
        Ligation molar ratio of insert : vector.
        Common ratios are 1:3, 1:1, and 3:1. 1:1 by default

    Returns
    -------
    insert_amount: Unit
        Volume of insert solution needed in uL

    Raises
    ------
    ValueError
        If wells are not of type list, WellGroup or Container

    """

    conc_dimension = ["[substance] / [length] ** 3", '[mass] / [length] ** 3']

    # Check input types
    if not isinstance(plasmid_size, int):
        raise ValueError("Plasmid_size: must be an integer")

    if isinstance(plasmid_mass, str):
        plasmid_mass = Unit.fromstring(plasmid_mass)

    if not isinstance(plasmid_mass, Unit) and \
            str(plasmid_mass.dimensionality) == "[mass]":
        raise ValueError(
            "Plasmid mass must be of type str or Unit in prefix-g")

    if not isinstance(insert_size, int):
        raise ValueError("insert_size: must be an integer")

    if isinstance(insert_conc, str):
        insert_conc = Unit.fromstring(insert_conc)

    if not (isinstance(insert_conc, Unit) and
            str(insert_conc.dimensionality) in conc_dimension):
        raise ValueError(
            "Plasmid concentration must be of type Unit in prefix-M or "
            "prefix-g / prefix-L ")

    if not isinstance(ds, bool):
        raise ValueError(
            "ds is of type %s, must be of type bool: True for dsDNA, "
            "False for ssDNA" % type(ds))

    if type(molar_ratio) == str:
        molar_ratio = float(
            molar_ratio.split(":")[0]) / float(molar_ratio.split(":")[1])

    if type(molar_ratio) not in (int, float):
        raise ValueError(
            "molar_ratio: must be an int, float, or string in the "
            "form of int:int")

    len_ratio = float(insert_size) / float(plasmid_size)
    plasmid_ng = plasmid_mass.to("ng")
    insert_ng = plasmid_ng * len_ratio * molar_ratio

    # Convert concentration to ng/uL
    if str(insert_conc.dimensionality) == conc_dimension[0]:
        insert_conc = molar_to_mass_conc(insert_size, insert_conc, ds)

    else:
        insert_conc = insert_conc.to("ng/uL")

    insert_vol = insert_ng / insert_conc

    return insert_vol


def ligation_insert_amount(plasmid_size, plasmid_conc, plasmid_volume,
                           insert_size, insert_conc, ds=True, molar_ratio=1):
    """
    For the plasmid size, plasmid concentration, insert size, insert
    concentration, and molar ratio given,
    return the volume of insert solution needed for ligation

    Different form ligation_insert_volume: plasmid concentration and volume
    are given instead of plasmid mass

    Example Usage:

    .. code-block:: python

        from autoprotocol_utilities import ligation_insert_amount
        from autoprotocol_utilities import molar_to_mass_conc
        from autoprotocol.unit import Unit

        plasmid_size = 2000
        plasmid_conc = '1.5:uM'
        plasmid_volume = Unit(10, 'uL')
        insert_size = 25
        insert_conc = Unit(10, 'ng/uL')
        ligation_insert_amount(plasmid_size, plasmid_conc, plasmid_volume,
                               insert_size, insert_conc)
    Returns:

    .. code-block:: python

        Unit(24.75, 'microliter')

    Parameters
    ----------
    plasmid_size : int
        Length of plasmid in bp.
    plasmid_conc : str, Unit
        Molar or mass concentration of plasmid solution
    plasmid_volume: str, Unit
        Volume of plasmid solution in prefix-L
    insert_size: int
        Length of insert in bp
    insert_conc : str, Unit
        Molar or mass concentration of insert solution
    ds: bool, optional
        True for dsDNA, False for ssDNA
    molar_ratio : int, float, string, optional
        Ligation molar ratio of insert : vector.
        Common ratios are 1:3, 1:1, and 3:1. 1:1 by default

    Returns
    -------
    insert_amount: Unit
        Volume of insert solution in uL

    Raises
    ------
    ValueError
        If wells are not of type list, WellGroup or Container

    """
    # Check input types
    if not isinstance(plasmid_size, int):
        raise ValueError("Plasmid_size: must be an integer")

    if not isinstance(insert_size, int):
        raise ValueError("insert_size: must be an integer")

    if isinstance(plasmid_volume, str):
        plasmid_volume = Unit.fromstring(plasmid_volume)
    if not isinstance(plasmid_volume, Unit) or \
            str(plasmid_volume.dimensionality) != "[length] ** 3":
        raise ValueError(
            "Volume of plasmid solution must be of type str or Unit")

    conc_dimension = ["[substance] / [length] ** 3", '[mass] / [length] ** 3']
    conc = [plasmid_conc, insert_conc]
    size = [plasmid_size, insert_size]
    for i in range(0, 2):
        if isinstance(conc[i], str):
            conc[i] = Unit.fromstring(conc[i])
        if (isinstance(conc[i], Unit) and
                str(conc[i].dimensionality) in conc_dimension):
            # Convert all concentrations to ng/uL
            if str(conc[i].dimensionality) == conc_dimension[0]:
                conc[i] = molar_to_mass_conc(size[i], conc[i], ds)
            else:
                conc[i] = conc[i].to("ng/uL")
        else:
            raise ValueError(
                "Concentration must be of type string or Unit ")

    if not isinstance(ds, bool):
        raise ValueError(
            "ds is of type %s, must be of type bool: True for dsDNA, "
            "False for ssDNA" % type(ds))

    if type(molar_ratio) == str:
        molar_ratio = float(
            molar_ratio.split(":")[0]) / float(molar_ratio.split(":")[1])

    if type(molar_ratio) not in (int, float):
        raise ValueError(
            "molar_ratio: must be an int, float, or string in the "
            "form of int:int")

    plasmid_conc = conc[0]
    insert_conc = conc[1]
    # Convert input volume to uL
    plasmid_uL = Unit((plasmid_volume / Unit(1, "uL")).magnitude, "uL")
    len_ratio = float(insert_size) / float(plasmid_size)
    plasmid_ng = plasmid_conc * plasmid_uL
    insert_ng = plasmid_ng * len_ratio * molar_ratio
    insert_amount = insert_ng / insert_conc

    return insert_amount
