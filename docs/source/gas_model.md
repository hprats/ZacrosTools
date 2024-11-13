# Gas Model

The `GasModel` class in ZacrosTools is designed to represent gas-phase molecular data required for Kinetic Monte Carlo (KMC) reaction modeling using Zacros. It encapsulates all necessary properties of gas-phase species, ensuring consistency and facilitating integration with other models like `ReactionModel`.

## Overview

The `GasModel` requires information about each gas-phase molecule involved in the simulation. This information includes molecular weight, symmetry number, moments of inertia, and formation energy. Optionally, the degeneracy of the ground state can also be specified.

### Required Columns

- **`type`** (`str`): Specifies whether the molecule is `'linear'` or `'non_linear'`.
- **`gas_molec_weight`** (`float`): Molecular weight in atomic mass units (amu).
- **`sym_number`** (`int`): Symmetry number of the molecule.
- **`inertia_moments`** (`list` of `float`): Moments of inertia in amu·Å².
  - Linear molecules: Provide 1 moment of inertia.
  - Non-linear molecules: Provide 3 moments of inertia.
- **`gas_energy`** (`float`): Formation energy in electronvolts (eV). Do not include the zero-point energy (ZPE).

### Optional Column

- **`degeneracy`** (`int`): Degeneracy of the ground state, used in calculating the electronic partition function.
  - Default value: `1`.

### Example Data Table

| index | type       | gas_molec_weight | sym_number | degeneracy | inertia_moments             | gas_energy |
|-------|------------|------------------|------------|------------|-----------------------------|------------|
| CO    | linear     | 28.01            | 1          | 1          | [8.973619026272551]         | -1.16      |
| O2    | linear     | 32.00            | 2          | 3          | [12.178379354326061]        | 0.00       |
| CO2   | non_linear | 44.01            | 2          | 1          | [44.317229117708344,        | -3.94      |
|       |            |                  |            |            | 22.158614558854172,         |            |
|       |            |                  |            |            | 22.158614558854172]         |            |

---

## Creating a GasModel

There are several ways to create a `GasModel` instance:

1. **From a Dictionary**
2. **From a CSV File**
3. **From a Pandas DataFrame**

### 1. From a Dictionary

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
        'inertia_moments': [8.973619026272551],
        'gas_energy': -1.16
    },
    'O2': {
        'type': 'linear',
        'gas_molec_weight': 32.00,
        'sym_number': 2,
        'degeneracy': 3,
        'inertia_moments': [12.178379354326061],
        'gas_energy': 0.00
    },
    'CO2': {
        'type': 'non_linear',
        'gas_molec_weight': 44.01,
        'sym_number': 2,
        'degeneracy': 1,
        'inertia_moments': [44.317229117708344, 22.158614558854172, 22.158614558854172],
        'gas_energy': -3.94
    }
}

# Create the GasModel instance
gas_model = GasModel.from_dict(species_data)
```

### 2. From a CSV File

You can load gas-phase species data from a CSV file. The CSV should have the required columns and use the species names as the index.

#### Example CSV (`gas_data.csv`)

```csv
,index,type,gas_molec_weight,sym_number,degeneracy,inertia_moments,gas_energy
CO,linear,28.01,1,1,"[8.973619026272551]",-1.16
O2,linear,32.00,2,3,"[12.178379354326061]",0.00
CO2,non_linear,44.01,2,1,"[44.317229117708344, 22.158614558854172, 22.158614558854172]",-3.94
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
    'type': ['linear', 'linear', 'non_linear'],
    'gas_molec_weight': [28.01, 32.00, 44.01],
    'sym_number': [1, 2, 2],
    'degeneracy': [1, 3, 1],
    'inertia_moments': [
        [8.973619026272551],
        [12.178379354326061],
        [44.317229117708344, 22.158614558854172, 22.158614558854172]
    ],
    'gas_energy': [-1.16, 0.00, -3.94]
}
df = pd.DataFrame(data, index=['CO', 'O2', 'CO2'])

# Create the GasModel instance
gas_model = GasModel.from_df(df)
```

---

## Adding and Removing Species

You can modify an existing `GasModel` by adding or removing species.

### Adding a Species

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

### Removing Species

Use the `remove_species` method to remove species by name.

#### Example

```python
# List of species to remove
species_to_remove = ['CO2']

# Remove species from the GasModel
gas_model.remove_species(species_to_remove)
```

---

## Accessing Gas-Phase Data

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
O2  linear            32.000           2           3   
N2  linear            28.013           2           1   

                      inertia_moments  gas_energy  
CO            [8.973619026272551]        -1.16  
O2          [12.178379354326061]         0.00  
N2                        [10.822]         0.00  
```

---

## Full Example

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
        'inertia_moments': [8.973619026272551],
        'gas_energy': -1.16
    },
    'O2': {
        'type': 'linear',
        'gas_molec_weight': 32.00,
        'sym_number': 2,
        'degeneracy': 3,
        'inertia_moments': [12.178379354326061],
        'gas_energy': 0.00
    }
}

# Create the GasModel instance
gas_model = GasModel.from_dict(species_data)

# Add a new species
gas_model.add_species(species_info={
    'species_name': 'CO2',
    'type': 'non_linear',
    'gas_molec_weight': 44.01,
    'sym_number': 2,
    'degeneracy': 1,
    'inertia_moments': [44.317229117708344, 22.158614558854172, 22.158614558854172],
    'gas_energy': -3.94
})

# Remove an existing species
gas_model.remove_species(['O2'])

# Access the DataFrame
print(gas_model.df)
```

---

## Next Steps

With the `GasModel` defined, you can proceed to:

- **Define the Reaction Model**: Specify reaction mechanisms using the `ReactionModel`.
- **Set Up the Energetics Model**: Provide cluster energetics with the `EnergeticsModel`.
- **Configure the Lattice Model**: Define the simulation lattice using the `LatticeModel`.
- **Assemble the KMC Model**: Integrate all components into a `KMCModel` for simulation.

For detailed guidance on these steps, refer to the respective sections in the documentation.

---

**Note:** Ensure that all required data is accurate and consistent when creating the `GasModel`, as this will impact the accuracy of your KMC simulations.