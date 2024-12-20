<header style="text-align: center; padding: 20px;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/logo_without_background.png?raw=true" alt="ZacrosTools Logo" width="200"/>
</header>

# Welcome to the ZacrosTools documentation

[![PyPI](https://img.shields.io/pypi/v/zacrostools)](https://pypi.org/project/zacrostools/)
[![License](https://img.shields.io/github/license/hprats/ZacrosTools)](https://github.com/hprats/ZacrosTools/blob/main/LICENSE)
[![CI](https://github.com/hprats/ZacrosTools/actions/workflows/ci.yml/badge.svg)](https://github.com/hprats/ZacrosTools/actions/workflows/ci.yml)

This guide provides comprehensive information on using the ZacrosTools Python library.

ZacrosTools is a versatile toolkit designed to simplify the preparation and analysis of Kinetic Monte Carlo (KMC) simulations with **[Zacros](https://zacros.org/)**.

## Key features 

- **Automatic input file generation**: Easily create Zacros input files, reducing errors.
- **Output file parsing**: Quickly read, analyze, and process Zacros output data.
- **Pressure and temperature scans**: Streamline the process of performing scans over different pressures and temperatures.
- **Documentation and examples:** Extensive documentation with detailed examples to help users get started and make full use of ZacrosTools.

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/multiple_heatmaps.png?raw=true" alt="Multiple heatmaps" width="700"/> </div>

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

### Installing from source

To install the latest development version from GitHub:

```bash
git clone https://github.com/hprats/ZacrosTools.git
cd ZacrosTools
pip install .
```

## Quick start guide

Get started with ZacrosTools by following these steps:

1. **Define the `GasModel`, the `EnergeticsModel` and the `ReactionModel` from a Python dictionary, a Pandas DataFrame, or a `.csv` file**
2. **Create a default or custom `LatticeModel`**
3. **Combine all previous models to create a `KMCModel`**
4. **Write the input files with {py:func}`KMCModel.create_job_dir()` and run Zacros**
5. **Parse the results with `KMCOutput` and visualize the results with `plot_functions` to gain insights**

Detailed instructions for each step are provided in the documentation sections below.

## Documentation

The ZacrosTools documentation is organized into the following sections:

- **[Gas model](gas_model.md)**: Learn how to define the gas-phase molecular data.
- **[Energetics model](energetics_model.md)**: Define all the terms used in the cluster expansion.
- **[Reaction model](reaction_model.md)**: Specify the elementary steps included in the reaction mechanism.
- **[Lattice model](lattice_model.md)**: Understand how to set up a lattice model.
- **[Writing_input_files](writing_input_files.md)**: Integrate all components into a KMC model and write the Zacros input files.
- **[Reading output files](reading_output_files.md)**: Parse and analyze data from Zacros output files.
- **[Plotting single simulation results](plotting_single_simulation.md)**: Plot the simulation results, such as surface coverage, molecules produced, or event frequencies. 
- **[Plotting heatmaps](plotting_heatmaps.md)**: Draw heatmap plots from a set of KMC simulations at various operating conditions.
- **[API reference](api_reference.md)**: Detailed API documentation for ZacrosTools modules and classes.

## Recent changes

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

Full details are available in the [ZacrosTools CHANGELOG](https://github.com/hprats/ZacrosTools/blob/main/CHANGELOG.md).

## What's next

We plan to continue improving ZacrosTools with additional features, optimizations, and support for more advanced Zacros functionalities.

Contributions are welcome!

- **Report bugs**: Use the [issue tracker](https://github.com/hprats/ZacrosTools/issues) to report bugs.
- **Request features**: Suggest new features or improvements.
- **Submit pull requests**: Fork the repository and submit pull requests for your contributions.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/hprats/ZacrosTools/blob/main/LICENSE) file for details.

## Contributors

- **Hector Prats** - [hector.prats@tuwien.ac.at](mailto:hector.prats@tuwien.ac.at)

## Acknowledgements

- **Zeyu Wu** 

```{eval-rst}
.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation.md
   gas_model.md
   energetics_model.md
   reaction_model.md
   lattice_model.md
   writing_input_files.md
   reading_output_files.md
   plotting_single_simulation.md
   plotting_heatmaps.md
   api_reference.md
```
