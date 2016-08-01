# Autoprotocol Utilities

[![Build Status](https://travis-ci.org/autoprotocol/autoprotocol-utilities.svg?branch=master)](https://travis-ci.org/autoprotocol/autoprotocol-utilities)
[![PyPI version](https://img.shields.io/pypi/v/autoprotocol-utilities.svg?maxAge=2592000)](https://pypi.python.org/pypi/autoprotocol-utilities)

View Autoprotocol-utilities [Documentation](http://autoprotocol-utilities.readthedocs.org/en/latest/) on readthedocs.org

[Autoprotocol](http://www.autoprotocol.org) is a standard way to express
experiments in life science. This repository contains helper functions to be used with the [Autoprotocol-python](https://github.com/autoprotocol/autoprotocol-python) library to generate Autoprotocol.

## Installation

	$ pip install autoprotocol_utilities

	OR
	
    $ git clone https://github.com/autoprotocol/autoprotocol-utilities
    $ cd autoprotocol-utilities
    $ python setup.py install

 Check the releases tab or the [changelog](http://autoprotocol-utilities.readthedocs.org/en/latest/changelog.html) in this repository to see the latest release that will be downloaded.

## Example Usage

.. code-block:: python

	from autoprotocol import Protocol
	from autoprotocol_utilities.container_helpers import volume_check

	p = Protocol()
	example_container = p.ref(name="exampleplate", id=None, cont_type="96-pcr", storage="warm_37")
	p.dispense(ref=example_container, reagent="water", columns=[{"column": 0, "volume": "10:microliters"}])

	# Checks if there are 5 microliters above the dead volume available in well 0
	assert (volume_check(well=example_container.well(0), usage_volume=5)) is None
	# Checks if the volume in well 0 is at least the safe minimum volume
	assert (volume_check(well=example_container.well(0), usage_volume=0, use_safe_vol=True) is None

## Extras

A folder of SublimeText snippets for this library is included in this repository.

## Contributing

The easiest way to contribute is to fork this repository and submit a pull
request.  You can also submit an issue or write an email to us at
support@transcriptic.com if you want to discuss ideas or bugs.

autoprotocol-utilities is BSD licensed (see [LICENSE]http://autoprotocol-utilities.readthedocs.org/en/latest/LICENSE.html)).
Before we can accept your pull request, we require that you sign a CLA (Contributor License Agreement)
allowing us to distribute your work under the BSD license. Email one of the [AUTHORS](http://autoprotocol-utilities.readthedocs.org/en/latest/AUTHORS.html) for more details.
