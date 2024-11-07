# Welcome to ZacrosTools Documentation

[![PyPI](https://img.shields.io/pypi/v/zacrostools)](https://pypi.org/project/zacrostools/)
[![License](https://img.shields.io/github/license/hprats/ZacrosTools)](https://github.com/hprats/ZacrosTools/blob/main/LICENSE)
[![CI](https://github.com/hprats/ZacrosTools/actions/workflows/ci.yml/badge.svg)](https://github.com/hprats/ZacrosTools/actions/workflows/ci.yml)

Welcome to the ZacrosTools documentation! This guide provides comprehensive information on using the ZacrosTools Python library.

ZacrosTools is a versatile toolkit designed to simplify the preparation and analysis of Kinetic Monte Carlo (KMC) simulations with **[Zacros](https://zacros.org/)**.

## Table of Contents

- [Key Features](#key-features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Installing from Source](#installing-from-source)
- [Quick Start Guide](#quick-start-guide)
- [Recent Changes](#recent-changes)
- [What's Next](#whats-next)
- [Documentation](#documentation)
- [Contributors](#contributors)

## Key Features

- **Automatic Input File Generation**: Simplify the creation of Zacros input files, reducing the risk of errors and speeding up the setup process.
- **Output File Parsing**: Easily read, analyze, and process data from Zacros output files.
- **Pressure and Temperature Scans**: Streamline the process of performing scans over different pressures and temperatures.
- **Customizable Workflows**: Create customized workflows to fit specific simulation needs.
- **Documentation and Examples**: Extensive documentation is available, including detailed examples to help users quickly get started and make the most of ZacrosTools.

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributors

- **Hector Prats** - [hector.pratsgarcia@chem.ox.ac.uk](mailto:hector.pratsgarcia@chem.ox.ac.uk)

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
```
