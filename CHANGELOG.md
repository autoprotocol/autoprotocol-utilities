# CHANGELOG

This project adheres to [Semantic Versioning](http://semver.org/)

## Unreleased
---
Added

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
