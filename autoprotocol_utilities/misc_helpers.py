from autoprotocol import UserError
from collections import namedtuple
from autoprotocol.container import Well, WellGroup
import datetime
import sys

if sys.version_info[0] >= 3:
    string_type = str
else:
    string_type = basestring


def user_errors_group(error_msgs, info=None):
    """Takes a list error messages and neatly displays as a single UserError

    Will automatically remove instances of None and only report errors if list
    is not empty.

    Parameters
    ----------
    error_msgs : list
        List of strings that are the error messages

    Raises
    ------
    ValueError
        If error_msgs is not of type list

    """
    assert isinstance(error_msgs, list), ("Error messages must be in the form"
                                          " of a list to properly format the "
                                          "grouped message.")

    error_msgs = [_f for _f in error_msgs if _f]
    if len(error_msgs) != 0:
        raise UserError(
            "%s error(s) found in this protocol: " % len(error_msgs) +
            " ".join(["<Error " +
                      str(i + 1) + "> " +
                      str(m) for i, m in enumerate(error_msgs)]), info=info)


def printdatetime():
    """
    Generate a datetime string.

    Returns
    -------
    str
        The current date and time formatted as: YYYY-MM-DD_HH-MM-SS

    """
    printdate = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    return printdate


def printdate():
    """
    Generate a date string.

    Returns
    -------
    str
        The current date formatted as: YYYY-MM-DD

    """
    printdate = datetime.datetime.now().strftime('%Y-%m-%d')
    return printdate


def make_list(my_str, integer=False):
    """
    Return a list of strings (or ints) from a string containing
    comma separated elements.

    Parameters
    ----------
    my_str : str
        String with individual elements separated by comma.
    interger : bool
        If true list of integers instead of list of strings
        is returned. Default: False.

    Returns
    -------
    list
        List of strings or integers

    Raises
    ------
    ValueError
        If my_str is not of type string

    """
    assert isinstance(my_str, string_type), (
        "Input needs to be of type string")
    if integer:
        my_str = [int(x.strip()) for x in my_str.split(",")]
    else:
        my_str = [x.strip() for x in my_str.split(",")]
    return my_str


def flatten_list(l):
    """
    Flatten a list recursively without for loops or additional modules

    Example Usage:

    .. code-block:: python

            from autoprotocol_utilities.misc_helpers import flatten_list

            l = [-1, 0, [1,2], "string", [3, [4, 5]]]
            flatten_list(l)

    Returns:

    .. code-block:: python

            [-1, 0, 1, 2, 'string', 3, 4, 5]

    Parameters
    ---------
    l : list, list of WellGroup
        List or list of WellGroups to flatten


    Returns
    -------
    list
        Flat list

    Raises
    ------
    ValueError
        If l is not of type list

    """
    if isinstance(l, (list, WellGroup)):
        return [x for sublist in l for x in flatten_list(sublist)]
    else:
        return [l]


def det_new_group(i, base=0):
    """Determine if new_group should be added to pipetting operation.

    Helper to determine if new_group should be added. Returns true when
    'i' matches the base, which defaults to 0.

    Parameters
    ----------
    i : int
        The iteration you are on.
    base : int, optional
        The value at which you want to trigger a new group. Default: 0.

    Returns
    -------
    bool
        True if iteration equals base case.

    Raises
    ------
    ValueError
        If i is not of type integer
    ValueError
        If base is not of type integer

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

    Can either throw an error message if `length` is exceeded or correct the
    string and return the corrected string.

    Parameters
    ----------
    label : str
        String to test.
    length : int, optional
        Maximum label length for this string. Default: 22.
    trunc : bool, optional
        Truncate the label if it is too long. Default: False.
    clip : bool, optional
        Clip the label (remove from beginning of the string) if it is too long
        Default: False. If both trunc and clip are True, trunc will take effect
        and not clip.

    Returns
    -------
    namedtuple
        `label` (str) and `error_message` (string) that is empty on success
        `label` is the unmodified, truncated to clipped label as indicated

    Raises
    ------
    ValueError
        If label is not of type string

    """
    assert isinstance(label, string_type), "Label has to be of type string"

    r = namedtuple('Response', 'label error_message')
    if trunc and len(label) > length:
        label = label[0: length]
    if clip and len(label) > length:
        label = label[len(label) - length: len(label)]

    error_message = None
    if len(label) > length:
        error_message = ("The specified label, '%s', has too many characters."
                         " Please enter a label of %s or fewer "
                         "characters.") % (label, length)

    return r(label=label, error_message=error_message)


def recursive_search(params, class_name=None, method=None, args={}):
    """Recursive params checker

    Iterates through all items of a passed in dict, tuple, or list
    and either returns everything as a list, returns an optional subset of them
    or calls a specified method on the subset

    Example Usage:

    .. code-block:: python

        from autoprotocol.protocol import Protocol
        from autoprotocol.container import Well
        from autoprotocol_utilities import recursive_search

        p = Protocol()

        example_container = p.ref(name="example", id=None, cont_type="96-pcr",
                                  storage="ambient")

        p.dispense(ref=example_container, reagent="water",
                   columns=[{"column": 0, "volume": "20:microliters"},
                            {"column": 1, "volume": "10:microliters"}
                            ])

        wells = example_container.wells_from(start=0, num=9, columnwise=True)

        recursive_search(params=wells.wells, class_name=Well,
                         method=volume_check, args={"usage_volume": 15})
    Returns:

    .. code-block:: python

        ["1 volume errors: You want to pipette 15.0 ul from a container with "
        "3.0 ul dead volume (18.0 ul total). However, your aliquot: example-1,"
        "only has 10.0 ul."]

    Parameters
    ----------
    params : list, tuple or dict
        Structure to parse
    class_name : Class name, optional
        Optionally return only instances of a class.
    method : function, optional
        A function that will be applied to all instances found of a class,
        must include class name.
    args : parameters, optional
        Parameters to pass to a method, if desired.

    Returns
    -------
    list
        Will return a list of all items, or the found items of a specified
        class, or the response (if not None) from a method called on found
        items.


    """

    all_fields = []

    def find_all_fields(params):
        if isinstance(params, dict):
            for key, value in params.items():
                all_fields.append(key)
                find_all_fields(value)
        elif isinstance(params, list) or isinstance(params, tuple):
            for item in params:
                find_all_fields(item)
        else:
            all_fields.append(params)

    find_all_fields(params)

    if class_name:
        found_instances = []
        for field in all_fields:
            if isinstance(field, class_name):
                found_instances.append(field)
        if method:
            method_msgs = []
            if hasattr(method, '__call__'):
                for found in found_instances:
                    response = method(found, **args)
                    if response is not None:
                        method_msgs.append(response)
            else:
                raise Exception("Method called has no method __call__")
            return method_msgs
        else:
            return found_instances
    else:
        return all_fields


def transfer_properties(src_wells, dest_wells, properties={}, args={},
                        pset=False):
    """Transfer all or select propeties from one well to another

    Uses add_properties to transfer the properties from one well to another

    Parameters
    ----------
    src_wells: well, list of wells, WellGroup
    dest_wells: well, list of wells, WellGroup
    properties: dict, optional
        Dict with properties to transfer as keys and a function to modify
        property as value. If no modification is required, put None.
        If the dict is empty all propeties will be transferred.
    args: dict, optional
        Dict of dicts where the key is the property used to indicate the
        function and the value another dict containing the arguments.
    pset: bool, optional
        Indicate where to set or add the property, defaults to add.

    Returns
    -------
    list
        List of strings if some properties could not be found
    None
        If no messages were found

    Raises
    ------
    ValueError
        If src_wells or dest_wells are not of type well
    ValueError
        If src_wells and dest_wells are not of equal length
    ValueError
        If properties is not of type dict
    """

    if isinstance(src_wells, Well):
        src_wells = [src_wells]
    if isinstance(dest_wells, Well):
        dest_wells = [dest_wells]

    assert isinstance(src_wells, (list, WellGroup))
    assert isinstance(dest_wells, (list, WellGroup))
    assert len(src_wells) == len(dest_wells)
    assert isinstance(properties, dict)
    for well in list(src_wells) + list(dest_wells):
        assert isinstance(well, Well)

    def dummy(prop):
        return prop

    error_messages = []

    if len(properties) == 0:
        for i, well in enumerate(src_wells):
            if pset:
                dest_wells[i].set_properties(well.properties)
            else:
                dest_wells[i].add_properties(well.properties)
    else:
        for prop, func in properties.items():
            if func is None:
                func = dummy
            for i, well in enumerate(src_wells):
                if prop in well.properties:
                    if pset:
                        dest_wells[i].set_properties(
                            {prop: func(well.properties[prop],
                                        **args.get(prop, {}))})
                    else:
                        dest_wells[i].add_properties(
                            {prop: func(well.properties[prop],
                                        **args.get(prop, {}))})
                else:
                    error_messages.append("Could not find property %s on "
                                          "well%s." % (prop, well))

    if len(error_messages) > 0:
        return error_messages
    else:
        return None
