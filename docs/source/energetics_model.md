# Energetics model

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

| index          | cluster_eng              | site_types | lattice_state                            | neighboring | angles | graph_multiplicity |
|----------------|--------------------------|------------|------------------------------------------|-------------|--------|--------------------|
| CO_point       | 0.2308527000000104       | tC         | ['1 CO* 1']                              | NaN         | NaN    | NaN                |
| O_point        | -1.3260536999999744      | tC         | ['1 O* 1']                               | NaN         | NaN    | NaN                |
| CO2_point      | -1.5718709999999767      | tC         | ['1 CO2* 1']                             | NaN         | NaN    | NaN                |
| C_point        | 2.442806399999977        | tC         | ['1 C* 1']                               | NaN         | NaN    | NaN                |
| CO2+CO2_pair   | 0.1439299999999548       | tC tC      | ['1 CO2* 1', '2 CO2* 1']                 | 1-2         | NaN    | 2.0                |
| CO2+CO_pair    | -0.1832200000000057      | tC tC      | ['1 CO2* 1', '2 CO* 1']                  | 1-2         | NaN    | NaN                |
| CO2+O_pair     | -0.1612800000000334      | tC tC      | ['1 CO2* 1', '2 O* 1']                   | 1-2         | NaN    | NaN                |
| CO+CO_pair     | 0.1771099999999705       | tC tC      | ['1 CO* 1', '2 CO* 1']                   | 1-2         | NaN    | 2.0                |
| CO+O_pair      | -0.0324900000000525      | tC tC      | ['1 CO* 1', '2 O* 1']                    | 1-2         | NaN    | NaN                |
| O+O_pair       | 0.0333200000000033       | tC tC      | ['1 O* 1', '2 O* 1']                     | 1-2         | NaN    | 2.0                |

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
    'CO_point': {
        'cluster_eng': 0.2308527000000104,
        'site_types': 'tC',
        'lattice_state': ['1 CO* 1']
    },
    'O_point': {
        'cluster_eng': -1.3260536999999744,
        'site_types': 'tC',
        'lattice_state': ['1 O* 1']
    },
    'CO2_point': {
        'cluster_eng': -1.5718709999999767,
        'site_types': 'tC',
        'lattice_state': ['1 CO2* 1']
    },
    'C_point': {
        'cluster_eng': 2.442806399999977,
        'site_types': 'tC',
        'lattice_state': ['1 C* 1']
    },
    'CO2+CO2_pair': {
        'cluster_eng': 0.1439299999999548,
        'site_types': 'tC tC',
        'lattice_state': ['1 CO2* 1', '2 CO2* 1'],
        'neighboring': '1-2',
        'graph_multiplicity': 2.0
    },
    'CO2+CO_pair': {
        'cluster_eng': -0.1832200000000057,
        'site_types': 'tC tC',
        'lattice_state': ['1 CO2* 1', '2 CO* 1'],
        'neighboring': '1-2'
    },
    'CO2+O_pair': {
        'cluster_eng': -0.1612800000000334,
        'site_types': 'tC tC',
        'lattice_state': ['1 CO2* 1', '2 O* 1'],
        'neighboring': '1-2'
    },
    'CO+CO_pair': {
        'cluster_eng': 0.1771099999999705,
        'site_types': 'tC tC',
        'lattice_state': ['1 CO* 1', '2 CO* 1'],
        'neighboring': '1-2',
        'graph_multiplicity': 2.0
    },
    'CO+O_pair': {
        'cluster_eng': -0.0324900000000525,
        'site_types': 'tC tC',
        'lattice_state': ['1 CO* 1', '2 O* 1'],
        'neighboring': '1-2'
    },
    'O+O_pair': {
        'cluster_eng': 0.0333200000000033,
        'site_types': 'tC tC',
        'lattice_state': ['1 O* 1', '2 O* 1'],
        'neighboring': '1-2',
        'graph_multiplicity': 2.0
    }
}

# Create the EnergeticsModel instance
energetics_model = EnergeticsModel.from_dict(clusters_data)
```

### 2. From a CSV file

You can load cluster energetics data from a CSV file. The CSV should have the required columns and use the cluster names as the index.

#### Example CSV (`energetics_data.csv`)

```text
,index,cluster_eng,graph_multiplicity,lattice_state,neighboring,site_types
CO_point,0.2308527000000104,,['1 CO* 1'],,tC
O_point,-1.3260536999999744,,['1 O* 1'],,tC
CO2_point,-1.5718709999999767,,['1 CO2* 1'],,tC
C_point,2.442806399999977,,['1 C* 1'],,tC
CO2+CO2_pair,0.1439299999999548,2.0,"['1 CO2* 1', '2 CO2* 1']",1-2,"tC tC"
CO2+CO_pair,-0.1832200000000057,,"['1 CO2* 1', '2 CO* 1']",1-2,"tC tC"
CO2+O_pair,-0.1612800000000334,,"['1 CO2* 1', '2 O* 1']",1-2,"tC tC"
CO+CO_pair,0.1771099999999705,2.0,"['1 CO* 1', '2 CO* 1']",1-2,"tC tC"
CO+O_pair,-0.0324900000000525,,"['1 CO* 1', '2 O* 1']",1-2,"tC tC"
O+O_pair,0.0333200000000033,2.0,"['1 O* 1', '2 O* 1']",1-2,"tC tC"
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
    'cluster_eng': [
        0.2308527000000104,
        -1.3260536999999744,
        -1.5718709999999767,
        2.442806399999977,
        0.1439299999999548,
        -0.1832200000000057,
        -0.1612800000000334,
        0.1771099999999705,
        -0.0324900000000525,
        0.0333200000000033
    ],
    'graph_multiplicity': [
        None,
        None,
        None,
        None,
        2.0,
        None,
        None,
        2.0,
        None,
        2.0
    ],
    'lattice_state': [
        ['1 CO* 1'],
        ['1 O* 1'],
        ['1 CO2* 1'],
        ['1 C* 1'],
        ['1 CO2* 1', '2 CO2* 1'],
        ['1 CO2* 1', '2 CO* 1'],
        ['1 CO2* 1', '2 O* 1'],
        ['1 CO* 1', '2 CO* 1'],
        ['1 CO* 1', '2 O* 1'],
        ['1 O* 1', '2 O* 1']
    ],
    'neighboring': [
        None,
        None,
        None,
        None,
        '1-2',
        '1-2',
        '1-2',
        '1-2',
        '1-2',
        '1-2'
    ],
    'site_types': [
        'tC',
        'tC',
        'tC',
        'tC',
        'tC tC',
        'tC tC',
        'tC tC',
        'tC tC',
        'tC tC',
        'tC tC'
    ],
    'angles': [None]*10
}

df = pd.DataFrame(data, index=[
    'CO_point',
    'O_point',
    'CO2_point',
    'C_point',
    'CO2+CO2_pair',
    'CO2+CO_pair',
    'CO2+O_pair',
    'CO+CO_pair',
    'CO+O_pair',
    'O+O_pair'
])

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
    'cluster_name': 'new_cluster',
    'cluster_eng': 1.0,
    'site_types': 'tC tC',
    'lattice_state': ['1 CO* 1', '2 C* 1'],
    'neighboring': '1-2'
}

# Add the cluster to the EnergeticsModel
energetics_model.add_cluster(cluster_info=new_cluster)
```

### Removing clusters

Use the `remove_clusters` method to remove clusters by name.

#### Example

```python
# List of clusters to remove
clusters_to_remove = ['CO2_point']

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
                cluster_eng  graph_multiplicity                      lattice_state neighboring angles site_types
CO_point          0.2308527                NaN                         [1 CO* 1]        None   None        tC
O_point          -1.3260537                NaN                          [1 O* 1]        None   None        tC
CO2_point        -1.5718710                NaN                       [1 CO2* 1]        None   None        tC
C_point           2.4428064                NaN                         [1 C* 1]         None   None        tC
CO2+CO2_pair      0.1439300                2.0       [1 CO2* 1, 2 CO2* 1]         1-2    None     tC tC
CO2+CO_pair      -0.1832200                NaN         [1 CO2* 1, 2 CO* 1]         1-2    None     tC tC
CO2+O_pair       -0.1612800                NaN         [1 CO2* 1, 2 O* 1]          1-2    None     tC tC
CO+CO_pair        0.1771100                2.0         [1 CO* 1, 2 CO* 1]          1-2    None     tC tC
CO+O_pair        -0.0324900                NaN         [1 CO* 1, 2 O* 1]           1-2    None     tC tC
O+O_pair          0.0333200                2.0          [1 O* 1, 2 O* 1]           1-2    None     tC tC
```

---

## Full example

Below is an example demonstrating the creation and modification of an `EnergeticsModel`:

```python
from zacrostools.energetics_model import EnergeticsModel

# Initial cluster data
clusters_data = {
    'CO_point': {
        'cluster_eng': 0.2308527000000104,
        'site_types': 'tC',
        'lattice_state': ['1 CO* 1']
    },
    'O_point': {
        'cluster_eng': -1.3260536999999744,
        'site_types': 'tC',
        'lattice_state': ['1 O* 1']
    }
}

# Create the EnergeticsModel instance
energetics_model = EnergeticsModel.from_dict(clusters_data)

# Add a new cluster
energetics_model.add_cluster(cluster_info={
    'cluster_name': 'CO2_point',
    'cluster_eng': -1.5718709999999767,
    'site_types': 'tC',
    'lattice_state': ['1 CO2* 1']
})

# Remove an existing cluster
energetics_model.remove_clusters(['O_point'])

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