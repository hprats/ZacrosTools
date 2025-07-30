# Changelog

All notable changes to this project are documented in this file.

## [2.5] - 30-Jul-2025

### Added
- **Additional keywords support**: added an `additional_keywords` parameter to `KMCModel.create_job_dir` and `write_simulation_input` to append additional Zacros keywords to `simulation_input.dat`.  
- **`sign` parameter for ∆time heatmaps**: introduced a `sign` argument in `plot_dtime` (`'both'`, `'positive'`, or `'negative'`) to filter ∆time values by sign.  
- **Issue masking in ∆TOF heatmaps**: added a `check_issues` parameter to `plot_dtof` (`'none'`, `'both'`, `'main'`, or `'ref'`) to mask cells flagged by `detect_issues`.  
- **Unspecified state support**: `EnergeticsModel` now accepts the `& & &` placeholder in `lattice_state` definitions to represent unspecified site states.  
- **Multidentate species support**: `EnergeticsModel` handles adsorbates multidentate surface species occupying multiple site types.  

### Changed 
- **Surface species name parsing**: removed the requirement that species names end with `*`. Surface species names now stay exactly as typed by the user (i.e. no removal of `*` at the end).

### Fixed
- **`parse_general_output_file` crash**: fixed a bug that caused a crash when an initial state is provided.
- **∆TOF docstring & title logic**: corrected the relative ∆TOF formula in `plot_dtof`’s docstring.

## [2.4] - 11-Apr-2025

### Added
- **Specialized functions for creating heatmaps**: New functions `plot_dtime` and `plot_cputime`.

### Fixed
- **Stiffness scalable steps**: Resolved a bug where `stiffness_scalable_steps = 'all'` could be ignored.

## [2.3] - 04-Apr-2025

### Added
- **Specialized functions for creating heatmaps**: Each heatmap type now has its own function (e.g., `plot_tof`, `plot_selectivity`).
- **∆TOF heatmaps**: New function `plot_dtof` computes and plots the difference in TOF (absolute or relative) between two simulations.
- **Periodic lattice plotting**: New function `plot_periodic_lattice` to visualize a periodic lattice model.
- **Stiffness scalable steps**: It is now possible to set `stiffness_scalable_steps = 'all'` in `create_job_dir`.
- **Zacros version parameter**: New `version` parameter in `create_job_dir` to specify the Zacros version.

### Fixed
- **Non-zero TOF bug**: Resolved a numerical issue where a poisoned catalyst could yield a non-zero TOF.
- **Adsorption step bug**: Fixed a requirement for `vib_energies_ts` in non-activated steps when creating a reaction model from a dictionary.
- **Event frequencies**: Updated `plot_procstat` to ensure compatibility with models that include irreversible steps.

## [2.2] 20-Dec-2024

### Added
- **Plot event frequencies**: introduced the ability to parse the event frequencies from `procstat_output.txt` using `zacrostools.procstat_output` and visualize them.
- **Plot stiffness coefficients**: added functionality to parse stiffness coefficient information from `general_output.txt` using `zacrostools.parse_general_output_file` and generate corresponding plots.
- **Examples:**  
  - **`DRM_on_PtHfC`**: Demonstrates how to analyze hundreds of output files to generate heatmaps and plot the event frequencies and stiffness coefficients.
  - **`custom_lattice_models`**: Illustrates how to create custom lattice models for Zacros simulations.

### Changed
- **Analysis of output files:**  
  - Renamed `window_percent` to `analysis_range` 
  - Renamed `window_type` to `range_type`

### Improved
- **Documentation**: Improved the [ZacrosTools Documentation](https://zacrostools.readthedocs.io/en/latest/).

## [2.1] 27-Nov-2024

### Added
- **New classes and methods**: introduced the following classes, which can be instantiated from a Python dictionary, a Pandas DataFrame, or a `.csv` file:
  - `GasModel`: information about gas-phase species. Methods available: `add_species` and `remove_species`. 
  - `EnergeticsModel`: information about each cluster in the cluster expansion. Methods available: `add_cluster`, `remove_cluster` and `write_energetics_input`.
  - `ReactionModel`: information about each elementary step. Methods available: `add_step`, `remove_steps` and `write_mechanism_input`.
- **Automatic neighboring structure generation**: use a distance criteria between site to automatically create the neighboring structure for a custom lattice model. 
- **Total pressure in heatmap axes**: the `total_pressure` parameter can now be selected for either the `x` or `y` axis in heatmap plots, enabling the creation of pressure vs temperature heatmaps.
- **Continuous integration tests**: added a new test for GitHub Actions that generates all input files and compares them against reference files to ensure consistency.
- **New parameters**: 
  - `sig_figs_lattice`: added to `KMCModel.create_job_dir` to control the number of significant figures used when writing coordinates in `lattice_input.dat`.
  - `show_max`: added to `plot_heatmap` to display a green 'x' marker at the point with the highest TOF. 

### Changed
- **Building a `KMCModel`**: the `KMCModel` construction process now requires a `GasModel`, an `EnergeticsModel`, a `ReactionModel`, and a `LatticeModel`.

### Improved
- **Output file parsing**: enhanced `parse_general_output` to support parsing `general_output.txt` files generated by Zacros version 2.x. 
- **Parameter validation**: improved the parsing and validation of selected parameters across all modules to prevent errors. 
- **Docstrings**: updated all docstrings to adhere to the NumPy format for better clarity and consistency.
- **Documentation**: Improved the [ZacrosTools Documentation](https://zacrostools.readthedocs.io/en/latest/).

## [1.3] 07-Nov-2024

### Added
- **Comprehensive test suite with Pytest**: Implemented a suite of tests using Pytest to ensure code reliability and facilitate future development.
- **Continuous integration with GitHub Actions**: Set up CI workflows to automatically run tests on every push and pull request, enhancing code quality and preventing regressions.
- **Documentation**:
  - Updated `README.md` with detailed installation instructions, usage examples, badges, and contributor guidelines.

## [1.2] 06-Nov-2024

### Added
- **New parameters in `KMCModel.create_job_dir`**: Introduced new parameters in anticipation of a future version of Zacros.

### Changed
- **Parameter renaming in `KMCModel.create_job_dir`**:
  - Renamed `auto_scaling_steps` to `stiffness_scaling_steps`.
  - Renamed `auto_scaling_tags` to `stiffness_scaling_tags`.

### Fixed
- **Surface species list bug**: Resolved an issue where, if only one surface species was declared, `surf_specs_dent` would be an integer instead of a list.
- **Total pressure format**: Fixed a bug where the total pressure could be written as an integer, causing simulation crashes.

### Improved
- **Keyword validation**: Added checks to ensure that the keywords provided in `stiffness_scaling_tags` are allowed.
- **Documentation enhancements**: Improved the [ZacrosTools Documentation](https://zacrostools.readthedocs.io/en/latest/).

## [1.1] 13-Oct-2024

### Added
- **Data validation in `plot_result.py`**: Implemented data validation and error handling to improve robustness.
- **Support for multidentate species**: ZacrosTools now supports multidentate species.
- **Compatibility with default lattices**: Added support for default lattice configurations.

### Changed
- **`detect_issues` function**:
  - Adjusted the function to consider only the specified analysis range.
  - Changed default `analysis_range` from `[50, 100]` to `[30, 100]`.

### Fixed
- **Vibrational energies bug**: Fixed an issue where specifying vibrational energies of 0.0 could cause unexpected behavior.

### Improved
- **Documentation**: Updated and expanded the [ZacrosTools Documentation](https://zacrostools.readthedocs.io/en/latest/).

## [1.0] 06-Sep-2024

### Initial Release
- Launched ZacrosTools with core functionalities for preparing Zacros input files and parsing output data.
