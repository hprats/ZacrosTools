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

### Recent Changes

#### Version 1.02 - 06-Nov-2024
- In `KMCModel.create_job_dir` method, parameter `auto_scaling_steps` has been renamed to `stiffness_scaling_steps`and 
parameter `auto_scaling_tags` has been renamed to `stiffness_scaling_tags`.
- Fixed bug where, if only one surface species was declared, `surf_specs_dent` would be an integer instead of a list.
- Fixed bug where the total pressure could be written as an integer, and then the simulation will crash.
- Now, ZacrosTools checks if the keywords provided in `stiffness_scaling_tags` are allowed.
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
