################################
Autoprotocol Utils documentation
################################

Autoprotocol Utilities are helper functions and modules to generate autoprotocol faster and include on-the-fly verifications. It can only be used in conjunction with `autoprotocol-python <http://public.readthedocs.com/docs/transcriptic-autoprotocol-python/en/latest/>`_ and automatically installs its required version.

Protocol modules and helper functions such as `createMastermix` can be found in `promodules <https://readthedocs.com/docs/transcriptic-promodules/en/latest/>`_. In contrast to `autoprotocol-utlities`, these do require instances of `Protocol` and return autoprotocol instructions.

.. toctree::
    :maxdepth: 2

    General helpers <general_helpers>
    Resource helpers <resource_helpers>
    Container helpers <container_helpers>
    Thermocyling helpers <thermocycle_helpers>
    AUTHORS


************
Installation
************
.. code-block:: none

    $ git clone ssh://vcs@work.r23s.net/diffusion/APUTILS/autoprotocol-utilities.git
    $ cd autoprotocol-utilities
    $ python setup.py install

or

.. code-block:: none

    $ pip install autoprotocol_utils --extra-index-url https://rZzsY1ZxQC6RiyZapa21@repo.fury.io/transcriptic/


************
Contributing
************

Use Phabricator to contribute code. 
Source Code: https://work.r23s.net/diffusion/APUTILS/


* :ref:`genindex`


:copyright: 2016 by The Autoprotocol Development Team, see AUTHORS
    for more details.
:license: BSD, see LICENSE for more details