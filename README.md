<header style="text-align: center; padding: 20px;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/logo_without_background.png?raw=true" alt="ZacrosTools Logo" width="200"/>
</header>

# ZacrosTools

[![PyPI](https://img.shields.io/pypi/v/zacrostools)](https://pypi.org/project/zacrostools/)
[![License](https://img.shields.io/github/license/hprats/ZacrosTools)](https://github.com/hprats/ZacrosTools/blob/main/LICENSE)
[![CI](https://github.com/hprats/ZacrosTools/actions/workflows/ci.yml/badge.svg)](https://github.com/hprats/ZacrosTools/actions/workflows/ci.yml)

ZacrosTools is a versatile toolkit designed to simplify the preparation of **[Zacros](https://zacros.org/)** input files and the reading of Zacros output files. It is especially useful for performing pressure and temperature scans, which often require the generation of numerous input files and the processing of extensive output data.

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/examples/DRM_on_PtHfC/multiple_heatmaps.png?raw=true" alt="Multiple heatmaps" width="900"/> </div>

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Installing from Source](#installing-from-source)
- [Documentation](#documentation)
- [Changelog](#changelog)
- [Contributing](#contributing)
- [License](#license)
- [Contributors](#contributors)

## Key Features

- **Automatic input file generation**: Simplify the creation of Zacros input files, reducing the risk of errors and speeding up the setup process.
- **Output file parsing**: Easily read, analyze and process data from Zacros output files.
- **Pressure and temperature scans**: Streamline the process of performing scans over different pressures and temperatures.
- **Documentation and examples:** Extensive documentation is available, including detailed examples to help users quickly get started and make the most of ZacrosTools.

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

## Documentation

Comprehensive documentation is available at [zacrostools.readthedocs.io](https://zacrostools.readthedocs.io/en/latest/).

## Changelog

You can view the full list of changes in [CHANGELOG.md](./CHANGELOG.md).

## Contributing

Contributions are welcome!

- **Report Bugs**: Use the [issue tracker](https://github.com/hprats/ZacrosTools/issues) to report bugs.
- **Request Features**: Suggest new features or improvements.
- **Submit Pull Requests**: Fork the repository and submit pull requests for your contributions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributors

- **Hector Prats** - [hector.prats@tuwien.ac.at](mailto:hector.prats@tuwien.ac.at)