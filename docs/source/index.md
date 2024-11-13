# Welcome to ZacrosTools Documentation

[![PyPI](https://img.shields.io/pypi/v/zacrostools)](https://pypi.org/project/zacrostools/)
[![License](https://img.shields.io/github/license/hprats/ZacrosTools)](https://github.com/hprats/ZacrosTools/blob/main/LICENSE)
[![CI](https://github.com/hprats/ZacrosTools/actions/workflows/ci.yml/badge.svg)](https://github.com/hprats/ZacrosTools/actions/workflows/ci.yml)

Welcome to the ZacrosTools documentation! This guide provides comprehensive information on using the ZacrosTools Python library.

ZacrosTools is a versatile toolkit designed to simplify the preparation and analysis of Kinetic Monte Carlo (KMC) simulations with **[Zacros](https://zacros.org/)**.

## Key Features 

- **Automatic input file generation**: Simplify the creation of Zacros input files, reducing the risk of errors and speeding up the setup process.
- **Output file parsing**: Easily read, analyze, and process data from Zacros output files.
- **Pressure and temperature scans**: Streamline the process of performing scans over different pressures and temperatures.
- **Customizable workflows**: Create customized workflows to fit specific simulation needs.
- **Documentation and examples**: Extensive documentation is available, including detailed examples to help users quickly get started and make the most of ZacrosTools.

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/ScanTof.png?raw=true" alt="ScanTof" width="400"/>
    <p>Example of turnover frequency heatmap generated using ZacrosTools.</p>
</div>

## Installation 

ZacrosTools is available on PyPI and can be installed using `pip`:

```bash
pip install zacrostools
```

### Prerequisites 

- **Python 3.8 or higher**
- **[Scipy](https://scipy.org/)**
- **[Pandas](https://pandas.pydata.org/)**

These dependencies will be installed automatically with `pip`.

### Installing from Source

To install the latest development version from GitHub:

```bash
git clone https://github.com/hprats/ZacrosTools.git
cd ZacrosTools
pip install .
```

## Quick Start Guide

Get started with ZacrosTools by following these steps:

1. **Define the Gas Model**: Specify gas-phase molecular data required for your simulations.
2. **Set Up the Lattice Model**: Define the lattice structure on which the KMC simulation will run.
3. **Create the Energetics Model**: Provide cluster formation energies and configurations.
4. **Define the Reaction Model**: Outline the reaction mechanisms and steps involved in the simulation.
5. **Assemble the KMC Model**: Combine all models to prepare for running simulations.
6. **Run Simulations**: Execute KMC simulations using Zacros with the generated input files.
7. **Analyze Results**: Parse and visualize the output data to gain insights.

Detailed instructions for each step are provided in the documentation sections below.

## Documentation

The ZacrosTools documentation is organized into the following sections:

- **[Gas Model](gas_model.md)**: Learn how to define gas-phase molecular data for KMC simulations.
- **[Lattice Model](lattice_model.md)**: Understand how to set up lattice structures for simulations.
- **[Energetics Model](energetics_model.md)**: Define cluster energetics for your simulations.
- **[Reaction Model](reaction_model.md)**: Specify reaction mechanisms and steps.
- **[KMC Model](kmc_model.md)**: Integrate all components to set up and run KMC simulations.
- **[Reading Output Files](reading_output_files.md)**: Parse and analyze data from Zacros output files.
- **[Plotting Results](plotting_results.md)**: Visualize simulation results effectively.
- **[API Reference](api_reference.md)**: Detailed API documentation for ZacrosTools modules and classes.

## Recent Changes

### [1.3] - 07-Nov-2024

#### Added

- **Comprehensive Test Suite with Pytest**: Implemented a suite of tests using Pytest to ensure code reliability and facilitate future development.
- **Continuous Integration with GitHub Actions**: Set up CI workflows to automatically run tests on every push and pull request, enhancing code quality and preventing regressions.
- **Enhanced Documentation**:
  - Updated `README.md` with detailed installation instructions, usage examples, badges, and contributor guidelines.

Full details are available in the [ZacrosTools CHANGELOG](https://github.com/hprats/ZacrosTools/blob/main/CHANGELOG.md).

## What's Next

We plan to continue improving ZacrosTools with additional features, optimizations, and support for more advanced Zacros functionalities.

Contributions are welcome!

- **Report Bugs**: Use the [issue tracker](https://github.com/hprats/ZacrosTools/issues) to report bugs.
- **Request Features**: Suggest new features or improvements.
- **Submit Pull Requests**: Fork the repository and submit pull requests for your contributions.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/hprats/ZacrosTools/blob/main/LICENSE) file for details.

## Contributors

- **Hector Prats** - [hector.pratsgarcia@chem.ox.ac.uk](mailto:hector.pratsgarcia@chem.ox.ac.uk)

```{eval-rst}
.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation.md
   gas_model.md
   lattice_model.md
   energetics_model.md
   reaction_model.md
   kmc_model.md
   reading_output_files.md
   plotting_results.md
   api_reference.md
```
