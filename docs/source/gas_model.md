# 1. Create a Gas Model

## Overview

The `GasModel` contains the information about each gas-phase molecule involved in the simulation.

### Properties

- **`type`** (`str`): Molecular type — `'linear'`, `'non_linear'` or `'monoatomic'`.
- **`gas_energy`** (`float`): Formation energy (eV).
- **`gas_molec_weight`** (`float`): Molecular weight (amu).
- **`sym_number`** (`int`): Symmetry number (ignored for monoatomic species).
- **`inertia_moments`** (`list` of `float`): Moments of inertia (amu·Å²).
  - `'linear'`: 1 value required.
  - `'non_linear'`: 3 values required.
- **`degeneracy`** (`int`, *optional*): Ground-state degeneracy (default = 1).

## Creating a `GasModel`

There are several ways to create a `GasModel` instance:

1. **From a dictionary**
2. **From a CSV file**
3. **From a Pandas DataFrame**

### From a dictionary

You can create a `GasModel` by providing a dictionary where each key is a species name and each value is a dictionary of properties.

```python
from zacrostools.gas_model import GasModel

species_data = {
    'CO': {
        'type': 'linear',
        'gas_molec_weight': 28.01,
        'sym_number': 1,
        'degeneracy': 1,
        'inertia_moments': [8.973],
        'gas_energy': 1.954
    },
    'O2': {
        'type': 'linear',
        'gas_molec_weight': 32.00,
        'sym_number': 2,
        'degeneracy': 3,
        'inertia_moments': [12.178],
        'gas_energy': 2.613
    },
    'CO2': {
        'type': 'linear',
        'gas_molec_weight': 44.01,
        'sym_number': 2,
        'degeneracy': 1,
        'inertia_moments': [44.317],
        'gas_energy': 0.00
    }
}

gas_model = GasModel.from_dict(species_data)
```

### From a CSV file

The CSV should have the required columns and use the species names as the index.

```python
from zacrostools.gas_model import GasModel

gas_model = GasModel.from_csv('gas_data.csv')
```

### From a Pandas DataFrame

If you already have a DataFrame containing the gas species data, you can create a `GasModel` directly.

#### Example

```python
from zacrostools.gas_model import GasModel

gas_model = GasModel.from_df(df)
```

---

## Adding and removing species

You can modify an existing `GasModel` by adding or removing species.

Use the `add_species` method to add a new species.

```python
new_species = {
    'species_name': 'N2',
    'type': 'linear',
    'gas_molec_weight': 28.013,
    'sym_number': 2,
    'degeneracy': 1,
    'inertia_moments': [10.822],
    'gas_energy': 0.00
}
gas_model.add_species(species_info=new_species)
```

Use the `remove_species` method to remove species by name.

```python
gas_model.remove_species(['CO2'])
```

---

## Accessing gas-phase data

The gas species data is stored internally as a Pandas DataFrame, accessible via the `df` attribute.

```python
print(gas_model.df)
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
        'inertia_moments': [8.973],
        'gas_energy': 1.9544267
    },
    'O2': {
        'type': 'linear',
        'gas_molec_weight': 32.00,
        'sym_number': 2,
        'degeneracy': 3,
        'inertia_moments': [12.178],
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
    'inertia_moments': [44.317],
    'gas_energy': 0.00
})

# Remove an existing species
gas_model.remove_species(['O2'])

# Access the DataFrame
print(gas_model.df)
```

---