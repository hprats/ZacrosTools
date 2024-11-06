## [1.02] - 06-Nov-2024

### Added
- Added new parameters in `KMCModel.create_job_dir` in anticipation of a future version of Zacros.

### Changed
- In `KMCModel.create_job_dir` method, parameter `auto_scaling_steps` has been renamed to `stiffness_scaling_steps`and 
parameter `auto_scaling_tags` has been renamed to `stiffness_scaling_tags`.

### Fixed
- Fixed bug where, if only one surface species was declared, `surf_specs_dent` would be an integer instead of a list.
- Fixed bug where the total pressure could be written as an integer, and then the simulation will crash.

### Improved
- Now, ZacrosTools checks if the keywords provided in `stiffness_scaling_tags` are allowed.
- Improved the [ZacrosTools Documentation](https://zacrostools.readthedocs.io/en/latest/).

## [1.01] - 13-Oct-2024

### Added
- Added data validation and error handling in `plot_result.py`.
- *ZacrosTools* is now compatible with multidentate species.
- *ZacrosTools* is now compatible with default lattices.

### Changed
- The `detect_issues` function now only considers the specified window percent.
- Default `window_percent` for `detect_issues` changed from `[50, 100]` to `[30, 100]`.

### Fixed
- Bug fix for cases where vibrational energies of 0.0 are specified in the reaction model. 

### Improved
- Improved the [ZacrosTools Documentation](https://zacrostools.readthedocs.io/en/latest/).

## [1.0] - 06-Sep-2024

Initial release.
