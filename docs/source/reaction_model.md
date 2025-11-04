# 3. Creating the Reaction Model

The `ReactionModel` stores information about each elementary reaction step. 

#### Properties

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


#### How to create it

You can provide a dictionary where each key is a cluster name and each value is a dictionary of elementary step properties:

```python
from zacrostools.reaction_model import ReactionModel

steps_data = {
    'CO_adsorption': {
        'activ_eng': 0.0,
        'area_site': 5.34,
        'initial': ['1 * 1'],
        'final': ['1 CO* 1'],
        'molecule_is': 'CO',
        'prox_factor': 0.0,
        'site_types': 'top',
        'vib_energies_is': [263.427],
        'vib_energies_fs': [240.497, 82.738, 60.132, 60.080, 7.271, 6.553],
    },
    'O2_adsorption': {
        'activ_eng': 0.742,
        'area_site': 5.34,
        'initial': ['1 * 1, 2 * 1'],
        'final': ['1 O* 1, 2 O* 1'],
        'neighboring': '1-2',
        'molecule_is': 'O2',
        'prox_factor': 0.5,
        'site_types': 'top',
        'vib_energies_is': [263.427],
        'vib_energies_ts': [244.692, 81.168, 53.342, 30.084, 2.234],
        'vib_energies_fs': [240.497, 82.738, 60.132, 60.080, 7.271, 6.553],
    }, 
    'CO+O_to_CO2': {
        'activ_eng': 1.693,
        'initial': ['1 CO* 1', '2 O* 1'],
        'final': ['1 CO2* 1', '2 * 1'],
        'neighboring': '1-2',
        'site_types': 'top top',
        'vib_energies_is': [171.188, 145.669, 96.964, 86.255, 56.201, 52.376, 35.933, 24.343, 21.025],
        'vib_energies_ts': [217.941, 81.362, 66.833, 56.918, 50.342, 37.430, 19.074, 12.356],
        'vib_energies_fs': [240.497, 82.738, 60.133, 60.080, 7.272, 6.553, 78.662, 40.796, 40.349],
    },
    'CO2_adsorption': {  # recommended to define the forward direction as the adsorption
        'activ_eng': 0.0,
        'area_site': 5.34,
        'initial': ['1 * 1'],
        'final': ['1 CO2* 1'],
        'molecule_is': 'CO2',
        'prox_factor': 0.0,
        'site_types': 'top',
        'vib_energies_is': [293.279, 163.686, 78.019, 77.959],
        'vib_energies_fs': [171.188, 145.668, 96.961, 86.214, 56.201, 52.375, 35.932, 24.343, 21.022],
    }
}

reaction_model = ReactionModel.from_dict(steps_data)
```

Alternatively, it can also be created from a CSV file. In this case, the indexes must correspond to the elementary step names:

```python
from zacrostools.reaction_model import ReactionModel

reaction_model = ReactionModel.from_csv('mechanism_data.csv')
```

Finally, it can also be created from a Pandas dataframe:

```python
import pandas as pd
from zacrostools.reaction_model import ReactionModel

df = pd.read_csv("reactions_data.csv")  # or create dataframe directly
reaction_model = ReactionModel.from_df(df)
```

---

#### Adding and removing steps

Use the `add_step` method to add a new step:

```python
reaction_model.add_step(step_info={
        'step_name': 'CO_diffusion',
        'activ_eng': 1.156,
        'initial': ['1 CO* 1', '2 * 1'],
        'final': ['1 * 1', '2 CO* 1'],
        'neighboring': '1-2',
        'graph_multiplicity': 2.0,
        'site_types': 'top top',
        'vib_energies_fs': [240.497, 82.738, 60.133, 60.080, 7.272, 6.553],
        'vib_energies_is': [240.497, 82.738, 60.133, 60.080, 7.272, 6.553],
        'vib_energies_ts': [218.382, 53.527, 47.612, 28.580, 6.600]
    })
```

Use the `remove_steps` method to remove a step:

```python
steps_to_remove = ['O_diffusion']
reaction_model.remove_steps(steps_to_remove)
```

---

#### Writing the `mechanism_input.dat` file

The `ReactionModel` can generate the `mechanism_input.dat` file required by Zacros.

Required parameters:
- **`output_dir`** (`str` or `Path`): Directory where the file will be written.
- **`temperature`** (`float`): Temperature in Kelvin for pre-exponential calculations.
- **`gas_model`** (`GasModel`): Instance of `GasModel` containing gas-phase species data.
- **`manual_scaling`** (`dict`, optional): Dictionary of manual scaling factors per step.
- **`stiffness_scalable_steps`** (`list`, optional): List of steps that are stiffness scalable.
- **`stiffness_scalable_symmetric_steps`** (`list`, optional): List of steps that are stiffness scalable and symmetric.
- **`sig_figs_energies`** (`int`, optional): Number of significant figures for activation energies.
- **`sig_figs_pe`** (`int`, optional): Number of significant figures for pre-exponential factors.

```python
from zacrostools.gas_model import GasModel

gas_model = GasModel.from_csv('gas_data.csv')
reaction_model.write_mechanism_input(
    output_dir='kmc_simulation',
    temperature=500,
    gas_model=gas_model,
    sig_figs_energies=8,
    sig_figs_pe=8
)
```

---

#### Accessing reaction data

The reaction steps data is stored internally as a Pandas DataFrame, accessible via the `df` attribute.

```python
print(reaction_model.df)
```

---

#### Full example

Below is a complete example demonstrating the creation and modification of a `ReactionModel`:

```python
from zacrostools.reaction_model import ReactionModel
from zacrostools.gas_model import GasModel

# Assume gas_model is already defined
gas_model = GasModel.from_csv('gas_data.csv')

# Initial reaction steps data
steps_data = {
    'CO_adsorption': {
        'activ_eng': 0.0,
        'area_site': 5.34,
        'initial': ['1 * 1'],
        'final': ['1 CO* 1'],
        'molecule_is': 'CO',
        'prox_factor': 0.0,
        'site_types': 'top',
        'vib_energies_is': [263.427],
        'vib_energies_fs': [240.497, 82.738, 60.132, 60.080, 7.271, 6.553],
    }
}

# Create the ReactionModel instance
reaction_model = ReactionModel.from_dict(steps_data)

# Add a new step
reaction_model.add_step(step_info={
        'step_name': 'CO_diffusion',
        'activ_eng': 1.156,
        'initial': ['1 CO* 1', '2 * 1'],
        'final': ['1 * 1', '2 CO* 1'],
        'neighboring': '1-2',
        'graph_multiplicity': 2.0,
        'site_types': 'top top',
        'vib_energies_is': [240.497, 82.738, 60.133, 60.080, 7.272, 6.553],
        'vib_energies_ts': [218.382, 53.527, 47.612, 28.580, 6.600],
        'vib_energies_fs': [240.497, 82.738, 60.133, 60.080, 7.272, 6.553],
    })


# Remove an existing step
reaction_model.remove_steps(['CO_diffusion'])

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

#### Fixing pre-exponential factors

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

```python
from zacrostools.reaction_model import ReactionModel

reaction_data = {
    'CO_adsorption': {
        'activ_eng': 0.0,
        'area_site': 5.34,
        'initial': ['1 * 1'],
        'final': ['1 CO* 1'],
        'molecule_is': 'CO',
        'prox_factor': 0.0,
        'site_types': 'top',
        'vib_energies_is': [263.427],
        'vib_energies_fs': [240.497, 82.738, 60.132, 60.080, 7.271, 6.553],
        "fixed_pre_expon": 1.0e13,  # in s^-1 or bar^-1·s^-1 depending on type
        "fixed_pe_ratio": 2.5
    },
}

reaction_model = ReactionModel.from_dict(reaction_data)
```