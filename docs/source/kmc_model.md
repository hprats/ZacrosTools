# KMC Model

The `KMCModel` class in ZacrosTools represents the complete Kinetic Monte Carlo (KMC) simulation model for Zacros. It integrates the gas-phase species, reactions, energetics, and lattice configurations into a cohesive model that can generate all necessary input files for Zacros simulations. By encapsulating all aspects of the simulation setup, the `KMCModel` simplifies the process of preparing and running KMC simulations.

## Overview

The `KMCModel` combines the following components:

- **`GasModel`**: Defines gas-phase species involved in the simulation.
- **`ReactionModel`**: Specifies the reaction mechanism, including reaction steps and kinetics.
- **`EnergeticsModel`**: Provides cluster formation energies and configurations for surface species.
- **`LatticeModel`**: Describes the lattice structure on which the simulation runs.

By integrating these components, the `KMCModel` can generate all required input files for Zacros:

- `simulation_input.dat`
- `mechanism_input.dat`
- `energetics_input.dat`
- `lattice_input.dat`

---

## Creating a KMCModel

To create a `KMCModel`, you need to have instances of the four component models:

1. **`GasModel`**
2. **`ReactionModel`**
3. **`EnergeticsModel`**
4. **`LatticeModel`**

### Example

```python
from zacrostools.kmc_model import KMCModel
from zacrostools.gas_model import GasModel
from zacrostools.reaction_model import ReactionModel
from zacrostools.energetics_model import EnergeticsModel
from zacrostools.lattice_model import LatticeModel

# Assume gas_model, reaction_model, energetics_model, and lattice_model are already defined
gas_model = GasModel.from_csv('gas_data.csv')
reaction_model = ReactionModel.from_csv('mechanism_data.csv')
energetics_model = EnergeticsModel.from_csv('energetics_data.csv')
lattice_model = LatticeModel(
    lattice_type='periodic_cell',
    cell_vectors=((2.5, 0.0), (0.0, 2.5)),
    sites={
        'A': [(0.0, 0.0)],
        'B': [(0.5, 0.5)]
    },
    coordinate_type='direct',
    copies=[10, 10],
    neighboring_structure='from_distances',
    max_distances={
        'A-A': 3.0,
        'A-B': 3.0,
        'B-B': 3.0
    }
)

# Create the KMCModel instance
kmc_model = KMCModel(
    gas_model=gas_model,
    reaction_model=reaction_model,
    energetics_model=energetics_model,
    lattice_model=lattice_model
)
```

---

## Creating the Job Directory

The `KMCModel` provides the `create_job_dir` method to generate a job directory containing all necessary input files for Zacros. This method writes the following files:

- `simulation_input.dat`
- `mechanism_input.dat`
- `energetics_input.dat`
- `lattice_input.dat`

### Method

```python
kmc_model.create_job_dir(
    job_path,
    temperature,
    pressure,
    reporting_scheme=None,
    stopping_criteria=None,
    manual_scaling=None,
    stiffness_scaling_algorithm=None,
    stiffness_scalable_steps=None,
    stiffness_scalable_symmetric_steps=None,
    stiffness_scaling_tags=None,
    sig_figs_energies=8,
    sig_figs_pe=8,
    random_seed=None
)
```

#### Parameters

- **`job_path`** (`str`): The path for the job directory where input files will be written.
- **`temperature`** (`float` or `int`): Reaction temperature in Kelvin.
- **`pressure`** (`dict`): Partial pressures of gas species in bar, e.g., `{'CO': 1.0, 'O2': 0.001}`.
- **`reporting_scheme`** (`dict`, optional): Controls the reporting frequency of snapshots, process statistics, and species numbers.
  - Default:
    ```python
    {
        'snapshots': 'on event 10000',
        'process_statistics': 'on event 10000',
        'species_numbers': 'on event 10000'
    }
    ```
- **`stopping_criteria`** (`dict`, optional): Criteria for ending the simulation.
  - Default:
    ```python
    {
        'max_steps': 'infinity',
        'max_time': 'infinity',
        'wall_time': 86400  # in seconds
    }
    ```
- **`manual_scaling`** (`dict`, optional): Manual scaling factors for specific reaction steps.
- **`stiffness_scaling_algorithm`** (`str`, optional): Algorithm for stiffness scaling (`'legacy'` or `'prats2024'`).
- **`stiffness_scalable_steps`** (`list` of `str`, optional): Steps marked as `stiffness_scalable`.
- **`stiffness_scalable_symmetric_steps`** (`list` of `str`, optional): Steps marked as `stiffness_scalable_symmetric`.
- **`stiffness_scaling_tags`** (`dict`, optional): Parameters controlling the dynamic scaling algorithm.
- **`sig_figs_energies`** (`int`, optional): Significant figures for energies in input files.
- **`sig_figs_pe`** (`int`, optional): Significant figures for pre-exponential factors.
- **`random_seed`** (`int`, optional): Seed for the random number generator.

### Example

```python
# Define pressure in bar
pressure = {'CO': 1.0, 'O2': 0.001}

# Create the job directory
kmc_model.create_job_dir(
    job_path='kmc_simulation',
    temperature=500,
    pressure=pressure,
    manual_scaling={'CO_diffusion': 1.0e-1},
    stiffness_scalable_steps=['CO_diffusion'],
    random_seed=123456
)
```

This will create a directory named `kmc_simulation` containing all necessary input files.

---

## Generated Input Files

### 1. `simulation_input.dat`

Contains global simulation settings, including temperature, pressure, gas species, and reporting schemes.

### 2. `mechanism_input.dat`

Defines the reaction mechanism, including reaction steps, pre-exponential factors, and activation energies.

### 3. `energetics_input.dat`

Provides cluster definitions and formation energies for surface species.

### 4. `lattice_input.dat`

Describes the lattice structure, including site positions and neighboring structures.

---

## Additional Methods

### Checking for Errors

The `KMCModel` automatically checks for inconsistencies in the model configurations upon initialization.

```python
def check_errors(self):
    # Checks for data consistency after initialization
```

### Getting Surface Species

Extracts surface species names and their dentates from the `EnergeticsModel`.

```python
def get_surf_specs(self):
    # Returns a dictionary of surface species names and their dentates
```

---

## Full Example

Below is a complete example demonstrating how to set up and run a KMC simulation using the `KMCModel`.

```python
from zacrostools.kmc_model import KMCModel
from zacrostools.gas_model import GasModel
from zacrostools.reaction_model import ReactionModel
from zacrostools.energetics_model import EnergeticsModel
from zacrostools.lattice_model import LatticeModel

# Define gas model
gas_model = GasModel.from_dict({
    'CO': {
        'type': 'linear',
        'gas_molec_weight': 28.01,
        'sym_number': 1,
        'degeneracy': 1,
        'inertia_moments': [8.9736],
        'gas_energy': -1.16
    },
    'O2': {
        'type': 'linear',
        'gas_molec_weight': 32.00,
        'sym_number': 2,
        'degeneracy': 3,
        'inertia_moments': [12.1784],
        'gas_energy': 0.00
    }
})

# Define energetics model
energetics_model = EnergeticsModel.from_dict({
    'CO_ads': {
        'cluster_eng': -1.50,
        'site_types': '1',
        'lattice_state': ['1 CO* 1']
    },
    'O_ads': {
        'cluster_eng': -2.00,
        'site_types': '1',
        'lattice_state': ['1 O* 1']
    }
})

# Define reaction model
reaction_model = ReactionModel.from_dict({
    'CO_adsorption': {
        'site_types': '1',
        'initial': ['1 * 1'],
        'final': ['1 CO* 1'],
        'activ_eng': 0.00,
        'vib_energies_is': [100, 200],
        'vib_energies_fs': [150, 250],
        'vib_energies_ts': [],
        'molecule': 'CO',
        'area_site': 6.0
    },
    'CO_desorption': {
        'site_types': '1',
        'initial': ['1 CO* 1'],
        'final': ['1 * 1'],
        'activ_eng': 1.20,
        'vib_energies_is': [150, 250],
        'vib_energies_fs': [100, 200],
        'vib_energies_ts': [125, 225],
        'molecule': 'CO',
        'area_site': 6.0
    }
})

# Define lattice model
lattice_model = LatticeModel(
    lattice_type='default_choice',
    default_lattice_type='triangular_periodic',
    lattice_constant=2.5,
    copies=[20, 20]
)

# Create the KMCModel instance
kmc_model = KMCModel(
    gas_model=gas_model,
    reaction_model=reaction_model,
    energetics_model=energetics_model,
    lattice_model=lattice_model
)

# Define pressure in bar
pressure = {'CO': 1.0, 'O2': 0.001}

# Create the job directory
kmc_model.create_job_dir(
    job_path='kmc_simulation',
    temperature=500,
    pressure=pressure,
    random_seed=123456
)
```

---

## Additional Notes

- **Stiffness Scaling**:
  - **`stiffness_scaling_algorithm`** can be set to `'legacy'` or `'prats2024'` to enable dynamic stiffness scaling.
  - **`stiffness_scalable_steps`** and **`stiffness_scalable_symmetric_steps`** allow you to specify which reaction steps are subject to stiffness scaling.
  - **`stiffness_scaling_tags`** provides additional control over the dynamic scaling algorithm.

- **Manual Scaling**:
  - **`manual_scaling`** allows you to adjust the pre-exponential factors of specific steps manually.

- **Random Seed**:
  - By specifying a **`random_seed`**, you ensure reproducibility of stochastic simulations.

---

## Next Steps

With the job directory created, you can proceed to:

- **Run the Zacros Simulation**: Execute Zacros using the generated input files.
- **Analyze Simulation Results**: Use ZacrosTools or other analysis tools to interpret the simulation outputs.

For detailed guidance on running simulations and analyzing results, refer to the respective sections in the documentation.

---

**Note:** The `KMCModel` provides a high-level interface to set up complex KMC simulations with ease. By integrating all components and automating input file generation, it streamlines the simulation workflow, allowing you to focus on analyzing and interpreting the results.

---

This concludes the documentation for the `KMCModel`. By following the examples and guidelines provided, you should be able to set up and run your own KMC simulations using ZacrosTools.