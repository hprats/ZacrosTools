# Welcome to ZacrosTools Documentation

Welcome to the ZacrosTools documentation! This guide provides comprehensive information on using the ZacrosTools Python library.

ZacrosTools is a versatile toolkit designed to simplify the preparation and analysis of Kinetic Monte Carlo (KMC) simulations with **[Zacros](https://zacros.org/)**.

## Key Features

- **Automatic input file generation**: Simplify the creation of Zacros input files, reducing the risk of errors and speeding up the setup process.
- **Output file parsing**: Easily read, analyze and process data from Zacros output files.
- **Pressure and temperature scans**: Streamline the process of performing scans over different pressures and temperatures.
- **Customizable workflows**: Create customised workflows to fit specific simulation needs.
- **Documentation and examples:** Extensive documentation is available, including detailed examples to help users quickly get started and make the most of ZacrosTools.

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/ScanTof.png?raw=true" alt="ScanTof" width="400"/>
</div>

### Recent Changes

#### [1.3] - 07-Nov-2024

##### Added
- **Comprehensive Test Suite with Pytest**: Implemented a suite of tests using Pytest to ensure code reliability and facilitate future development.
- **Continuous Integration with GitHub Actions**: Set up CI workflows to automatically run tests on every push and pull request, enhancing code quality and preventing regressions.
- **Enhanced Documentation**:
  - Updated `README.md` with detailed installation instructions, usage examples, badges, and contributor guidelines.

#### [1.2] - 06-Nov-2024

##### Added
- **New Parameters in `KMCModel.create_job_dir`**: Introduced new parameters in anticipation of a future version of Zacros.

##### Changed
- **Parameter Renaming in `KMCModel.create_job_dir`**:
  - Renamed `auto_scaling_steps` to `stiffness_scaling_steps`.
  - Renamed `auto_scaling_tags` to `stiffness_scaling_tags`.

##### Fixed
- **Surface Species List Bug**: Resolved an issue where, if only one surface species was declared, `surf_specs_dent` would be an integer instead of a list.
- **Total Pressure Format**: Fixed a bug where the total pressure could be written as an integer, causing simulation crashes.

##### Improved
- **Keyword Validation**: Added checks to ensure that the keywords provided in `stiffness_scaling_tags` are allowed.
- **Documentation Enhancements**: Improved the [ZacrosTools Documentation](https://zacrostools.readthedocs.io/en/latest/).

Full details in the [ZacrosTools CHANGELOG](https://github.com/hprats/ZacrosTools/blob/main/CHANGELOG.md).

### What’s Next:
We plan to continue improving ZacrosTools with additional features, optimizations, and support for more advanced Zacros functionalities. We welcome contributions from the community and are eager to hear feedback on this initial release.

### Contributors

- Hector Prats

```{eval-rst}
.. toctree::
   :maxdepth: 3
   :caption: Contents

   installation.md
   writing_input_files.md
   reading_output_files.md
   plotting_results.md
   api_reference.md
```
