# CHANGELOG

This project adheres to [Semantic Versioning](http://semver.org/)

## Unreleased
---
Added
- flatten_list() can flatten WellGroup

Changed

Removed

Fixed

## v2.1.6 - 2016-06-24
---
Added
- more examples to functions

Changed

Removed

Fixed

## v2.1.5 - 2016-06-14
---
Added
- include positive control reagents for exonuclease assembly kits

Changed

Removed

Fixed
- Container storage for ref_kit_items()

## v2.1.4 - 2016-05-11
---
Added
 - additonal tests and documentation
 - media types and restriction enzymes
Changed

Removed

Fixed
 - unique_containers can properly deal with WellGroups

## v2.1.3 - 2016-04-07
---
Added

Changed
 - check_container_type now returns consolidated string of all container errors found
 - added additional information to oligo scale limit error messages
 - volume_check now returns consolidated string of errors
 - documentation improvements

Removed

Fixed

## v2.1.2 - 2016-04-05
---
Added

Changed
 - well_name now takes and argument `humanize` which results in the index being printed as `A1` as opposed to `0`

Removed

Fixed

## v2.1.1 - 2016-04-05
---
Added
- additional resources
- magnetic helper functions
- allow container type strings for wells_available in plates_needed

Changed

Removed

Fixed

## v2.0.1 - 2016-03-29
---
Added

Changed
- allow set_pipettable_volume() to process wells from many containers
- improvements in documentation
- add resources for exonuclease and picrogreen assays

Removed

Fixed

## v2.0.0 - 2016-03-18
---
Added
- add `restriction_enzyme_buffers` method to ResourceIDs
- resource id adjustments
- use new unit system (pint) with autoprotocol-python 3.0

Changed

Removed

Fixed

## v1.4.4 - 2016-03-011
---
Added
- t4_ligase() method for ResourceIDs
- adjust media strings
- documentation

Changed

Removed

Fixed

## v1.4.3 - 2016-03-06
---
Added
- ligase reagents and better documentation

Changed

Removed

Fixed

## v1.4.2 - 2016-03-06
---
Added
- 10nm scale to oligo_scale_default
- transfer_properties

Changed
- volume_check() can accept a list of wells or WellGroup
- stamp_shape() now always returns a list. start_well will be of type Well. start_well will be None if no shape is found
- stamp_shape() also returns included_wells
- renaming some reactangle functions
- add transformation controls
- stamp_shape() does not break anymore when presented with a container that is not 96 or 384 well. returns all wells as remaining
- unique_containers can also deal with single well
- rewrite is_columnwise

Removed

Fixed

## v1.4.0 - 2016-02-28
---
Added

Changed
- user_error_groups optional info parameter

Removed
modules - moved to promodules

Fixed

## v1.3.0 - 2016-0-24
---
Added
- container_type_checker() function

Changed
- stamp shape() can now deal with 384 plates (quadrants)

Removed

Fixed
- createMastermix Unit input

## v1.2.0 - 2016-0-22
---
Added

Changed
- user_errors_group automatically filters out None

Removed

Fixed
 - user_error_groups
 - stamp function defaults to only return full row or col stamp

## v1.1.0 - 2016-02-19
---
Added
- well_name() function
- recursive_search() function
- first_empty_well() can take a list of wells or container
- list_of_filled_wells() can take a list of wells or container

Changed

Removed
- stray setup.py

Fixed

## v1.0.0 - 2016-02-18
---
Added
- Initial release

Changed

Removed

Fixed
