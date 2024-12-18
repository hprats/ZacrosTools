# Writing input files

## Creating a KMCModel

The `KMCModel` class represents the complete KMC simulation model for Zacros.
To create a `KMCModel`, you must first prepare and verify the individual components that comprise a complete KMC simulation setup:

1. **`GasModel`**: Contains gas-phase species definitions, including their molecular weights and energies.
2. **`ReactionModel`**: Details elementary reaction steps, including initial/final states, activation energies, and vibrational energies.
3. **`EnergeticsModel`**: Lists clusters and their energies, reflecting the cluster expansion used for energy calculations.
4. **`LatticeModel`**: Describes the lattice structure, site types, and spatial arrangement of sites.

Once you have these models, you can pass them into the `KMCModel`. The `KMCModel` constructor checks for data consistency—helping catch common issues (e.g., missing `site_types` definitions) early on.

### Example

```python
from zacrostools.kmc_model import KMCModel
from zacrostools.gas_model import GasModel
from zacrostools.reaction_model import ReactionModel
from zacrostools.energetics_model import EnergeticsModel
from zacrostools.lattice_model import LatticeModel

# Assume you have already prepared these data files
gas_model = GasModel.from_csv('gas_data.csv')
reaction_model = ReactionModel.from_csv('mechanism_data.csv')
energetics_model = EnergeticsModel.from_csv('energetics_data.csv')

# Define a lattice model
lattice_model = LatticeModel(
    lattice_type='periodic_cell',
    cell_vectors=((3.27, 0), (0, 3.27)),
    sites={'tC': (0.25, 0.25), 'tM': (0.75, 0.75)},
    copies=[10, 10],
    neighboring_structure='from_distances',
    max_distances={'tC-tC': 4.0, 'tC-tM': 4.0, 'tM-tM': 4.0},
)

# Create the KMCModel instance, integrating all components
kmc_model = KMCModel(
    gas_model=gas_model,
    reaction_model=reaction_model,
    energetics_model=energetics_model,
    lattice_model=lattice_model
)
```

This integrated `kmc_model` now holds a complete configuration of the KMC simulation, ready for input file generation.

---

## Writing the input files

Once the `KMCModel` is created, you can generate the Zacros input files by calling the `create_job_dir` method. This method writes all required input files into a specified directory:

- **`simulation_input.dat`**: Defines global simulation parameters (temperature, pressure, reporting frequencies, stopping criteria, and optional stiffness scaling parameters).
- **`energetics_input.dat`**: Lists clusters and their corresponding energies from the `EnergeticsModel`.
- **`mechanism_input.dat`**: Specifies the elementary reaction steps, their activation energies, and vibrational energies from the `ReactionModel`.
- **`lattice_input.dat`**: Outlines the lattice configuration, as defined in the `LatticeModel`.

### Parameters

- **`job_path`** (`str`): Directory where the input files will be written.
- **`temperature`** (`float` or `int`): Simulation temperature in Kelvin.
- **`pressure`** (`dict`): Partial pressures of gas species in bar, e.g., `{'CO': 1.0, 'O2': 0.001}`.
- **`reporting_scheme`** (`dict`, optional): Controls how often Zacros writes snapshots, process statistics, and species counts.
- **`stopping_criteria`** (`dict`, optional): Conditions to end the simulation (max steps, max time, wall time).
- **`manual_scaling`** (`dict`, optional): Apply scaling factors to specific reaction steps.
- **`stiffness_scaling_algorithm`** (`str`, optional): Algorithm for handling stiffness scaling (`'legacy'` or `'prats2024'`).
- **`stiffness_scalable_steps`** and **`stiffness_scalable_symmetric_steps`** (`list` of `str`, optional): Steps that can be dynamically scaled in Zacros to handle stiffness.
- **`stiffness_scaling_tags`** (`dict`, optional): Parameters controlling the dynamic scaling algorithm.
- **`sig_figs_energies`** (`int`, optional): Significant figures for energies written to input files.
- **`sig_figs_pe`** (`int`, optional): Significant figures for pre-exponential factors.
- **`random_seed`** (`int`, optional): Seed for Zacros's random number generator.

These parameters can be tailored to suit your simulation needs, ensuring that the generated files are both accurate and easy to reproduce.

### Example for a single KMC simulation

```python
kmc_model.create_job_dir(
    job_path='kmc_simulation',
    temperature=1000.0,
    pressure={'CO': 1.0, 'O2': 0.001, 'CO2': 0.0},
    reporting_scheme={
      'snapshots': 'on event 10000', 
      'process_statistics': 'on event 10000', 
      'species_numbers': 'on event 10000'},
    stopping_criteria={
      'max_steps': 'infinity', 
      'max_time': 'infinity', 
      'wall_time': 86400},
    manual_scaling={
      'CO_diffusion': 1.0e-1, 
      'O_diffusion': 1.0e-2},
    stiffness_scaling_algorithm=None,
    sig_figs_energies=8,
    sig_figs_pe=8,
)
```

The specified directory (`kmc_simulation`) will be created, containing all four Zacros input files.

### Looping over pressure and temperature values

This example automates the creation of multiple sets of input files across a parameter grid, enabling high-throughput studies of reaction conditions.

```python
import numpy as np

for pX in np.logspace(-4, 0, 10):
    for pY in np.logspace(-4, 0, 10):
        kmc_model.create_job_dir(
            job_path=f'pressure_scan/CO_{pX:.3e}#O2_{pY:.3e}',
            temperature=1000,
            pressure={'CO': pX, 'O2': pY, 'CO2': 0.0},
            reporting_scheme={'snapshots': 'on event 10000', 
                              'process_statistics': 'on event 10000', 
                              'species_numbers': 'on event 10000'},
            stopping_criteria={'max_steps': 'infinity', 
                               'max_time': 'infinity', 
                               'wall_time': 86400},
            manual_scaling={'CO_diffusion': 1.0e-1, 
                            'O_diffusion': 1.0e-2},
            sig_figs_energies=3,
            sig_figs_pe=3
        )
```
---

## Next steps

Once your input files are generated, you can:

- **Run the Zacros simulation** using the generated input files.
- **Parse and analyze the output data**, extracting information about reaction rates, coverages, and production profiles.
- **Visualize results**, creating plots or heatmaps to understand trends and identify optimal conditions.

For more details on analyzing and visualizing results, consult the corresponding sections of the documentation.
