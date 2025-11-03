# Reaction model

## Overview

The `ReactionModel` stores information about each elementary reaction step. Supported step types include non-activated/activated adsorption or desorption, and surface reactions or diffusions.

### Properties

- **`initial`** (`list[str]`): Initial configuration (e.g., `['1 CO* 1', '2 * 1']`).  
- **`final`** (`list[str]`): Final configuration (e.g., `['1 C* 1', '2 O* 1']`).  
- **`activ_eng`** (`float`): Activation energy (eV).  
- **`vib_energies_is`** (`list[float]`): Vibrational energies for the initial state (meV).  
- **`vib_energies_fs`** (`list[float]`): Vibrational energies for the final state (meV).  
- **`vib_energies_ts`** (`list[float]`, *optional*): Vibrational energies for the transition state (meV).  
  Omit or set to `[]` for non-activated steps.  
- **`area_site`** (`float`, *optional*): Site area (Å²); required if a gas species participates.  
- **`molecule_is`** (`str`, *optional*): Name of gas-phase molecule in the initial state (only for adsorption).  
- **`molecule_fs`** (`str`, *optional*): Name of gas-phase molecule in the final state (only for desorption).  
- **`site_types`** (`str`, *optional*): Site types required if `lattice_type='periodic_cell'`).  
- **`neighboring`** (`str`, *optional*): Connectivity between sites (e.g., `'1-2'`; default = `None`).  
- **`prox_factor`** (`float`, *optional*): Proximity factor.  
- **`angles`** (`str`, *optional*): Angle constraints (e.g., `'1-2-3:180'`; default = `None`).  
- **`graph_multiplicity`** (`int` or `float`, *optional*): Symmetry factor of the step. The computed pre-exponential factor is divided by this value.  
- **`fixed_pre_expon`** (`float`, *optional*): Fixed forward pre-exponential factor (no scaling or symmetry applied).  
  Units must follow Zacros conventions:  
  - Surface/non-activated desorption → `s⁻¹`  
  - Adsorption (activated/non-activated) → `bar⁻¹·s⁻¹`  
- **`fixed_pe_ratio`** (`float`, *optional*): Fixed pre-exponential ratio `pe_fwd/pe_rev`. Must be used with `fixed_pre_expon`.  

> **Deprecation note:** The old **`molecule`** column is deprecated and treated as `molecule_is` with a warning.


---

### Example data table

| index       | activ_eng          | area_site | final                          | graph_multiplicity | initial                       | molecule_is | neighboring | prox_factor | site_types | vib_energies_fs                                                                 | vib_energies_is                                                                             | vib_energies_ts                                                              |
|-------------|--------------------|-----------|--------------------------------|--------------------|-------------------------------|-------------|-------------|-------------|------------|----------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| aO2_HfC     | 0.0                | 5.34      | ['1 O* 1', '2 O* 1']           | NaN                | ['1 * 1', '2 * 1']            | O2          | 1-2         | 0.0         | tC tC      | [78.662275, 40.796289, 40.348665, 78.662275, 40.796289, 40.348665]              | [194.605883]                                                                                | []                                                                            |
| aCO_HfC     | 0.0                | 5.34      | ['1 CO* 1']                    | NaN                | ['1 * 1']                     | CO          | NaN         | 0.0         | tC         | [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]               | [263.427949]                                                                                | []                                                                            |
| aCO2_HfC    | 0.0                | 5.34      | ['1 CO2* 1']                   | NaN                | ['1 * 1']                     | CO2         | NaN         | 0.0         | tC         | [171.188002, 145.668886, 96.963691, 86.25514, 56.201368, 52.375682, 35.933392, 24.342963, 21.024922] | [293.279791, 163.611086, 78.016609, 77.959489]                                                | []                                                                            |
| fCO_HfC     | 1.3251912539165005 | NaN       | ['1 CO* 1', '2 * 1']           | NaN                | ['1 C* 1', '2 O* 1']          | NaN         | 1-2         | NaN         | tC tC      | [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]               | [138.207451, 24.592242, 17.986572, 78.662275, 40.796289, 40.348665]                          | [129.799624, 55.940895, 41.760039, 33.292377, 20.816034]                       |
| bCO2_HfC    | 1.6930197990402576 | NaN       | ['1 CO* 1', '2 O* 1']          | NaN                | ['1 CO2* 1', '2 * 1']         | NaN         | 1-2         | NaN         | tC tC      | [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359, 78.662275, 40.796289, 40.348665] | [171.188002, 145.668886, 96.963691, 86.25514, 56.201368, 52.375682, 35.933392, 24.342963, 21.024922] | [217.940927, 81.361728, 66.833494, 56.917831, 50.342099, 37.430358, 19.074043, 12.356398] |
| dCO_HfC     | 1.156349999999975  | NaN       | ['1 * 1', '2 CO* 1']           | 2.0                | ['1 CO* 1', '2 * 1']          | NaN         | 1-2         | NaN         | tC tC      | [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]               | [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]                           | [218.382388, 53.526855, 47.6122, 28.580404, 6.599679]                         |
| dO_HfC      | 1.220541240457237  | NaN       | ['1 * 1', '2 O* 1']            | 2.0                | ['1 O* 1', '2 * 1']           | NaN         | 1-2         | NaN         | tC tC      | [78.662275, 40.796289, 40.348665]                                               | [78.662275, 40.796289, 40.348665]                                                          | [56.617104, 49.715199]                                                       |
| dC_HfC      | 1.4489481277169034 | NaN       | ['1 * 1', '2 C* 1']            | NaN                | ['1 C* 1', '2 * 1']           | NaN         | 1-2         | NaN         | tC tC      | [138.207451, 24.592242, 17.986572]                                               | [138.207451, 24.592242, 17.986572]                                                        | [85.015794, 66.512731]                                                       |

---

## Creating a `ReactionModel`

You can create a `ReactionModel` instance in several ways:

1. **From a dictionary**
2. **From a CSV file**
3. **From a Pandas DataFrame**

### 1. From a dictionary

Provide a dictionary where each key is a reaction step name and each value is a dictionary of step properties.

#### Example

```python
from zacrostools.reaction_model import ReactionModel

# Define the reaction steps data
steps_data = {
    'aO2_HfC': {
        'activ_eng': 0.0,
        'area_site': 5.34,
        'final': ['1 O* 1', '2 O* 1'],
        'initial': ['1 * 1', '2 * 1'],
        'molecule_is': 'O2',
        'neighboring': '1-2',
        'prox_factor': 0.0,
        'site_types': 'tC tC',
        'vib_energies_fs': [78.662275, 40.796289, 40.348665, 78.662275, 40.796289, 40.348665],
        'vib_energies_is': [194.605883],
        'vib_energies_ts': []
    },
    'aCO_HfC': {
        'activ_eng': 0.0,
        'area_site': 5.34,
        'final': ['1 CO* 1'],
        'initial': ['1 * 1'],
        'molecule_is': 'CO',
        'prox_factor': 0.0,
        'site_types': 'tC',
        'vib_energies_fs': [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359],
        'vib_energies_is': [263.427949],
        'vib_energies_ts': []
    },
    'aCO2_HfC': {
        'activ_eng': 0.0,
        'area_site': 5.34,
        'final': ['1 CO2* 1'],
        'initial': ['1 * 1'],
        'molecule_is': 'CO2',
        'prox_factor': 0.0,
        'site_types': 'tC',
        'vib_energies_fs': [171.188002, 145.668886, 96.963691, 86.25514, 56.201368, 52.375682, 35.933392, 24.342963, 21.024922],
        'vib_energies_is': [293.279791, 163.611086, 78.016609, 77.959489],
        'vib_energies_ts': []
    },
    'fCO_HfC': {
        'activ_eng': 1.3251912539165005,
        'final': ['1 CO* 1', '2 * 1'],
        'initial': ['1 C* 1', '2 O* 1'],
        'neighboring': '1-2',
        'site_types': 'tC tC',
        'vib_energies_fs': [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359],
        'vib_energies_is': [138.207451, 24.592242, 17.986572, 78.662275, 40.796289, 40.348665],
        'vib_energies_ts': [129.799624, 55.940895, 41.760039, 33.292377, 20.816034]
    },
    'bCO2_HfC': {
        'activ_eng': 1.6930197990402576,
        'final': ['1 CO* 1', '2 O* 1'],
        'initial': ['1 CO2* 1', '2 * 1'],
        'neighboring': '1-2',
        'site_types': 'tC tC',
        'vib_energies_fs': [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359, 78.662275, 40.796289, 40.348665],
        'vib_energies_is': [171.188002, 145.668886, 96.963691, 86.25514, 56.201368, 52.375682, 35.933392, 24.342963, 21.024922],
        'vib_energies_ts': [217.940927, 81.361728, 66.833494, 56.917831, 50.342099, 37.430358, 19.074043, 12.356398]
    },
    'dCO_HfC': {
        'activ_eng': 1.156349999999975,
        'final': ['1 * 1', '2 CO* 1'],
        'initial': ['1 CO* 1', '2 * 1'],
        'neighboring': '1-2',
        'graph_multiplicity': 2.0,
        'site_types': 'tC tC',
        'vib_energies_fs': [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359],
        'vib_energies_is': [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359],
        'vib_energies_ts': [218.382388, 53.526855, 47.6122, 28.580404, 6.599679]
    },
    'dO_HfC': {
        'activ_eng': 1.220541240457237,
        'final': ['1 * 1', '2 O* 1'],
        'initial': ['1 O* 1', '2 * 1'],
        'neighboring': '1-2',
        'graph_multiplicity': 2.0,
        'site_types': 'tC tC',
        'vib_energies_fs': [78.662275, 40.796289, 40.348665],
        'vib_energies_is': [78.662275, 40.796289, 40.348665],
        'vib_energies_ts': [56.617104, 49.715199]
    },
    'dC_HfC': {
        'activ_eng': 1.4489481277169034,
        'final': ['1 * 1', '2 C* 1'],
        'initial': ['1 C* 1', '2 * 1'],
        'neighboring': '1-2',
        'site_types': 'tC tC',
        'vib_energies_fs': [138.207451, 24.592242, 17.986572],
        'vib_energies_is': [138.207451, 24.592242, 17.986572],
        'vib_energies_ts': [85.015794, 66.512731]
    }
}

# Create the ReactionModel instance
reaction_model = ReactionModel.from_dict(steps_data)
```

### 2. From a CSV File

Load reaction steps data from a CSV file. The CSV should have the required columns and use the reaction step names as the index.

#### Example CSV (`mechanism_data.csv`)

```csv
,index,activ_eng,area_site,final,graph_multiplicity,initial,molecule_is,neighboring,prox_factor,site_types,vib_energies_fs,vib_energies_is,vib_energies_ts
aO2_HfC,0.0,5.34,"['1 O* 1', '2 O* 1']",,"['1 * 1', '2 * 1']",O2,1-2,0.0,"tC tC","[78.662275, 40.796289, 40.348665, 78.662275, 40.796289, 40.348665]",[194.605883],[]
aCO_HfC,0.0,5.34,"['1 CO* 1']",,"['1 * 1']",CO,,0.0,tC,"[240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]",[263.427949],[]
aCO2_HfC,0.0,5.34,"['1 CO2* 1']",,"['1 * 1']",CO2,,0.0,tC,"[171.188002, 145.668886, 96.963691, 86.25514, 56.201368, 52.375682, 35.933392, 24.342963, 21.024922]","[293.279791, 163.611086, 78.016609, 77.959489]",[]
fCO_HfC,1.3251912539165005,,"['1 CO* 1', '2 * 1']",,"['1 C* 1', '2 O* 1']",,1-2,, "tC tC","[240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]","[138.207451, 24.592242, 17.986572, 78.662275, 40.796289, 40.348665]","[129.799624, 55.940895, 41.760039, 33.292377, 20.816034]"
bCO2_HfC,1.6930197990402576,,"['1 CO* 1', '2 O* 1']",,"['1 CO2* 1', '2 * 1']",,1-2,, "tC tC","[240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359, 78.662275, 40.796289, 40.348665]","[171.188002, 145.668886, 96.963691, 86.25514, 56.201368, 52.375682, 35.933392, 24.342963, 21.024922]","[217.940927, 81.361728, 66.833494, 56.917831, 50.342099, 37.430358, 19.074043, 12.356398]"
dCO_HfC,1.156349999999975,,"['1 * 1', '2 CO* 1']",2.0,"['1 CO* 1', '2 * 1']",,1-2,, "tC tC","[240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]","[240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]","[218.382388, 53.526855, 47.6122, 28.580404, 6.599679]"
dO_HfC,1.220541240457237,,"['1 * 1', '2 O* 1']",2.0,"['1 O* 1', '2 * 1']",,1-2,, "tC tC","[78.662275, 40.796289, 40.348665]","[78.662275, 40.796289, 40.348665]","[56.617104, 49.715199]"
dC_HfC,1.4489481277169034,,"['1 * 1', '2 C* 1']",,"['1 C* 1', '2 * 1']",,1-2,, "tC tC","[138.207451, 24.592242, 17.986572]","[138.207451, 24.592242, 17.986572]","[85.015794, 66.512731]"
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

data = {
    'activ_eng': [0.0, 0.0, 0.0, 1.3251912539165005, 1.6930197990402576, 1.156349999999975, 1.220541240457237, 1.4489481277169034],
    'area_site': [5.34, 5.34, 5.34, None, None, None, None, None],
    'final': [
        ['1 O* 1', '2 O* 1'],
        ['1 CO* 1'],
        ['1 CO2* 1'],
        ['1 CO* 1', '2 * 1'],
        ['1 CO* 1', '2 O* 1'],
        ['1 * 1', '2 CO* 1'],
        ['1 * 1', '2 O* 1'],
        ['1 * 1', '2 C* 1']
    ],
    'graph_multiplicity': [None, None, None, None, None, 2.0, 2.0, None],
    'initial': [
        ['1 * 1', '2 * 1'],
        ['1 * 1'],
        ['1 * 1'],
        ['1 C* 1', '2 O* 1'],
        ['1 CO2* 1', '2 * 1'],
        ['1 CO* 1', '2 * 1'],
        ['1 O* 1', '2 * 1'],
        ['1 C* 1', '2 * 1']
    ],
    'molecule_is': ['O2', 'CO', 'CO2', None, None, None, None, None],
    'neighboring': ['1-2', None, None, '1-2', '1-2', '1-2', '1-2', '1-2'],
    'prox_factor': [0.0, 0.0, 0.0, None, None, None, None, None],
    'site_types': ['tC tC', 'tC', 'tC', 'tC tC', 'tC tC', 'tC tC', 'tC tC', 'tC tC'],
    'vib_energies_fs': [
        [78.662275, 40.796289, 40.348665, 78.662275, 40.796289, 40.348665],
        [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359],
        [171.188002, 145.668886, 96.963691, 86.25514, 56.201368, 52.375682, 35.933392, 24.342963, 21.024922],
        [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359],
        [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359, 78.662275, 40.796289, 40.348665],
        [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359],
        [78.662275, 40.796289, 40.348665],
        [138.207451, 24.592242, 17.986572]
    ],
    'vib_energies_is': [
        [194.605883],
        [263.427949],
        [293.279791, 163.611086, 78.016609, 77.959489],
        [138.207451, 24.592242, 17.986572, 78.662275, 40.796289, 40.348665],
        [171.188002, 145.668886, 96.963691, 86.25514, 56.201368, 52.375682, 35.933392, 24.342963, 21.024922],
        [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359],
        [78.662275, 40.796289, 40.348665],
        [138.207451, 24.592242, 17.986572]
    ],
    'vib_energies_ts': [
        [],
        [],
        [],
        [129.799624, 55.940895, 41.760039, 33.292377, 20.816034],
        [217.940927, 81.361728, 66.833494, 56.917831, 50.342099, 37.430358, 19.074043, 12.356398],
        [218.382388, 53.526855, 47.6122, 28.580404, 6.599679],
        [56.617104, 49.715199],
        [85.015794, 66.512731]
    ]
}

df = pd.DataFrame(data, index=[
    'aO2_HfC',
    'aCO_HfC',
    'aCO2_HfC',
    'fCO_HfC',
    'bCO2_HfC',
    'dCO_HfC',
    'dO_HfC',
    'dC_HfC'
])

# Create the ReactionModel instance
reaction_model = ReactionModel.from_df(df)
```

---

## Adding and removing steps

You can modify an existing model programmatically.

### Adding a step

```python
new_step = {
    'step_name': 'new_step',
    'activ_eng': 2.0,
    'final': ['1 * 1'],
    'initial': ['1 CO* 1'],
    'vib_energies_is': [150, 200],
    'vib_energies_fs': [100, 150],
    'vib_energies_ts': [125],
    'site_types': 'tC'
}

reaction_model.add_step(step_info=new_step)
```

### Removing steps

```python
steps_to_remove = ['aCO_HfC']
reaction_model.remove_steps(steps_to_remove)
```

---


## Writing the `mechanism_input.dat` file

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

# Write the mechanism_input.dat file
reaction_model.write_mechanism_input(
    output_dir='kmc_simulation',
    temperature=500,
    gas_model=gas_model,
    sig_figs_energies=8,
    sig_figs_pe=8
)
```

---

## Accessing reaction data

The reaction steps data is stored internally as a Pandas DataFrame, accessible via the `df` attribute.

#### Example

```python
# View the reaction steps data
print(reaction_model.df)
```

---

## Full example

Below is a complete example demonstrating the creation and modification of a `ReactionModel`:

```python
from zacrostools.reaction_model import ReactionModel
from zacrostools.gas_model import GasModel

# Assume gas_model is already defined
gas_model = GasModel.from_csv('gas_data.csv')

# Initial reaction steps data
steps_data = {
    'aO2_HfC': {
        'activ_eng': 0.0,
        'area_site': 5.34,
        'final': ['1 O* 1', '2 O* 1'],
        'initial': ['1 * 1', '2 * 1'],
        'molecule_is': 'O2',
        'neighboring': '1-2',
        'prox_factor': 0.0,
        'site_types': 'tC tC',
        'vib_energies_fs': [78.662275, 40.796289, 40.348665, 78.662275, 40.796289, 40.348665],
        'vib_energies_is': [194.605883],
        'vib_energies_ts': []
    }
}

# Create the ReactionModel instance
reaction_model = ReactionModel.from_dict(steps_data)

# Add a new step
reaction_model.add_step(step_info={
    'step_name': 'aCO_HfC',
    'activ_eng': 0.0,
    'area_site': 5.34,
    'final': ['1 CO* 1'],
    'initial': ['1 * 1'],
    'molecule_is': 'CO',
    'prox_factor': 0.0,
    'site_types': 'tC',
    'vib_energies_fs': [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359],
    'vib_energies_is': [263.427949],
    'vib_energies_ts': []
})

# Remove an existing step
reaction_model.remove_steps(['aO2_HfC'])

# Write the mechanism input file
reaction_model.write_mechanism_input(
    output_dir='kmc_simulation',
    temperature=500,
    gas_model=gas_model,
    sig_figs_energies=8,
    sig_figs_pe=8
)

# Access the DataFrame
print(reaction_model.df)
```

---

## Fixing pre-exponential factors

By default, `ReactionModel` computes the forward pre-exponential factor (`pre_expon`) and the pre-exponential ratio (`pe_ratio`) from statistical mechanics.  
However, in some cases you may want to **fix these values explicitly** (for both forward and reverse directions). This can be done by providing two optional parameters:

- **`fixed_pre_expon`** (`float`): User-specified forward pre-exponential factor.  
- **`fixed_pe_ratio`** (`float`): User-specified pre-exponential ratio.  

⚠️ **Important**:  
- If one of these parameters is provided, the other must also be provided.  
- Using `fixed_pre_expon`/`fixed_pe_ratio` is **incompatible** with:
  1. Setting `stiffness_scalable_steps="all"`.  
  2. Including a fixed step in `stiffness_scalable_steps`.  
  3. Including a fixed step in `stiffness_scalable_symmetric_steps`.  

If any of these conditions occur, a `ReactionModelError` is raised.

### Example

```python
from zacrostools.reaction_model import ReactionModel

reaction_data = {
    'CO_ads': {
        'activ_eng': 0.0,
        'area_site': 6.54,
        'initial': ['1 * 1'],
        'final': ['1 CO* 1'],
        'molecule_is': 'CO',
        'prox_factor': 0.0,
        'vib_energies_is': [263],
        'vib_energies_fs': [253, 40, 36, 33, 7, 5],
        "fixed_pre_expon": 1.0e13,  # in s^-1 or bar^-1·s^-1 depending on type
        "fixed_pe_ratio": 2.5
    }
}

reaction_model = ReactionModel.from_dict(reaction_data)
```

## Next Steps

With the `ReactionModel` defined, you can proceed to:

- Create a `LatticeModel`
- Assemble the `KMCModel`

For detailed guidance on these steps, refer to the respective sections in the documentation.