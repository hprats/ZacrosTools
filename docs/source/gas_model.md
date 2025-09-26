# Gas model

## Overview

The `GasModel` contains the information about each gas-phase molecule involved in the simulation.

### Required columns

- **`type`** (`str`): Specifies whether the molecule is `'linear'`, `'non_linear'` or `'monoatomic'`.
- **`gas_energy`** (`float`): Formation energy in electronvolts (eV). Do not include the zero-point energy (ZPE).
- **`gas_molec_weight`** (`float`): Molecular weight in atomic mass units (amu).

### Required for 'linear' and 'non_linear' molecules

- **`sym_number`** (`int`): Symmetry number of the molecule (must be positive integer). Must be undefined/None for 'monoatomic'.
- **`inertia_moments`** (`list` of `float`): Moments of inertia in amu·Å².
  - Linear molecules: Provide 1 moment of inertia.
  - Non-linear molecules: Provide 3 moments of inertia.

### Optional column

- **`degeneracy`** (`int`): Degeneracy of the ground state, used in calculating the electronic partition function.
  - Default value: `1`.

### Example data table

| index | type    | gas_molec_weight | sym_number | degeneracy | inertia_moments            | gas_energy |
|-------|---------|------------------|------------|------------|----------------------------|------------|
| CO    | linear  | 28.01            | 1          | 1          | [8.973618976566065]        | 1.9544267  |
| O2    | linear  | 32.00            | 2          | 3          | [12.178373934770187]       | 2.6131292  |
| CO2   | linear  | 44.01            | 2          | 1          | [44.317204709218686]       | 0.00       |

---

## Creating a `GasModel`

There are several ways to create a `GasModel` instance:

1. **From a dictionary**
2. **From a CSV file**
3. **From a Pandas DataFrame**

### 1. From a dictionary

You can create a `GasModel` by providing a dictionary where each key is a species name and each value is a dictionary of properties.

#### Example

```python
from zacrostools.gas_model import GasModel

# Define the gas species data
species_data = {
    'CO': {
        'type': 'linear',
        'gas_molec_weight': 28.01,
        'sym_number': 1,
        'degeneracy': 1,
        'inertia_moments': [8.973618976566065],
        'gas_energy': 1.9544267
    },
    'O2': {
        'type': 'linear',
        'gas_molec_weight': 32.00,
        'sym_number': 2,
        'degeneracy': 3,
        'inertia_moments': [12.178373934770187],
        'gas_energy': 2.6131292
    },
    'CO2': {
        'type': 'linear',
        'gas_molec_weight': 44.01,
        'sym_number': 2,
        'degeneracy': 1,
        'inertia_moments': [44.317204709218686],
        'gas_energy': 0.00
    }
}

# Create the GasModel instance
gas_model = GasModel.from_dict(species_data)
```

### 2. From a CSV file

The CSV should have the required columns and use the species names as the index.

#### Example CSV (`gas_data.csv`)

```csv
,index,type,gas_molec_weight,sym_number,degeneracy,inertia_moments,gas_energy
CO,linear,28.01,1,1,"[8.973618976566065]",1.9544267
O2,linear,32.00,2,3,"[12.178373934770187]",2.6131292
CO2,linear,44.01,2,1,"[44.317204709218686]",0.00
```

#### Loading from CSV

```python
from zacrostools.gas_model import GasModel

# Create the GasModel instance from a CSV file
gas_model = GasModel.from_csv('gas_data.csv')
```

### 3. From a Pandas DataFrame

If you already have a DataFrame containing the gas species data, you can create a `GasModel` directly.

#### Example

```python
import pandas as pd
from zacrostools.gas_model import GasModel

# Create a DataFrame
data = {
    'type': ['linear', 'linear', 'linear'],
    'gas_molec_weight': [28.01, 32.00, 44.01],
    'sym_number': [1, 2, 2],
    'degeneracy': [1, 3, 1],
    'inertia_moments': [
        [8.973618976566065],
        [12.178373934770187],
        [44.317204709218686]
    ],
    'gas_energy': [1.9544267, 2.6131292, 0.00]
}
df = pd.DataFrame(data, index=['CO', 'O2', 'CO2'])

# Create the GasModel instance
gas_model = GasModel.from_df(df)
```

---

## Adding and removing species

You can modify an existing `GasModel` by adding or removing species.

### Adding a species

Use the `add_species` method to add a new species.

#### Example

```python
# Define the new species data
new_species = {
    'species_name': 'N2',
    'type': 'linear',
    'gas_molec_weight': 28.0134,
    'sym_number': 2,
    'degeneracy': 1,
    'inertia_moments': [10.822],
    'gas_energy': 0.00
}

# Add the species to the GasModel
gas_model.add_species(species_info=new_species)
```

### Removing species

Use the `remove_species` method to remove species by name.

#### Example

```python
# List of species to remove
species_to_remove = ['CO2']

# Remove species from the GasModel
gas_model.remove_species(species_to_remove)
```

---

## Accessing gas-phase data

The gas species data is stored internally as a Pandas DataFrame, accessible via the `df` attribute.

#### Example

```python
# View the gas species data
print(gas_model.df)
```

**Output:**

```
     type  gas_molec_weight  sym_number  degeneracy  \
CO  linear            28.010           1           1   
CO2 linear            44.010           2           1   

                     inertia_moments  gas_energy  
CO           [8.973618976566065]     1.9544267  
CO2         [44.317204709218686]     0.00  
```

---

## Full example

Below is a complete example demonstrating the creation and modification of a `GasModel`:

```python
from zacrostools.gas_model import GasModel

# Initial gas species data
species_data = {
    'CO': {
        'type': 'linear',
        'gas_molec_weight': 28.01,
        'sym_number': 1,
        'degeneracy': 1,
        'inertia_moments': [8.973618976566065],
        'gas_energy': 1.9544267
    },
    'O2': {
        'type': 'linear',
        'gas_molec_weight': 32.00,
        'sym_number': 2,
        'degeneracy': 3,
        'inertia_moments': [12.178373934770187],
        'gas_energy': 2.6131292
    }
}

# Create the GasModel instance
gas_model = GasModel.from_dict(species_data)

# Add a new species
gas_model.add_species(species_info={
    'species_name': 'CO2',
    'type': 'linear',
    'gas_molec_weight': 44.01,
    'sym_number': 2,
    'degeneracy': 1,
    'inertia_moments': [44.317204709218686],
    'gas_energy': 0.00
})

# Remove an existing species
gas_model.remove_species(['O2'])

# Access the DataFrame
print(gas_model.df)
```

---

## Next steps

With the `GasModel` defined, you can proceed to:

- Define the `EnergeticsModel`
- Define the `ReactionModel`
- Create a `LatticeModel`
- Assemble the `KMCModel`

For detailed guidance on these steps, refer to the respective sections in the documentation.