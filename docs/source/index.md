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
- **Quickly read, analyze, and process Zacros output files**
- **Perform scans over different pressures and temperatures**
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

### Version 2.10 — 2025-11-03

#### Changed
- **Redefined relative ∆TOF calculation in `dtof.py`**:  
  - The `difference_type='relative'` mode now computes |TOF(main) / TOF(ref)| instead of the previous fractional form (TOF(main) - TOF(ref)) / |TOF(ref)|
  - The colorbar for relative ∆TOF is now **logarithmic by default**, centered at **10⁰ (ratio = 1)**.  
  - The range automatically adapts to the nearest order of magnitude of the data (e.g., from 10⁻² to 10²).  
    - Users may still specify `max_dtof` to manually set the range; the colorbar will then span `[10^{-N}, 10^{+N}]`, where `10^N` is the closest power of ten to the given value.  
  - When using `difference_type='relative'`, the `scale` parameter is automatically forced to `'log'`.  
- **Improved automatic titles in heatmaps:**:  
  - In `heatmaps.time`, `auto_title=True` now omits units from the title.
  - In `heatmaps.coverage` and `heatmaps.phasediagram`, `auto_title=True` now omits the site type name if a default lattice is used. 
  
#### Removed
- **Deprecated `percent` parameter**:  
  - The `percent` keyword is **no longer supported** in `plot_dtof()`.

### Version 2.9 — 2025-10-07

#### Fixed
- **Missing heatmaps subpackage in PyPI builds**: The `zacrostools.heatmaps` folder is now correctly included in the package distribution.  
  - Added an `__init__.py` file to ensure it is recognized as a subpackage.  
  - Users can now successfully import plotting functions such as:
    ```python
    from zacrostools.heatmaps.tof import plot_tof
    from zacrostools.heatmaps.coverage import plot_coverage
    from zacrostools.heatmaps.phasediagram import plot_phasediagram
    ```
  - This fix ensures compatibility when installing ZacrosTools via `pip` or from PyPI.

### Version 2.8 — 2025-10-01

#### Added
- **Monoatomic gas species support**: `GasModel` now accepts a third `type` value: `"monoatomic"`.  
  - For monoatomics, rotational partition is treated as 1, so `sym_number` and `inertia_moments` may be **omitted or set to `None`**.  
  - CSVs that contain **only** monoatomic species no longer need `sym_number` or `inertia_moments` columns.  
  - Works seamlessly with `ReactionModel` and the updated partition/pre-exponential functions.

#### Changed
- **Fixed pre-exponential factors are now step-level fields**: Instead of passing `fixed_pre_expon` / `fixed_pe_ratio` to `ReactionModel.write_mechanism_input()`, define them **per step** (like other optional columns).  
  - New optional columns on each step:  
    - `fixed_pre_expon` (float): forward pre-exponential written as-is  
    - `fixed_pe_ratio` (float): ratio `pe_fwd/pe_rev` written as-is  
  - When provided together for a step, ZacrosTools **does not** apply manual scaling or graph multiplicity to that step’s pre-exponential.
  - Incompatibilities are enforced:
    - `stiffness_scalable_steps='all'` is not allowed if any step is fixed  
    - A fixed step cannot appear in `stiffness_scalable_steps`  
    - A fixed step cannot appear in `stiffness_scalable_symmetric_steps`
    
### Version 2.7 — 2025-09-25

#### Added
- **Fixed pre-exponential option**: Users can now fix the pre-exponential factor (`pre_expon`) and ratio (`pe_ratio`) of selected steps by providing `fixed_pre_expon` and `fixed_pe_ratio` dictionaries to `ReactionModel.write_mechanism_input()`. This bypasses automatic computation.  
  - Incompatible with `stiffness_scalable_steps='all'`.  
  - Incompatible with listing fixed steps in either `stiffness_scalable_steps` or `stiffness_scalable_symmetric_steps`.


Full details are available in the [ZacrosTools CHANGELOG](https://github.com/hprats/ZacrosTools/blob/main/CHANGELOG.md).

## What's next

We plan to continue improving ZacrosTools with additional features, optimizations, and support for more advanced Zacros functionalities. Contributions are welcome!

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
   gas_model.md
   energetics_model.md
   reaction_model.md
   lattice_model.md
   writing_input_files.md
   reading_output_files.md
   plotting_single_simulation.md
   plotting_heatmaps.md
```
