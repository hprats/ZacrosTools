<header style="text-align: center; padding: 20px;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/logo_without_background.png?raw=true" alt="ZacrosTools Logo" width="200"/>
</header>

# Welcome to the ZacrosTools documentation

[![PyPI](https://img.shields.io/pypi/v/zacrostools)](https://pypi.org/project/zacrostools/)
[![License](https://img.shields.io/github/license/hprats/ZacrosTools)](https://github.com/hprats/ZacrosTools/blob/main/LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.1021/acs.jpca.5c02802.svg)](https://doi.org/10.1021/acs.jpca.5c02802)
[![CI](https://github.com/hprats/ZacrosTools/actions/workflows/ci.yml/badge.svg)](https://github.com/hprats/ZacrosTools/actions/workflows/ci.yml)

ZacrosTools is a versatile toolkit designed to simplify the preparation and analysis of Kinetic Monte Carlo (KMC) simulations with **[Zacros](https://zacros.org/)**.

## Key features 

- **Automatize the creation of Zacros input files**
- **Perform scans over different pressures and temperatures**
- **Quickly read, analyze, and process Zacros output files**
- **Easily plot heatmaps from the simulation results**
- **Extensive documentation with detailed examples to help users get started**

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/multiple_heatmaps.png?raw=true" alt="Multiple heatmaps" width="700"/> </div>

## How to cite

If you use **ZacrosTools** in your research, please cite:

> Prats, H. ZacrosTools: A Python Library for Automated Preparation, Analysis, and Visualization of Kinetic Monte Carlo Simulations with Zacros. *J. Phys. Chem. A* **2025**, *129*, 6608–6614. DOI: [10.1021/acs.jpca.5c02802](https://doi.org/10.1021/acs.jpca.5c02802)


## Installation 

ZacrosTools is available on PyPI and can be installed using `pip`:

```bash
pip install zacrostools
```

Prerequisites:
- **Python 3.8 or higher**
- **[Scipy](https://scipy.org/)**
- **[Pandas](https://pandas.pydata.org/)**

Alternatively, the latest development version can be installed from GitHub as follows:

```bash
git clone https://github.com/hprats/ZacrosTools.git
cd ZacrosTools
pip install .
```

## Recent changes

### Version 2.12 — 2026-08-27

#### Added
- **Multiple gas-phase species per reaction side**: `ReactionModel` now accepts one or more whitespace-separated species in `molecule_is` and `molecule_fs`, e.g. `molecule_is='CO2 H2'`.
  - `gas_reacs_prods` is written with the corresponding stoichiometric coefficient for every species.
  - Repeated species are combined, and species appearing on both sides are assigned their net coefficient.
  - For steps with multiple gas reactants or products in one direction, `fixed_pre_expon` and `fixed_pe_ratio` must be supplied because automatic pre-exponential calculation remains limited to one gas species per direction.

#### Changed
- **Simplified fixed-rate reaction models**: Steps defining both `fixed_pre_expon` and `fixed_pe_ratio` no longer need to provide `vib_energies_is` or `vib_energies_fs`.
- **Stricter validation for calculated prefactors**: Non-fixed steps must provide non-empty `vib_energies_is` and `vib_energies_fs` lists.
- **Fixed-step scaling validation**: `ReactionModel` now raises an error if `manual_scaling` is applied to a step using fixed pre-exponential values.

#### Improved
- **Documentation and examples**: Updated the project overview and expanded the input-generation example to demonstrate scans over temperature and multiple gas pressures.

Full details are available in the [ZacrosTools CHANGELOG](https://github.com/hprats/ZacrosTools/blob/main/CHANGELOG.md).

## What's next

We plan to continue improving ZacrosTools with additional features, optimizations, and support for more advanced Zacros functionalities. Contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/hprats/ZacrosTools/blob/main/LICENSE) file for details.

## Contributors

- **Hector Prats** - [hpratsga@ub.edu](mailto:hpratsga@ub.edu)

## Acknowledgements

- **Zeyu Wu**: for testing the library and reporting bugs

```{eval-rst}
.. toctree::
   :maxdepth: 2
   :caption: Contents

   citation.md
   gas_model.md
   energetics_model.md
   reaction_model.md
   lattice_model.md
   writing_input_files.md
   reading_output_files.md
   plotting_single_simulation.md
   plotting_heatmaps.md
```
