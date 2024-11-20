# Reaction Model

The `ReactionModel` class in ZacrosTools represents the reaction mechanism for Kinetic Monte Carlo (KMC) simulations using Zacros. It allows you to define adsorption, desorption, surface reactions, and diffusion steps, including all necessary parameters such as activation energies and vibrational frequencies. This class integrates with the `GasModel` to ensure consistency between gas-phase species and reactions.

## Overview

The `ReactionModel` requires detailed information about each reaction step, including the initial and final states, activation energies, and vibrational energies. It supports different types of reaction steps:

- **Non-activated adsorption**
- **Activated adsorption**
- **Surface reactions**

### Required Columns

- **`initial`** (`list` of `str`): Initial configuration in Zacros format (e.g., `['1 CO* 1', '2 * 1']`).
- **`final`** (`list` of `str`): Final configuration in Zacros format (e.g., `['1 C* 1', '2 O* 1']`).
- **`activ_eng`** (`float`): Activation energy in electronvolts (eV).
- **`vib_energies_is`** (`list` of `float`): Vibrational energies for the initial state in millielectronvolts (meV), excluding the zero-point energy (ZPE).
- **`vib_energies_fs`** (`list` of `float`): Vibrational energies for the final state in meV, excluding the ZPE.

### Additional Required Columns for Specific Steps

- **Adsorption Steps**:
  - **`molecule`** (`str`): Gas-phase molecule involved.
  - **`area_site`** (`float`): Area of the adsorption site in square angstroms (Å²).
- **Activated Steps** (e.g., activated adsorption, surface reactions):
  - **`vib_energies_ts`** (`list` of `float`): Vibrational energies for the transition state in meV, excluding the ZPE.

### Optional Columns

- **`site_types`** (`str`): Types of each site in the reaction pattern. Required if `lattice_type is 'periodic_cell'`.
- **`neighboring`** (`str`): Connectivity between sites involved (e.g., `'1-2'`).
- **`prox_factor`** (`float`): Proximity factor.
- **`angles`** (`str`): Angle constraints between sites in Zacros format (e.g., `'1-2-3:180'`).
- **`graph_multiplicity`** (`int` or `float`): Symmetry factor of the step. The computed pre-exponential factor will be divided by this value. Useful for symmetric steps like diffusion on equivalent sites.

### Example Data Table

| index              | site_types | initial                       | final                       | activ_eng | vib_energies_is      | vib_energies_fs      | molecule | area_site | vib_energies_ts    | neighboring | prox_factor | angles     | graph_multiplicity |
|--------------------|------------|-------------------------------|-----------------------------|-----------|----------------------|----------------------|----------|-----------|--------------------|-------------|-------------|------------|--------------------|
| CO_adsorption      | 1          | ['1 * 1']                     | ['1 CO* 1']                 | 0.00      | [100, 200]           | [150, 250]           | CO       | 6.0       | []                 | NaN         | NaN         | NaN        | NaN                |
| O2_dissociation    | 1 1        | ['1 O2* 1']                   | ['1 O* 1', '2 O* 1']        | 0.80      | [200, 300]           | [150, 250, 350, 450] | NaN      | NaN       | [250, 350, 450]    | 1-2         | NaN         | NaN        | 1                  |
| CO_diffusion       | 1 1        | ['1 CO* 1', '2 * 1']          | ['1 * 1', '2 CO* 1']        | 0.50      | [150, 250]           | [150, 250]           | NaN      | NaN       | [200, 300]         | 1-2         | NaN         | NaN        | 2                  |

---

## Creating a ReactionModel

You can create a `ReactionModel` instance in several ways:

1. **From a Dictionary**
2. **From a CSV File**
3. **From a Pandas DataFrame**

### 1. From a Dictionary

Provide a dictionary where each key is a reaction step name and each value is a dictionary of step properties.

#### Example

```python
from zacrostools.reaction_model import ReactionModel

# Define the reaction steps data
steps_data = {
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
    'O2_dissociation': {
        'site_types': '1 1',
        'initial': ['1 O2* 1'],
        'final': ['1 O* 1', '2 O* 1'],
        'activ_eng': 0.80,
        'vib_energies_is': [200, 300],
        'vib_energies_fs': [150, 250, 350, 450],
        'vib_energies_ts': [250, 350, 450],
        'neighboring': '1-2'
    },
    'CO_diffusion': {
        'site_types': '1 1',
        'initial': ['1 CO* 1', '2 * 1'],
        'final': ['1 * 1', '2 CO* 1'],
        'activ_eng': 0.50,
        'vib_energies_is': [150, 250],
        'vib_energies_fs': [150, 250],
        'vib_energies_ts': [200, 300],
        'neighboring': '1-2',
        'graph_multiplicity': 2
    }
}

# Create the ReactionModel instance
reaction_model = ReactionModel.from_dict(steps_data)
```

### 2. From a CSV File

Load reaction steps data from a CSV file. The CSV should have the required columns and use the reaction step names as the index.

#### Example CSV (`mechanism_data.csv`)

```csv
,index,site_types,initial,final,activ_eng,vib_energies_is,vib_energies_fs,molecule,area_site,vib_energies_ts,neighboring,prox_factor,angles,graph_multiplicity
CO_adsorption,1,"['1 * 1']","['1 CO* 1']",0.00,"[100, 200]","[150, 250]",CO,6.0,"[]",,,
O2_dissociation,"1 1","['1 O2* 1']","['1 O* 1', '2 O* 1']",0.80,"[200, 300]","[150, 250, 350, 450]",,,[250, 350, 450],"1-2",,,
CO_diffusion,"1 1","['1 CO* 1', '2 * 1']","['1 * 1', '2 CO* 1']",0.50,"[150, 250]","[150, 250]",,,[200, 300],"1-2",,,2
```

#### Loading from CSV

```python
from zacrostools.reaction_model import ReactionModel

# Create the ReactionModel instance from a CSV file
reaction_model = ReactionModel.from_csv('mechanism_data.csv')
```

### 3. From a Pandas DataFrame

If you have a DataFrame containing the reaction steps data, you can create a `ReactionModel` directly.

#### Example

```python
import pandas as pd
from zacrostools.reaction_model import ReactionModel

# Create a DataFrame
data = {
    'site_types': ['1', '1 1', '1 1'],
    'initial': [
        ['1 * 1'],
        ['1 O2* 1'],
        ['1 CO* 1', '2 * 1']
    ],
    'final': [
        ['1 CO* 1'],
        ['1 O* 1', '2 O* 1'],
        ['1 * 1', '2 CO* 1']
    ],
    'activ_eng': [0.00, 0.80, 0.50],
    'vib_energies_is': [
        [100, 200],
        [200, 300],
        [150, 250]
    ],
    'vib_energies_fs': [
        [150, 250],
        [150, 250, 350, 450],
        [150, 250]
    ],
    'vib_energies_ts': [
        [],
        [250, 350, 450],
        [200, 300]
    ],
    'molecule': ['CO', None, None],
    'area_site': [6.0, None, None],
    'neighboring': [None, '1-2', '1-2'],
    'graph_multiplicity': [None, None, 2]
}
df = pd.DataFrame(data, index=['CO_adsorption', 'O2_dissociation', 'CO_diffusion'])

# Create the ReactionModel instance
reaction_model = ReactionModel.from_df(df)
```

---

## Adding and Removing Steps

You can modify an existing `ReactionModel` by adding or removing reaction steps.

### Adding a Step

Use the `add_step` method to add a new reaction step.

#### Example

```python
# Define the new step data
new_step = {
    'step_name': 'CO_desorption',
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

# Add the step to the ReactionModel
reaction_model.add_step(step_info=new_step)
```

### Removing Steps

Use the `remove_steps` method to remove steps by name.

#### Example

```python
# List of steps to remove
steps_to_remove = ['O2_dissociation']

# Remove steps from the ReactionModel
reaction_model.remove_steps(steps_to_remove)
```

---

## Writing the Mechanism Input File

The `ReactionModel` can generate the `mechanism_input.dat` file required by Zacros.

### Method

```python
reaction_model.write_mechanism_input(
    output_dir,
    temperature,
    gas_model,
    manual_scaling=None,
    stiffness_scalable_steps=None,
    stiffness_scalable_symmetric_steps=None,
    sig_figs_energies=8,
    sig_figs_pe=8
)
```

- **`output_dir`** (`str` or `Path`): Directory where the file will be written.
- **`temperature`** (`float`): Temperature in Kelvin for pre-exponential calculations.
- **`gas_model`** (`GasModel`): Instance of `GasModel` containing gas-phase species data.
- **`manual_scaling`** (`dict`, optional): Dictionary of manual scaling factors per step.
- **`stiffness_scalable_steps`** (`list`, optional): List of steps that are stiffness scalable.
- **`stiffness_scalable_symmetric_steps`** (`list`, optional): List of steps that are stiffness scalable and symmetric.
- **`sig_figs_energies`** (`int`, optional): Number of significant figures for activation energies.
- **`sig_figs_pe`** (`int`, optional): Number of significant figures for pre-exponential factors.

#### Example

```python
from zacrostools.gas_model import GasModel

# Assume gas_model is already defined
gas_model = GasModel.from_csv('gas_data.csv')

# Define manual scaling factors (if any)
manual_scaling = {'CO_diffusion': 1.0e-1}

# Write the mechanism_input.dat file
reaction_model.write_mechanism_input(
    output_dir='kmc_simulation',
    temperature=500,
    gas_model=gas_model,
    manual_scaling=manual_scaling,
    stiffness_scalable_steps=['CO_diffusion'],
    sig_figs_energies=8,
    sig_figs_pe=8
)
```

---

## Accessing Reaction Data

The reaction steps data is stored internally as a Pandas DataFrame, accessible via the `df` attribute.

#### Example

```python
# View the reaction steps data
print(reaction_model.df)
```

**Output:**

```
                 site_types                            initial  \
CO_adsorption             1                       [1 * 1]   
CO_diffusion            1 1         [1 CO* 1, 2 * 1]   

                                       final  activ_eng vib_energies_is  \
CO_adsorption                   [1 CO* 1]         0.0     [100, 200]   
CO_diffusion       [1 * 1, 2 CO* 1]         0.5     [150, 250]   

               vib_energies_fs molecule area_site vib_energies_ts neighboring  \
CO_adsorption     [150, 250]       CO       6.0             []        None   
CO_diffusion      [150, 250]      None       NaN      [200, 300]        1-2   

               prox_factor angles graph_multiplicity  
CO_adsorption        None   None                NaN  
CO_diffusion         None   None                  2  
```

---

## Full Example

Below is a complete example demonstrating the creation and modification of a `ReactionModel`:

```python
from zacrostools.reaction_model import ReactionModel
from zacrostools.gas_model import GasModel

# Define gas model (assumed to be defined)
gas_model = GasModel.from_csv('gas_data.csv')

# Initial reaction steps data
steps_data = {
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
    'CO_diffusion': {
        'site_types': '1 1',
        'initial': ['1 CO* 1', '2 * 1'],
        'final': ['1 * 1', '2 CO* 1'],
        'activ_eng': 0.50,
        'vib_energies_is': [150, 250],
        'vib_energies_fs': [150, 250],
        'vib_energies_ts': [200, 300],
        'neighboring': '1-2',
        'graph_multiplicity': 2
    }
}

# Create the ReactionModel instance
reaction_model = ReactionModel.from_dict(steps_data)

# Add a new step
reaction_model.add_step(step_info={
    'step_name': 'CO_desorption',
    'site_types': '1',
    'initial': ['1 CO* 1'],
    'final': ['1 * 1'],
    'activ_eng': 1.20,
    'vib_energies_is': [150, 250],
    'vib_energies_fs': [100, 200],
    'vib_energies_ts': [125, 225],
    'molecule': 'CO',
    'area_site': 6.0
})

# Remove an existing step
reaction_model.remove_steps(['CO_diffusion'])

# Write the mechanism input file
reaction_model.write_mechanism_input(
    output_dir='kmc_simulation',
    temperature=500,
    gas_model=gas_model
)

# Access the DataFrame
print(reaction_model.df)
```

---

## Next Steps

With the `ReactionModel` defined, you can proceed to:

- **Define the Gas Model**: Specify gas-phase species using the `GasModel`.
- **Set Up the Energetics Model**: Provide cluster energetics with the `EnergeticsModel`.
- **Configure the Lattice Model**: Set up the simulation lattice using the `LatticeModel`.
- **Assemble the KMC Model**: Integrate all components into a `KMCModel` for simulation.

For detailed guidance on these steps, refer to the respective sections in the documentation.

---

## Additional Notes

- **Vibrational Energies**:
  - Provide vibrational energies in millielectronvolts (meV) without including the zero-point energy (ZPE).
  - Ensure that no vibrational energy is zero, as this can lead to calculation errors.

- **Activation Energies**:
  - Activation energies should be provided in electronvolts (eV).

- **Pre-exponential Factors**:
  - The `ReactionModel` calculates pre-exponential factors internally when writing the mechanism input file, based on the provided vibrational energies and temperature.

- **Graph Multiplicity**:
  - Used to account for symmetry in reaction steps.
  - The pre-exponential factor is divided by the `graph_multiplicity`.

- **Manual Scaling**:
  - You can manually scale the pre-exponential factors of specific steps using the `manual_scaling` dictionary.

---

By carefully defining the reaction model, you ensure that the KMC simulation accurately represents the reaction mechanisms and kinetics of the system, leading to reliable and meaningful simulation results.