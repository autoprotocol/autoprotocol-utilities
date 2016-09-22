=========
Changelog
=========

* :feature:`-` added well generator :ref:`next-wells`

* :release:`2.2.1 <2016-09-12>`
* :support:`- backported` fix dox example :ref:`thermocycle-ramp`
* :bug:`-` fixed python2/3 compatibility bugs
* :feature:`- backported` Travis-ci and tox checkers added
* :bug:`-` fix import compatibility for py3

* :release:`2.2.0 <2016-07-28>`
* :support:`-` new changelog and improved documentation
* :feature:`-` bio_calculators module 
* :bug:`- major` sys.path.insert typo in docs/conf.py
* :bug:`- major` fix :ref:`thermocycle-ramp` calculations

* :release:`2.1.7 <2016-06-29>`
* :bug:`-` :ref:`flatten-list` can flatten WellGroup
* :feature:`- backported` positive control for Gibson assembly

* :release:`2.1.6 <2016-06-24>`
* :support:`- backported` more examples to functions

* :release:`2.1.5 <2016-06-14>`
* :feature:`- backported` include positive control reagents for exonuclease assembly kits
* :bug:`-` Container storage for :ref:`ref-kit-container`

* :release:`2.1.4 <2016-05-11>`
* :support:`- backported` additonal tests and documentation
* :feature:`- backported` media types and restriction enzymes
* :bug:`-` :ref:`unique-containers` can properly deal with WellGroups

* :release:`2.1.3 <2016-04-07>`
* :bug:`-` :ref:`container-type-checker` now returns consolidated string of all container errors found
* :support:`- backported` added additional information to oligo scale limit error messages
* :bug:`-` :ref:`volume-check` now returns consolidated string of errors
* :support:`- backported` documentation improvements

* :release:`2.1.2 <2016-04-05>`
* :bug:`-` :ref:`well-name` now takes and argument `humanize` which results in the index being printed as `A1` as opposed to `0`

* :release:`2.1.1 <2016-04-05>`
* :feature:`-` additional resources in :ref:`resource_helpers`
* :feature:`-` magnetic helper functions in :ref:`magnetic_helpers`
* :feature:`-` allow container type strings for wells_available in :ref:`plates-needed`

* :release:`2.0.1 <2016-03-29>`
* :feature:`- backported` allow :ref:`set-pipettable-volume` to process wells from many containers
* :support:`- backported` improvements in documentation
* :feature:`- backported` add resources for exonuclease and picrogreen assays in :ref:`resource_helpers`

* :release:`2.0.0 <2016-03-18>`
* :feature:`-` add `restriction_enzyme_buffers` method to ResourceIDs
* :feature:`-` resource id adjustments in :ref:`resource_helpers`
* :feature:`-` use new unit system (pint) with autoprotocol-python 3.0

* :release:`1.5.0 <2016-03-11>`
* :release:`1.4.4 <2016-03-11>`
* :feature:`- backported` t4_ligase() method for :ref:`resource-ids`
* :feature:`- backported` adjust media strings
* :support:`- backported` documentation

* :release:`1.4.3 <2016-03-06>`
* :support:`- backported` ligase reagents and better documentation

* :release:`1.4.2 <2016-03-06>`
* :feature:`- backported` 10nm scale to oligo_scale_default
* :feature:`- backported` transfer_properties
* :feature:`- backported` :ref:`volume-check` can accept a list of wells or WellGroup
* :feature:`- backported` :ref:`stamp-shape` now always returns a list. `start_well` will be of type Well. `start_well` will be None if no shape is found
* :feature:`- backported` :ref:`stamp-shape` also returns `included_wells`
* :feature:`- backported` renaming some reactangle functions
* :feature:`- backported` add transformation controls
* :feature:`- backported` :ref:`stamp-shape` does not break anymore when presented with a container that is not 96 or 384 well. returns all wells as remaining
* :feature:`- backported` :ref:`unique-containers` can also deal with single well
* :feature:`- backported` rewrite is_columnwise

* :release:`1.4.0 <2016-02-28>`
* :feature:`-` :ref:`user-errors-group` optional info parameter
* :support:`-` modules - moved to promodules

* :release:`1.3.0 <2016-02-24>`
* :feature:`-` :ref:`container-type-checker` function
* :feature:`-` :ref:`stamp-shape` can now deal with 384 plates (quadrants)
* :bug:`- major` createMastermix Unit input

* :release:`1.2.0 <2016-02-22>`
* :feature:`-` :ref:`user-errors-group` automatically filters out None
* :bug:`- major` :ref:`user-errors-group`
* :bug:`- major` stamp function defaults to only return full row or col stamp

* :release:`1.1.0 <2016-02-19>`
* :feature:`-` :ref:`well-name` function
* :feature:`-` :ref:`recursive-search` function
* :feature:`-` :ref:`first-empty-well` can take a list of wells or container
* :feature:`-` :ref:`list-of-filled-wells` can take a list of wells or container
* :bug:`- major` stray setup.py

* :release:`1.0.0 <2016-02-18>`
* :feature:`-` Initial release
