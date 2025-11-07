# 5. Assembling the KMC Model and Writing the Input Files

The `KMCModel` class represents the complete KMC simulation model for Zacros.

#### Properties

1. **`GasModel`**: Contains gas-phase species definitions, including their molecular weights and energies.
2. **`ReactionModel`**: Details elementary reaction steps, including initial/final states, activation energies, and vibrational energies.
3. **`EnergeticsModel`**: Lists clusters and their energies, reflecting the cluster expansion used for energy calculations.
4. **`LatticeModel`**: Describes the lattice structure, site types, and spatial arrangement of sites.

#### How to create the KMC Model

Create it in the same way as shown in the example below.

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

---

#### Writing the input files

Once the `KMCModel` is created, you can generate the Zacros input files by calling the `create_job_dir` method. 

Required parameters:
- **`job_path`** (`str`): Directory where the input files will be written.
- **`temperature`** (`float` or `int`): Simulation temperature in Kelvin.
- **`pressure`** (`dict`): Partial pressures of gas species in bar, e.g., `{'CO': 1.0, 'O2': 0.001}`.
- **`reporting_scheme`** (`dict`, *optional*): Controls how often Zacros writes snapshots, process statistics, and species counts.
- **`stopping_criteria`** (`dict`, *optional*): Conditions to end the simulation (max steps, max time, wall time).
- **`manual_scaling`** (`dict`, *optional*): Apply scaling factors to specific reaction steps.
- **`stiffness_scaling_algorithm`** (`str`, *optional*): Algorithm for handling stiffness scaling (`'legacy'` or `'prats2024'`).
- **`stiffness_scalable_steps`** (`list` of `str`, *optional*): Steps that will be marked as `'stiffness_scalable'` in mechanism_input.dat. Can be provided as a list of step names or the string `'all'` to indicate that all steps
            (except those specified in `stiffness_scalable_symmetric_steps) are stiffness scalable.
- **`stiffness_scalable_symmetric_steps`**: (`list` of `str`, *optional*): Steps that will be marked as `'stiffness_scalable_symmetric'` in `mechanism_input.dat`
- **`stiffness_scaling_tags`** (`dict`, *optional*): Parameters controlling the dynamic scaling algorithm.
- **`sig_figs_energies`** (`int`, *optional*): Significant figures for energies written to input files.
- **`sig_figs_pe`** (`int`, *optional*): Significant figures for pre-exponential factors.
- **`sig_figs_lattice`** (`int`, *optional*): Significant figures for coordinates.
- **`random_seed`** (`int`, *optional*): Seed for Zacros's random number generator.
- **`version`** (`float` or `int`, *optional*): The Zacros version. Can be a single integer (e.g. 4) or float (e.g. 4.2 or 5.1). Default is 5.0.

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

#### Looping over pressure and temperature values

```python
for temperature in [600, 700, 800]: # in K
    for pCO in [0.01, 0.1, 1.0, 10]:  # in bar
        for pO2 in [0.01, 0.1, 1.0, 10]:  # in bar
            kmc_model.create_job_dir(
                job_path=f'temp_{temperature}K_pCO_{pCO}bar_pO2_{pO2}bar',
                temperature=temperature,
                pressure={'CO': pCO, 'O2': pO2, 'CO2': 0.0},
                reporting_scheme={
                    'snapshots': 'on event 100000',
                    'process_statistics': 'on event 100000',
                    'species_numbers': 'on event 100000'},
                stopping_criteria={
                    'max_steps': 'infinity',
                    'max_time': 5.0e+06,
                    'wall_time': 250000}
            )
```
---
