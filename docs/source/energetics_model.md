# 2. Create an Energetics Model

The `EnergeticsModel` stores information about each cluster included in the cluster expansion.

#### Properties

- **`cluster_eng`** (`float`): Cluster formation energy (eV).  
- **`lattice_state`** (`list[str]`): Cluster configuration (e.g., `['1 CO* 1', '2 CO* 1']`).  
- **`site_types`** (`str`, *optional*): Site types (required if `lattice_type='periodic_cell'`).  
- **`neighboring`** (`str`, *optional*): Connectivity between sites (e.g., `'1-2'`; default = `None`).  
- **`angles`** (`str`, *optional*): Angle constraints (e.g., `'1-2-3:180'`; default = `None`).  
- **`graph_multiplicity`** (`int`, *optional*): Graph multiplicity (default = `None`).  

#### How to create it

You can provide a dictionary where each key is a cluster name and each value is a dictionary of cluster properties:

```python
from zacrostools.energetics_model import EnergeticsModel

clusters_data = {
    'CO_point': {
        'cluster_eng': 0.230,
        'site_types': 'top',
        'lattice_state': ['1 CO* 1']
    },
    'O_point': {
        'cluster_eng': -1.326,
        'site_types': 'top',
        'lattice_state': ['1 O* 1']
    },
    'CO2_point': {
        'cluster_eng': -1.571,
        'site_types': 'top',
        'lattice_state': ['1 CO2* 1']
    },
    'C_point': {
        'cluster_eng': 2.442,
        'site_types': 'top',
        'lattice_state': ['1 C* 1']
    },
    'CO2+CO2_pair': {
        'cluster_eng': 0.143,
        'site_types': 'top top',
        'lattice_state': ['1 CO2* 1', '2 CO2* 1'],
        'neighboring': '1-2',
        'graph_multiplicity': 2.0
    },
    'CO2+CO_pair': {
        'cluster_eng': -0.183,
        'site_types': 'top top',
        'lattice_state': ['1 CO2* 1', '2 CO* 1'],
        'neighboring': '1-2'
    },
    'CO2+O_pair': {
        'cluster_eng': -0.161,
        'site_types': 'top top',
        'lattice_state': ['1 CO2* 1', '2 O* 1'],
        'neighboring': '1-2'
    },
    'CO+CO_pair': {
        'cluster_eng': 0.177,
        'site_types': 'top top',
        'lattice_state': ['1 CO* 1', '2 CO* 1'],
        'neighboring': '1-2',
        'graph_multiplicity': 2.0
    },
    'CO+O_pair': {
        'cluster_eng': -0.032,
        'site_types': 'top top',
        'lattice_state': ['1 CO* 1', '2 O* 1'],
        'neighboring': '1-2'
    },
    'O+O_pair': {
        'cluster_eng': 0.033,
        'site_types': 'top top',
        'lattice_state': ['1 O* 1', '2 O* 1'],
        'neighboring': '1-2',
        'graph_multiplicity': 2.0
    }
}

energetics_model = EnergeticsModel.from_dict(clusters_data)
```

Alternatively, it can also be created from a CSV file. In this case, the indexes must correspond to the cluster names:

```python
from zacrostools.energetics_model import EnergeticsModel

energetics_model = EnergeticsModel.from_csv('energetics_data.csv')
```

Finally, it can also be created from a Pandas dataframe:

```python
import pandas as pd
from zacrostools.energetics_model import EnergeticsModel

df = pd.read_csv("energetics_data.csv")  # or create dataframe directly
energetics_model = EnergeticsModel.from_df(df)
```

---

#### Adding and removing clusters

Use the `add_cluster` method to add a new cluster:

```python
new_cluster = {
    'cluster_name': 'new_cluster',
    'cluster_eng': 1.0,
    'site_types': 'top top',
    'lattice_state': ['1 CO* 1', '2 C* 1'],
    'neighboring': '1-2'
}

energetics_model.add_cluster(cluster_info=new_cluster)
```

Use the `remove_clusters` method to remove clusters by name:

```python
energetics_model.remove_clusters(['CO2_point'])
```

---

#### Writing the `energetics_input.dat` file

The `EnergeticsModel` can generate the `energetics_input.dat` file required by Zacros:

```python
energetics_model.write_energetics_input(output_dir, sig_figs_energies=8)
```

- **`output_dir`** (`str` or `Path`): Directory where the file will be written.
- **`sig_figs_energies`** (`int`, *optional*): Number of significant figures for cluster energies.

```python
energetics_model.write_energetics_input(output_dir='kmc_simulation')
```

This will generate a file named `energetics_input.dat` in the `kmc_simulation` directory.

---

#### Accessing energetics data

The cluster data is stored internally as a Pandas DataFrame, accessible via the `df` attribute.

```python
print(energetics_model.df)
```

#### Full example

Below is an example demonstrating the creation and modification of an `EnergeticsModel`:

```python
from zacrostools.energetics_model import EnergeticsModel

# Initial cluster data
clusters_data = {
    'CO_point': {
        'cluster_eng': 0.230,
        'site_types': 'top',
        'lattice_state': ['1 CO* 1']
    },
    'O_point': {
        'cluster_eng': -1.326,
        'site_types': 'top',
        'lattice_state': ['1 O* 1']
    }
}

# Create the EnergeticsModel instance
energetics_model = EnergeticsModel.from_dict(clusters_data)

# Add a new cluster
energetics_model.add_cluster(cluster_info={
    'cluster_name': 'CO2_point',
    'cluster_eng': -1.571,
    'site_types': 'top',
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
