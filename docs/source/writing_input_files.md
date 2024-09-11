# Writing Input Files

In ZacrosTools, a Kinetic Monte Carlo (KMC) model is represented as a `KMCModel` object, which contains information on the gas-phase species involved, the reaction model, the energetics model, and the lattice model. Follow these steps to create a `KMCModel` object.

## 1. Information on the Gas-Phase Species

This information is contained in a `pandas.DataFrame`, where each row corresponds to a gas-phase molecule.

```{important}
The row index must be the name of the species.
```

### Columns

**Mandatory:**

- **type** (*str*): `'non_linear'` or `'linear'`.
- **gas_molec_weight** (*float*): Molecular weights (in amu) of the gas species.
- **sym_number** (*int*): Symmetry number of the molecule.
- **inertia_moments** (*list*): Moments of inertia for the gas-phase molecule (in amu·Å²).
  - 1 element for linear molecules, 3 elements for non-linear molecules.
  - Can be obtained from `ase.Atoms.get_moments_of_inertia()`.
- **gas_energy** (*float*): Formation energy (in eV). Do not include the ZPE.

**Optional:**

- **degeneracy** (*int*): Degeneracy of the ground state, for the calculation of the electronic partition function. 
  - Default value: `1`.

```{caution}
The **gas_energy** must not include the ZPE (it is included in the pre-exponential factor).
```

### Example

| index | type   | gas_molec_weight | sym_number | degeneracy | inertia_moments      | gas_energy |
|-------|--------|------------------|------------|------------|----------------------|------------|
| CO    | linear | 28.01            | 1          | 1          | [8.973619026272551]  | 1.96       |
| O2    | linear | 32.0             | 2          | 3          | [12.178379354326061] | 2.6        |
| CO2   | linear | 44.01            | 2.0        | 1.0        | [44.317229117708344] | 0.0        |

This `pandas.DataFrame` can be created, for instance, by including all the information on a `.csv` file and reading it:

```python
import pandas as pd

gas_data = pd.read_csv('gas_data.csv', index_col=0)
```

Alternatively, it can be created from a `dict`:

```python
import pandas as pd

gas_molecules = {
    'CO': {'type': 'linear',
           'gas_molec_weight': 28.01,
           'sym_number': 1,
           'degeneracy': 1,
           'inertia_moments': [8.973619026272551],
           'gas_energy': 1.96},
    'O2': {'type': 'linear',
           'gas_molec_weight': 32.0,
           'sym_number': 2,
           'degeneracy': 3,
           'inertia_moments': [12.178379354326061],
           'gas_energy': 2.60}
}

gas_data = pd.DataFrame(gas_molecules).T
```

## 2. Reaction model

The information on the reaction model is also contained in a `pandas.DataFrame`, where each row corresponds to an 
elementary step.

```{important}
The row index must be the name of the step.
```

### Columns

**Mandatory:**

- **site_types** (*str*): The types of each site in the pattern.
- **initial** (*list*): Initial configuration in Zacros format. 
  - Example: `['1 CO* 1','2 * 1']`.
- **final** (*list*): Final configuration in Zacros format.
  - Example: `['1 C* 1','2 O* 1']`.
- **activ_eng** (*float*): Activation energy (in eV).
- **vib_energies_is** (*list*): Vibrational energies for the initial state (in meV). Do not include the ZPE.
- **vib_energies_fs** (*list*): Vibrational energies for the final state (in meV). Do not include the ZPE.

**Mandatory for adsorption steps:**

- **molecule** (*str*): Gas-phase molecule involved. Only required for adsorption steps.
- **area_site** (*float*): Area of adsorption site (in Å²). Only required for adsorption steps.

**Mandatory for activated adsorption steps and surface reaction steps:**

- **vib_energies_ts** (*list*): Vibrational energies for the transition state (in meV). For non-activated adsorption 
steps, this value can be either undefined or an empty list, i.e., `[]`.

**Optional:**

- **neighboring** (*str*): Connectivity between sites involved.
  - Example: `'1-2'` 
  - Default value: `None`.
- **prox_factor** (*float*): Proximity factor. 
  - Default value: `0.5`.
- **angles** (*str*): Angle between sites in Zacros format.
  - Example: `'1-2-3:180'`. 
  - Default value: `None`.

```{caution}
- `activ_eng` must not include the ZPE (it is included in the pre-exponential factor).
- For elementary steps with more than one surface species in the initial and/or final states:
  - `activ_eng` must be calculated from the **co-adsorbed** configuration of the reactants.
  - `vib_energies_is` and `vib_energies_fs` must correspond to the reactants and/or products at **infinite** 
  separation.
```

### Example

| index          | site_types | neighboring | area_site | initial               | final                 | activ_eng | molecule | vib_energies_is                                                                                    | vib_energies_fs                                                                                      | vib_energies_ts                                                                           | prox_factor |
|----------------|------------|-------------|-----------|-----------------------|-----------------------|-----------|----------|----------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|-------------|
| CO_adsorption  | topC       |             | 5.34      | ['1 * 1']             | ['1 CO* 1']           | 0.0       | CO       | [264.160873]                                                                                       | [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]                                    | []                                                                                        | 0.0         |
| O2_adsorption  | topC topC  | 1-2         | 5.34      | ['1 * 1', '2 * 1']    | ['1 O* 1', '2 O* 1']  | 0.0       | O2       | [194.973022]                                                                                       | [79.738187, 77.981497, 40.487926, 39.798116, 38.056578, 37.441762]                                   | []                                                                                        | 0.0         |
| CO2_adsorption | topC       |             | 5.34      | ['1 * 1']             | ['1 CO2* 1']          | 0.0       | CO2      | [294.059036, 163.752147, 78.494148, 78.310738]                                                     | [171.188002, 145.668886, 96.963691, 86.25514, 56.201368, 52.375682, 35.933392, 24.342963, 21.024922] | []                                                                                        | 0.0         |
| CO+O_reaction  | topC topC  | 1-2         |           | ['1 CO* 1', '2 O* 1'] | ['1 CO2* 1', '2 * 1'] | 1.249     |          | [240.448231, 83.18955, 80.04067, 61.668486, 59.849388, 38.271338, 36.143131, 12.378844, 10.126178] | [171.188002, 145.668886, 96.963691, 86.25514, 56.201368, 52.375682, 35.933392, 24.342963, 21.024922] | [217.940927, 81.361728, 66.833494, 56.917831, 50.342099, 37.430358, 19.074043, 12.356398] |             |
| CO_diffusion   | topC topC  | 1-2         |           | ['1 CO* 1', '2 * 1']  | ['1 * 1', '2 CO* 1']  | 1.156     |          | [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]                                  | [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]                                    | [218.382388, 53.526855, 47.6122, 28.580404, 6.599679]                                     |             |
| O_diffusion    | topC topC  | 1-2         |           | ['1 O* 1', '2 * 1']   | ['1 * 1', '2 O* 1']   | 1.221     |          | [78.662275, 40.796289, 40.348665]                                                                  | [78.662275, 40.796289, 40.348665]                                                                    | [56.617104, 49.715199]                                                                    |             |

Note that the keyword `sites` in the `mechanism_input.dat` file is calculated automatically from the lattice state.

This `pandas.DataFrame` can be created, for instance, by including all the information in a `.csv` file and reading it:

```python
import pandas as pd

mechanism_data=pd.read_csv('mechanism_data.csv', index_col=0)
```

Alternatively, it can be created from a `dict`:

```python
import pandas as pd

steps = {
    'CO_adsorption': {
        'sites': 1,
        'site_types': 'topC',
        'neighboring': '',
        'area_site': 5.34,
        'initial': ['1 * 1'],
        'final': ['1 CO* 1'],
        'activ_eng': 0.0,
        'molecule': 'CO',
        'vib_energies_is': [264.160873],
        'vib_energies_fs': [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359],
        'vib_energies_ts': [],
        'prox_factor': 0.0},
    'O2_adsorption': {
        'sites': 2,
        'site_types': 'topC topC',
        'neighboring': '1-2',
        'area_site': 5.34,
        'initial': ['1 * 1', '2 * 1'],
        'final': ['1 O* 1', '2 O* 1'],
        'activ_eng': 0.0,
        'molecule': 'O2',
        'vib_energies_is': [194.973022],
        'vib_energies_fs': [79.738187, 77.981497, 40.487926, 39.798116, 38.056578, 37.441762],
        'vib_energies_ts': [],
        'prox_factor': 0.0}
}

mechanism_data = pd.DataFrame(steps).T
```

## 3. Energetics Model

The information on the energetics model is contained in a `pandas.DataFrame`, where each row corresponds to a cluster.

```{important}
The row index has to be the name of the cluster.
```

### Columns

**Mandatory:**

- **cluster_eng** (*float*): Cluster formation energy (in eV).
- **site_types** (*str*): The types of each site in the pattern.
- **lattice_state** (*list*): Cluster configuration in Zacros format.
  - Example: `['1 CO* 1','2 CO* 1']`.

Note that the keyword `sites` in the `energetics_input.dat` file is calculated automatically from the lattice state.

**Optional:**

- **neighboring** (*str*): Connectivity between sites involved.
  - Example: `1-2`. 
  - Default value: `None`.
- **angles** (*str*): Angle between sites in Zacros format.
  - Example: `'1-2-3:180'`. 
  - Default value: `None`.
- **graph_multiplicity** (*int*): Symmetry number of the cluster. 
  - Default value: `1`.

```{caution}
The **cluster_eng** must not include the ZPE. For the single-body terms, the ZPE is included in the pre-exponential 
factor. For the multi-body terms (lateral interactions), the ZPE should be ignored.
```

### Example

| index        | cluster_eng | site_types | lattice_state            | neighboring | graph_multiplicity |
|--------------|-------------|------------|--------------------------|-------------|--------------------|
| CO2_point    | -1.576      | tC         | ['1 CO2* 1']             |             |                    |
| CO_point     | 0.233       | tC         | ['1 CO* 1']              |             |                    |
| O_point      | -1.333      | tC         | ['1 O* 1']               |             |                    |
| CO2+CO2_pair | -0.062      | tC tC      | ['1 CO2* 1', '2 CO2* 1'] | 1-2         | 2                  |
| CO2+CO_pair  | -0.184      | tC tC      | ['1 CO2* 1', '2 CO* 1']  | 1-2         |                    |
| CO2+O_pair   | -0.162      | tC tC      | ['1 CO2* 1', '2 O* 1']   | 1-2         |                    |
| CO+CO_pair   | 0.177       | tC tC      | ['1 CO* 1', '2 CO* 1']   | 1-2         | 2                  |
| CO+O_pair    | -0.032      | tC tC      | ['1 CO* 1', '2 O* 1']    | 1-2         |                    |
| O+O_pair     | 0.034       | tC tC      | ['1 O* 1', '2 O* 1']     | 1-2         | 2                  |

This `pandas.DataFrame` can be created, for instance, by including all the information in a `.csv` file and reading it:

```python
import pandas as pd

energetics_data = pd.read_csv('energetics.csv', index_col=0)
```

Alternatively, it can be created from a `dict`:

```python
import pandas as pd

clusters = {
    'CO_point': {
        'site_types': 'tC',
        'lattice_state': ['1 CO* 1'],
        'cluster_eng': 0.233},
    'CO+CO_pair': {
        'site_types': 'tC tC',
        'neighboring': '1-2',
        'lattice_state': ['1 CO* 1', '2 CO* 1'],
        'cluster_eng': 0.177}
}

energetics_data = pd.DataFrame(clusters).T
```

## 4. Lattice model

Finally, a `LatticeModel` object ({py:func}`zacrostools.lattice_input.LatticeModel`) is needed to create a `KMCModel`.
Currently, the only way to create a `LatticeModel` is by reading a `lattice_input.dat` file:

```python
from zacrostools.lattice_input import LatticeModel

lattice_model = LatticeModel.from_file(filepath='lattice_inputs/lattice_input_for_HfC.dat')
```

In future releases, the user will be able to create a `LatticeModel` file directly from `ZacrosTools`.

Example of a lattice input file for HfC(001):

<div style="text-align: center;">
    <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/lattice.png?raw=true" alt="lattice" width="300"/>
</div>

    # lattice_input_for_HfC.dat file

    lattice periodic_cell
    
       cell_vectors
       3.27 0.00
       0.00 3.27
       repeat_cell 10 10
       n_cell_sites 2
       n_site_types 2
       site_type_names topHf topC
       site_types topHf topC
       site_coordinates
          0.25 0.25
          0.75 0.75
       neighboring_structure
          1-2 self
          1-1 north
          2-1 north
          2-2 north
          1-1 east
          2-1 east
          2-2 east
          2-1 northeast
       end_neighboring_structure
    
    end_lattice

## 5. Create a KMC model

With all the required information, the `KMCModel` object can be created:

```python
from zacrostools.kmc_model import KMCModel

kmc_model = KMCModel(gas_data=gas_data,
                     mechanism_data=mechanism_data,
                     energetics_data=energetics_data,
                     lattice_model=lattice_model)
```

## 6. Write Zacros Input Files

Once the `KMCModel` is created, the Zacros input files for the desired operating conditions can be generated using the 
`zacrostools.kmc_model.KMCModel.create_job_dir` function. This function also includes parameters for the reporting 
scheme, stopping criteria, and scaling of reaction rates for fast events.

### Arguments

**Mandatory:**

- **path** (*str*): Path for the new directory where the input files will be written. This directory will be created by 
ZacrosTools.
- **temperature** (*float*): Reaction temperature (in K).
- **pressure** (*dict*): Partial pressures of all gas species (in bar).
  - Example: `{'CO': 1.0, 'O2': 0.001}`.

**Optional:**

- **reporting_scheme** (*dict*): Reporting scheme in Zacros format. 
  - Must contain the following keys: `'snapshots'`, `'process_statistics'`, and `'species_numbers'`. 
  - Default value: `{'snapshots': 'on event 10000', 'process_statistics': 'on event 10000', 'species_numbers': 'on event 10000'}`.
- **stopping_criteria** (*dict*): Stopping criteria in Zacros format. 
  - Must contain the following keys: `'max_steps'`, `'max_time'`, and `'wall_time'`. 
  - Default value: `{'max_steps': 'infinity', 'max_time': 'infinity', 'wall_time': 86400}`.
- **manual_scaling** (*list*): Step names (keys) and their corresponding manual scaling factors (values). 
  - Example: `{'CO_diffusion': 1.0e-1, 'O_diffusion': 1.0e-2}`. 
  - Default value: `{}`.
- **auto_scaling_steps** (*list*): Steps that will be marked as `stiffness_scalable` in `mechanism_input.dat`. 
  - Example: `['CO_diffusion', 'O_diffusion']`. 
  - Default value: `[]`.
- **auto_scaling_tags** (*dict*): Keywords controlling the dynamic scaling algorithm and their corresponding values. 
  - Example: `{'check_every': 2000, 'min_separation': 200.0, 'max_separation': 600.0}`. 
  - Default value: `{}` (Zacros default values).
- **sig_figs_energies** (*int*): Number of significant figures used when writing `gas_energies` in the 
`simulation_input.dat`, `cluster_eng` in the `energetics_input.dat`, and `activ_eng` in `mechanism_input.dat`. 
  - Default value: `16`.
- **sig_figs_pe** (*int*): Number of significant figures used when writing `pre_expon` and `pe_ratio` in `mechanism_input.dat`. 
  - Default value: `16`.
- **random_seed** (*int*): Integer seed of the random number generator. If not specified, ZacrosTools will generate one. 
  - Default value: `None`.

For instance, to run a scan over a range of temperatures and partial pressures, the following loop can be used to create
 all input files:

```python
import os
import numpy as np

reporting_scheme={'snapshots': 'on event 10000', 
                  'process_statistics': 'on event 10000', 
                  'species_numbers': 'on event 10000'}

stopping_criteria={'max_steps': 'infinity', 'max_time': 'infinity', 'wall_time': 43200}

for temperature in np.linspace(500, 800, 4):
    scan_folder_name = f'scan_{int(temperature)}K'
    os.makedirs(scan_folder_name, exist_ok=True)
    for pCO in np.logspace(-3, 1, 10):
        for pO in np.logspace(-6, -2, 10):
            kmc_model.create_job_dir(path=f"{scan_folder_name}/pCO_{pCO:.3e}_pO_{pO:.3e}",
                                     temperature=temperature,
                                     pressure={'CO': pCO, 'O': pO, 'CO2': 0.0},
                                     reporting_scheme=reporting_scheme,
                                     stopping_criteria=stopping_criteria,
                                     sig_figs_energies=3,
                                     sig_figs_pe=3)
```

```{warning}
This section of the documentation is under development.
```
