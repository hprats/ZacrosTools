<header style="text-align: center; padding: 20px;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/logo_without_background.png?raw=true" alt="ZacrosTools Logo" width="200"/>
</header>

# Welcome to the ZacrosTools documentation

[![PyPI](https://img.shields.io/pypi/v/zacrostools)](https://pypi.org/project/zacrostools/)
[![License](https://img.shields.io/github/license/hprats/ZacrosTools)](https://github.com/hprats/ZacrosTools/blob/main/LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.1021/acs.jpca.5c02802.svg)](https://doi.org/10.1021/acs.jpca.5c02802)
[![CI](https://github.com/hprats/ZacrosTools/actions/workflows/ci.yml/badge.svg)](https://github.com/hprats/ZacrosTools/actions/workflows/ci.yml)

This guide provides comprehensive information on using the ZacrosTools Python library.

ZacrosTools is a versatile toolkit designed to simplify the preparation and analysis of Kinetic Monte Carlo (KMC) simulations with **[Zacros](https://zacros.org/)**.

## Key features 

- **Automatic input file generation**: Easily create Zacros input files, reducing errors.
- **Output file parsing**: Quickly read, analyze, and process Zacros output data.
- **Pressure and temperature scans**: Streamline the process of performing scans over different pressures and temperatures.
- **Documentation and examples:** Extensive documentation with detailed examples to help users get started and make full use of ZacrosTools.

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/multiple_heatmaps.png?raw=true" alt="Multiple heatmaps" width="700"/> </div>

## How to cite

If you use **ZacrosTools** in your research, please cite:

> Prats, H. ZacrosTools: A Python Library for Automated Preparation, Analysis, and Visualization of Kinetic Monte Carlo Simulations with Zacros. *J. Phys. Chem. A* **2025**, *129*, 6608–6614. DOI: [10.1021/acs.jpca.5c02802](https://doi.org/10.1021/acs.jpca.5c02802)


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

## [2.8] - 01-Oct-2025

### Added
- **Monoatomic gas species support**: `GasModel` now accepts a third `type` value: `"monoatomic"`.  
  - For monoatomics, rotational partition is treated as 1, so `sym_number` and `inertia_moments` may be **omitted or set to `None`**.  
  - CSVs that contain **only** monoatomic species no longer need `sym_number` or `inertia_moments` columns.  
  - Works seamlessly with `ReactionModel` and the updated partition/pre-exponential functions.

### Changed
- **Fixed pre-exponential factors are now step-level fields**: Instead of passing `fixed_pre_expon` / `fixed_pe_ratio` to `ReactionModel.write_mechanism_input()`, define them **per step** (like other optional columns).  
  - New optional columns on each step:  
    - `fixed_pre_expon` (float): forward pre-exponential written as-is  
    - `fixed_pe_ratio` (float): ratio `pe_fwd/pe_rev` written as-is  
  - When provided together for a step, ZacrosTools **does not** apply manual scaling or graph multiplicity to that step’s pre-exponential.
  - Incompatibilities are enforced:
    - `stiffness_scalable_steps='all'` is not allowed if any step is fixed  
    - A fixed step cannot appear in `stiffness_scalable_steps`  
    - A fixed step cannot appear in `stiffness_scalable_symmetric_steps`
    
## [2.7] - 25-Sep-2025

### Added
- **Fixed pre-exponential option**: Users can now fix the pre-exponential factor (`pre_expon`) and ratio (`pe_ratio`) of selected steps by providing `fixed_pre_expon` and `fixed_pe_ratio` dictionaries to `ReactionModel.write_mechanism_input()`. This bypasses automatic computation.  
  - Incompatible with `stiffness_scalable_steps='all'`.  
  - Incompatible with listing fixed steps in either `stiffness_scalable_steps` or `stiffness_scalable_symmetric_steps`.

## [2.6] - 24-Sep-2025

### Changed
- **Gas-phase molecule parameter update**: the deprecated `molecule` parameter has been replaced by two explicit parameters, `molecule_is` and `molecule_fs`, which indicate the presence of gas-phase species in the initial or final state of a step, respectively. Using `molecule` will trigger a `DeprecationWarning`.  

### Added
- **Bidirectional gas-phase step support**: ZacrosTools now accepts the definition of reaction steps involving gas-phase species in either direction (initial or final state). Previously, gas-phase species were only allowed in the initial state (adsorption).
  
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

   citation.md
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
