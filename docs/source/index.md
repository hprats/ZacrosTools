<header style="text-align: center; padding: 20px;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/logo_without_background.png?raw=true" alt="ZacrosTools Logo" width="200"/>
</header>

# Welcome to the ZacrosTools documentation

[![PyPI](https://img.shields.io/pypi/v/zacrostools)](https://pypi.org/project/zacrostools/)
[![License](https://img.shields.io/github/license/hprats/ZacrosTools)](https://github.com/hprats/ZacrosTools/blob/main/LICENSE)
[![CI](https://github.com/hprats/ZacrosTools/actions/workflows/ci.yml/badge.svg)](https://github.com/hprats/ZacrosTools/actions/workflows/ci.yml)

Welcome to the ZacrosTools documentation! This guide provides comprehensive information on using the ZacrosTools Python library.

ZacrosTools is a versatile toolkit designed to simplify the preparation and analysis of Kinetic Monte Carlo (KMC) simulations with **[Zacros](https://zacros.org/)**.

## Key features 

- **Automatic input file generation**: Simplify the creation of Zacros input files, reducing the risk of errors and speeding up the setup process.
- **Output file parsing**: Easily read, analyze, and process data from Zacros output files.
- **Pressure and temperature scans**: Run scans over different pressures and temperatures and easily create heatmap plots with the results.
- **Documentation and examples**: Extensive documentation is available, including detailed examples to help users quickly get started and make the most of ZacrosTools.

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/tof_heatmap.png?raw=true" alt="TOF heatmap" width="500"/> </div>

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

- **[Gas Model](gas_model.md)**: Learn how to define the gas-phase molecular data.
- **[Energetics Model](energetics_model.md)**: Define all the terms used in the cluster expansion.
- **[Reaction Model](reaction_model.md)**: Specify the elementary steps included in the reaction mechanism.
- **[Lattice Model](lattice_model.md)**: Understand how to set up a lattice model.
- **[Writing_input_files](writing_input_files.md)**: Integrate all components into a KMC model and write the Zacros input files.
- **[Reading output files](reading_output_files.md)**: Parse and analyze data from Zacros output files.
- **[Plotting results](plotting_results.md)**: Visualize simulation results using simple plots or heatmaps.
- **[API reference](api_reference.md)**: Detailed API documentation for ZacrosTools modules and classes.

## Recent changes

### [2.1] 27-Nov-2024

#### Added
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

#### Changed
- **Building a `KMCModel`**: the `KMCModel` construction process now requires a `GasModel`, an `EnergeticsModel`, a `ReactionModel`, and a `LatticeModel`.

#### Improved
- **Output file parsing**: enhanced `parse_general_output` to support parsing `general_output.txt` files generated by Zacros version 2.x. 
- **Parameter validation**: improved the parsing and validation of selected parameters across all modules to prevent errors. 
- **Docstrings**: updated all docstrings to adhere to the NumPy format for better clarity and consistency.
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

- **Hector Prats** - [hector.pratsgarcia@chem.ox.ac.uk](mailto:hector.pratsgarcia@chem.ox.ac.uk)

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
   plotting_results.md
   api_reference.md
```
