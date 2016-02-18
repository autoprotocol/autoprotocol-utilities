from autoprotocol.unit import Unit
import sys


if sys.version_info[0] >= 3:
    string_type = str
else:
    string_type = basestring


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
