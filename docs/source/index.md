# Welcome to ZacrosTools Documentation

Welcome to the ZacrosTools documentation! This guide provides comprehensive information on using the ZacrosTools Python library.

ZacrosTools is a versatile toolkit designed to simplify the preparation and analysis of Kinetic Monte Carlo (KMC) simulations with **[Zacros](https://zacros.org/)**.

### Key Features:
- **User-friendly:** Simplifies the creation, execution, and analysis of Zacros simulations with intuitive Python functions and classes.
- **Automated Input Generation:** Generates Zacros input files for pressure or temperature scans, reducing the risk of errors and speeding up the setup process.
- **Result Analysis Tools:** Provides powerful tools for analyzing Zacros simulation outputs, including multiple plotting functions.
- **Extensibility:** Easily integrates with other Python libraries and tools, enabling seamless incorporation into broader computational workflows.
- **Documentation and Examples:** Extensive documentation is available, including detailed examples to help users quickly get started and make the most of ZacrosTools.

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/plot_multiple_runs/ScanTof.png?raw=true" alt="ScanTof" width="400"/>
</div>

### Recent Changes [1.01] - 13-Oct-2024

#### Version 1.01 - 13-Oct-2024
- *ZacrosTools* is now compatible with multidentate species.
- *ZacrosTools* is now compatible with default lattices.
- Bug fix for cases where vibrational energies of 0.0 are specified in the reaction model.
- Improved the [ZacrosTools Documentation](https://zacrostools.readthedocs.io/en/latest/).

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
