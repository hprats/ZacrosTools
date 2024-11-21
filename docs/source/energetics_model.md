# Energetics Model

## Overview

The `EnergeticsModel` contains the information about each cluster included in the cluster expansion.

### Required columns

- **`cluster_eng`** (`float`): Cluster formation energy in electronvolts (eV).
- **`lattice_state`** (`list` of `str`): Cluster configuration in Zacros format, e.g., `['1 CO* 1', '2 CO* 1']`.

### Optional columns

- **`site_types`** (`str`): Types of each site in the cluster pattern. Required if `lattice_type` is `'periodic_cell'`.
- **`neighboring`** (`str`): Connectivity between sites involved, e.g., `'1-2'`. Default is `None`.
- **`angles`** (`str`): Angle constraints between sites in Zacros format, e.g., `'1-2-3:180'`. Default is `None`.
- **`graph_multiplicity`** (`int`): Symmetry number of the cluster. Default is `None`.

### Example data table

| index            | cluster_eng | site_types | lattice_state                  | neighboring | angles | graph_multiplicity |
|------------------|-------------|------------|-------------------------------|-------------|--------|--------------------|
| CO_on_site1      | -1.50       | 1          | ['1 CO* 1']                   | NaN         | NaN    | NaN                |
| O2_dissociation  | -2.00       | 1 1        | ['1 O* 1', '2 O* 1']          | 1-2         | NaN    | NaN                |
| CO2_formation    | -3.50       | 1 1 1      | ['1 CO* 1', '2 O* 1', '3 O* 1'] | 1-2 2-3     | 1-2-3:180 | 2                 |

---

## Creating an `EnergeticsModel`

You can create an `EnergeticsModel` instance in several ways:

1. **From a dictionary**
2. **From a CSV file**
3. **From a Pandas DataFrame**

### 1. From a dictionary

You can provide a dictionary where each key is a cluster name and each value is a dictionary of cluster properties.

#### Example

```python
from zacrostools.energetics_model import EnergeticsModel

# Define the energetics data
clusters_data = {
    'CO_on_site1': {
        'cluster_eng': -1.50,
        'site_types': '1',
        'lattice_state': ['1 CO* 1']
    },
    'O2_dissociation': {
        'cluster_eng': -2.00,
        'site_types': '1 1',
        'lattice_state': ['1 O* 1', '2 O* 1'],
        'neighboring': '1-2'
    },
    'CO2_formation': {
        'cluster_eng': -3.50,
        'site_types': '1 1 1',
        'lattice_state': ['1 CO* 1', '2 O* 1', '3 O* 1'],
        'neighboring': '1-2 2-3',
        'angles': '1-2-3:180',
        'graph_multiplicity': 2
    }
}

# Create the EnergeticsModel instance
energetics_model = EnergeticsModel.from_dict(clusters_data)
```

### 2. From a CSV file

You can load cluster energetics data from a CSV file. The CSV should have the required columns and use the cluster names as the index.

#### Example CSV (`energetics_data.csv`)

```text
,index,cluster_eng,site_types,lattice_state,neighboring,angles,graph_multiplicity
CO_on_site1,-1.50,1,"['1 CO* 1']",,,
O2_dissociation,-2.00,"1 1","['1 O* 1', '2 O* 1']","1-2",,
CO2_formation,-3.50,"1 1 1","['1 CO* 1', '2 O* 1', '3 O* 1']","1-2 2-3","1-2-3:180",2
```

#### Loading from CSV

```python
from zacrostools.energetics_model import EnergeticsModel

# Create the EnergeticsModel instance from a CSV file
energetics_model = EnergeticsModel.from_csv('energetics_data.csv')
```

### 3. From a Pandas DataFrame

If you have a DataFrame containing the cluster energetics data, you can create an `EnergeticsModel` directly.

#### Example

```python
import pandas as pd
from zacrostools.energetics_model import EnergeticsModel

# Create a DataFrame
data = {
    'cluster_eng': [-1.50, -2.00, -3.50],
    'site_types': ['1', '1 1', '1 1 1'],
    'lattice_state': [
        ['1 CO* 1'],
        ['1 O* 1', '2 O* 1'],
        ['1 CO* 1', '2 O* 1', '3 O* 1']
    ],
    'neighboring': [None, '1-2', '1-2 2-3'],
    'angles': [None, None, '1-2-3:180'],
    'graph_multiplicity': [None, None, 2]
}
df = pd.DataFrame(data, index=['CO_on_site1', 'O2_dissociation', 'CO2_formation'])

# Create the EnergeticsModel instance
energetics_model = EnergeticsModel.from_df(df)
```

---

## Adding and removing clusters

You can modify an existing `EnergeticsModel` by adding or removing clusters.

### Adding a cluster

Use the `add_cluster` method to add a new cluster.

#### Example

```python
# Define the new cluster data
new_cluster = {
    'cluster_name': 'CO2_adsorption',
    'cluster_eng': -4.00,
    'site_types': '1 1 1',
    'lattice_state': ['1 CO2* 1', '2 O* 1', '3 O* 1'],
    'neighboring': '1-2 2-3',
    'angles': '1-2-3:120',
    'graph_multiplicity': 1
}

# Add the cluster to the EnergeticsModel
energetics_model.add_cluster(cluster_info=new_cluster)
```

### Removing clusters

Use the `remove_clusters` method to remove clusters by name.

#### Example

```python
# List of clusters to remove
clusters_to_remove = ['O2_dissociation']

# Remove clusters from the EnergeticsModel
energetics_model.remove_clusters(clusters_to_remove)
```

---

## Writing the `energetics_input.dat` file

The `EnergeticsModel` can generate the `energetics_input.dat` file required by Zacros.

### Method

```python
energetics_model.write_energetics_input(output_dir, sig_figs_energies=8)
```

- **`output_dir`** (`str` or `Path`): Directory where the file will be written.
- **`sig_figs_energies`** (`int`, optional): Number of significant figures for cluster energies.

#### Example

```python
# Write the energetics_input.dat file to the specified directory
energetics_model.write_energetics_input(output_dir='kmc_simulation')
```

This will generate a file named `energetics_input.dat` in the `kmc_simulation` directory.

---

## Accessing energetics data

The cluster data is stored internally as a Pandas DataFrame, accessible via the `df` attribute.

#### Example

```python
# View the energetics data
print(energetics_model.df)
```

**Output:**

```
                 cluster_eng site_types                           lattice_state  \
CO_on_site1            -1.50          1                         [1 CO* 1]   
CO2_formation          -3.50      1 1 1  [1 CO* 1, 2 O* 1, 3 O* 1]   
CO2_adsorption         -4.00      1 1 1  [1 CO2* 1, 2 O* 1, 3 O* 1]   

              neighboring         angles  graph_multiplicity  
CO_on_site1          None           None                None  
CO2_formation      1-2 2-3  1-2-3:180                    2  
CO2_adsorption     1-2 2-3  1-2-3:120                    1  
```

---

## Full example

Below is an example demonstrating the creation and modification of an `EnergeticsModel`:

```python
from zacrostools.energetics_model import EnergeticsModel

# Initial cluster data
clusters_data = {
    'CO_on_site1': {
        'cluster_eng': -1.50,
        'site_types': '1',
        'lattice_state': ['1 CO* 1']
    },
    'O2_dissociation': {
        'cluster_eng': -2.00,
        'site_types': '1 1',
        'lattice_state': ['1 O* 1', '2 O* 1'],
        'neighboring': '1-2'
    }
}

# Create the EnergeticsModel instance
energetics_model = EnergeticsModel.from_dict(clusters_data)

# Add a new cluster
energetics_model.add_cluster(cluster_info={
    'cluster_name': 'CO2_formation',
    'cluster_eng': -3.50,
    'site_types': '1 1 1',
    'lattice_state': ['1 CO* 1', '2 O* 1', '3 O* 1'],
    'neighboring': '1-2 2-3',
    'angles': '1-2-3:180',
    'graph_multiplicity': 2
})

# Remove an existing cluster
energetics_model.remove_clusters(['O2_dissociation'])

# Write the energetics input file
energetics_model.write_energetics_input(output_dir='kmc_simulation')

# Access the DataFrame
print(energetics_model.df)
```

---

## Next steps

With the `EnergeticsModel` defined, you can proceed to:

- Define the `ReactionModel`
- Create a `LatticeModel`
- Assemble the `KMCModel`

For detailed guidance on these steps, refer to the respective sections in the documentation.


---

## Additional notes

- **Cluster Definitions**:
  - The `lattice_state` specifies the configuration of species on lattice sites, following Zacros syntax.
  - The `site_types` correspond to the types of sites involved in the cluster.

- **Neighboring and Angles**:
  - The `neighboring` field defines connections between sites using site indices (e.g., `'1-2'`).
  - The `angles` field can impose angle constraints between sites (e.g., `'1-2-3:180'` for a linear configuration).

- **Graph Multiplicity**:
  - The `graph_multiplicity` accounts for the symmetry of the cluster, affecting its statistical weight in simulations.

- **Writing the Input File**:
  - When writing the `energetics_input.dat` file, the clusters are defined in a format that Zacros can interpret directly.
