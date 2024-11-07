# Changelog

All notable changes to this project will be documented in this file.

## [1.3] - 07-Nov-2024

### Added
- **Comprehensive Test Suite with Pytest**: Implemented a suite of tests using Pytest to ensure code reliability and facilitate future development.
- **Continuous Integration with GitHub Actions**: Set up CI workflows to automatically run tests on every push and pull request, enhancing code quality and preventing regressions.
- **Enhanced Documentation**:
  - Updated `README.md` with detailed installation instructions, usage examples, badges, and contributor guidelines.

### Improved
- **Project Structure**: Organized the project files and directories for better clarity and maintainability.
- **Error Handling**: Enhanced custom exceptions and error messages for more informative feedback to users.
- **Code Quality**: Refactored code to adhere to PEP 8 standards, improving readability and consistency.

## [1.2] - 06-Nov-2024

### Added
- **New Parameters in `KMCModel.create_job_dir`**: Introduced new parameters in anticipation of a future version of Zacros.

### Changed
- **Parameter Renaming in `KMCModel.create_job_dir`**:
  - Renamed `auto_scaling_steps` to `stiffness_scaling_steps`.
  - Renamed `auto_scaling_tags` to `stiffness_scaling_tags`.

### Fixed
- **Surface Species List Bug**: Resolved an issue where, if only one surface species was declared, `surf_specs_dent` would be an integer instead of a list.
- **Total Pressure Format**: Fixed a bug where the total pressure could be written as an integer, causing simulation crashes.

### Improved
- **Keyword Validation**: Added checks to ensure that the keywords provided in `stiffness_scaling_tags` are allowed.
- **Documentation Enhancements**: Improved the [ZacrosTools Documentation](https://zacrostools.readthedocs.io/en/latest/).

## [1.1] - 13-Oct-2024

### Added
- **Data Validation in `plot_result.py`**: Implemented data validation and error handling to improve robustness.
- **Support for Multidentate Species**: ZacrosTools now supports multidentate species.
- **Compatibility with Default Lattices**: Added support for default lattice configurations.

### Changed
- **`detect_issues` Function**:
  - Adjusted the function to consider only the specified window percent.
  - Changed default `window_percent` from `[50, 100]` to `[30, 100]`.

### Fixed
- **Vibrational Energies Bug**: Fixed an issue where specifying vibrational energies of 0.0 could cause unexpected behavior.

### Improved
- **Documentation Enhancements**: Updated and expanded the [ZacrosTools Documentation](https://zacrostools.readthedocs.io/en/latest/).

## [1.0] - 06-Sep-2024

### Initial Release
- Launched ZacrosTools with core functionalities for preparing Zacros input files and parsing output data.
