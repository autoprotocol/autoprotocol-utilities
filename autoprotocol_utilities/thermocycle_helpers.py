from autoprotocol.unit import Unit
import sys

if sys.version_info[0] >= 3:
    string_type = str
else:
    string_type = basestring


def melt_curve(start=65, end=95, inc=0.5, rate=5):
    """Generate a melt curve on the fly

    No inputs neded for a standard melt curve.

    Example Usage:

    .. code-block:: python

        from autoprotocol import Protocol
        from autoprotocol_utilities import melt_curve
        protocol = Protocol()

        dest_plate = protocol.ref("plate", None, "96-pcr", discard=True,
                                  storage=None)
        protocol.seal(dest_plate)
        melt_params = melt_curve()
        protocol.thermocycle(dest_plate,
                             [{"cycles": 1,
                               "steps": [
                                   {"temperature": "37:celsius",
                                   "duration": "60:minute"}
                                   ]
                               }
                              ],
                             volume="15:microliter",
                             dataref="data",
                             dyes={"SYBR":
                             dest_plate.wells_from(0, 3).indices()},
                             **melt_params)

    Returns:

    .. code-block:: json

        {
          "refs": {
            "plate": {
              "new": "96-pcr",
              "discard": true
            }
          },
          "instructions": [
            {
              "object": "plate",
              "type": "ultra-clear",
              "op": "seal"
            },
            {
              "dataref": "data",
              "melting": {
                "start": "65.00:celsius",
                "rate": "5.00:second",
                "end": "95.00:celsius",
                "increment": "0.50:celsius"
              },
              "object": "plate",
              "volume": "15:microliter",
              "groups": [
                {
                  "cycles": 1,
                  "steps": [
                    {
                      "duration": "60:minute",
                      "temperature": "37:celsius"
                    }
                  ]
                }
              ],
              "dyes": {
                "SYBR": [
                  "A1",
                  "A2",
                  "A3"
                ]
              },
              "op": "thermocycle"
            }
          ]
        }

    Parameters
    ----------
    start : int, float
        Temperature to start at
    end : int, float
        Temperature to end at
    inc : int, float
        Temperature increment during the melt_curve
    rate : int
        After x seconds the temperature is incremented by inc

    Returns
    -------
    melt_params : dict
        containing melt_params

    Raises
    ------
    ValueError
        If start, end or inc are not of type `float` or `int`. And if rate is
        not of type `int`

    """
    assert isinstance(start, (float, int))
    assert isinstance(end, (float, int))
    assert isinstance(inc, (float, int))
    assert isinstance(rate, int)

    melt_params = {"melting_start": "%.2f:celsius" % start,
                   "melting_end": "%.2f:celsius" % end,
                   "melting_increment": "%.2f:celsius" % inc,
                   "melting_rate": "%.2f:second" % rate}
    return melt_params


def thermocycle_ramp(start_temp, end_temp, total_duration, step_duration):
    """Create a ramp instruction for the thermocyler.

    Create a multi-temperature thermocycling program commonly used in
    annealing protocols. Based on total time and the step duration this
    function computes the temperature increment required for each step within
    the start and the end temperature.

    Example Usage:

    .. code-block:: python

        thermocycle_group = [
          {
              "cycles": 1,
              "steps": thermocycle_ramp(65, 95, "30:minute", "1:minute")
          }
        ]
        protocol.thermocycle(dest_plate,
                             groups=thermocycle_group,
                             volume="15:microliter")

    Parameters
    ----------
    start_temp: string, int, float, Unit
        Start of the thermocycle protocol, in the format "37:celsius"
    end_temp: string, int, float, Unit
        End of the thermocycle protocol, in the format "37:celsius"
    total_duration: string, Unit
        Total duration of the thermocycle protocol, in the format "1:hour"
    step_duration: string, Unit
        Time that each temperature should be held, in the format "1:minute"

    Returns
    -------
    dict
        containing thermocycling steps that can be used in the
        thermocycle instruction

    Raises
    ------
    ValueError
        If either temperature is not of type `int`, `float`, `string` or
        `Unit` and if either duration is not of type `string` or `Unit`

    """
    assert isinstance(start_temp, (int, float, string_type, Unit))
    assert isinstance(end_temp, (int, float, string_type, Unit))
    assert isinstance(total_duration, (string_type, Unit))
    assert isinstance(step_duration, (string_type, Unit))

    if isinstance(start_temp, string_type):
        start_temp = Unit.fromstring(start_temp)
    elif isinstance(start_temp, (int, float)):
        start_temp = Unit(start_temp, 'degC')
    if isinstance(end_temp, string_type):
        end_temp = Unit.fromstring(end_temp)
    elif isinstance(end_temp, (int, float)):
        end_temp = Unit(end_temp, 'degC')
    if isinstance(total_duration, string_type):
        total_duration = Unit.fromstring(total_duration)
    if isinstance(step_duration, string_type):
        step_duration = Unit.fromstring(step_duration)

    start_temp.to('degC')
    end_temp.to('degC')
    total_duration.to_base_units()
    step_duration.to_base_units()

    num_steps = int(total_duration // step_duration)
    step_size = (end_temp - start_temp).magnitude / num_steps

    thermocycle_steps = []
    for i in range(num_steps + 1):
        thermocycle_steps.append({
            "temperature": "%s:celsius" % (
                start_temp.magnitude + i * step_size),
            "duration": str(step_duration)
        })
    return thermocycle_steps
