# ZacrosTools

```{warning}
This project is under development.
```

ZacrosTools is a simple toolkit for the preparation of **[Zacros](https://zacros.org/)** input files. It is specially 
useful when running scans at different pressure and temperature conditions, which may require hundreds of KMC 
simulations.

## Installation

The easiest way to install ZacrosTools is by using pip:
```{code-block}
$ pip install zacrostools
```
Alternatively, it can also be cloned from [GitHub](https://github.com/hprats/ZacrosTools):
```{code-block}
$ git clone https://github.com/hprats/ZacrosTools.git
```
The only requirements are [scipy](https://scipy.org/) and [pandas](https://pandas.pydata.org/).

## How to use it

In ZacrosTools, a KMC model is represented as a KMCModel object {py:func}`zacrostools.kmc_model.KMCModel`. 
To create a KMCModel object, the user has to supply information on the gas-phase species involved, a reaction model,
an energetics model, and a lattice model.

### Creating a new KMC model in ZacrosTools

#### 1. Prepare the information on the gas-phase species 

This information has to be contained in a Pandas DataFrame, where each row corresponds to a gas-phase molecule. 
The row index has to be the name of the species. 

```{important}
The row index has to be the name of the species.
```

The following columns are **mandatory**:
- **type** (*str*): 'non_linear' or 'linear'
- **gas_molec_weight** (*float*): molecular weights (in amu) of the gas species
- **sym_number** (*int*): symmetry number of the molecule
- **degeneracy** (*int*): degeneracy of the ground state, for the calculation of the electronic partition
  function. Default value: 1
- **intertia_moments** (*list*): moments of inertia for the gas-phase molecule (in amu·Å<sup>2</sup>).
  1 element for linear molecules, 3 elements for non-linear molecules.
  Can be obtained from ase.Atoms.get_moments_of_inertia()
- **gas_energy** (*float*): formation energy (in eV)

Example:

| index  | type    |gas_molec_weight| sym_number | degeneracy | inertia_moments      | gas_energy |
|--------|---------|----------------|------------|------------|----------------------|------------|
| CO     | linear  |28.01           | 1          | 1          | [8.973619026272551]  | 1.96       |
| O2     | linear  |32.0            | 2          | 3          | [12.178379354326061] | 2.6        |
| CO2    | linear  |44.01           | 2.0        | 1.0        | [44.317229117708344] | 0.0        |


#### 2. Prepare a reaction model

The information on the reaction model is contained in a second DataFrame, where each row corresponds to an elementary
step.

```{important}
The row index has to be the name of the step.
```

The following columns are **mandatory**:
- **site_types** (*str*): the types of each site in the pattern
- **initial** (*list*): initial configuration in Zacros format, e.g. ['1 CO* 1','2 * 1']
- **final** (*list*): final configuration in Zacros format, e.g. ['1 C* 1','2 O* 1']
- **activ_eng** (*float*): activation energy (in eV)
- **vib_energies_is** (*list*): vibrational energies for the initial state (in meV)
- **vib_energies_ts** (*list*): vibrational energies for the transition state (in meV).
  For non-activated adsorption, define this as an empty list i.e. []
- **vib_energies_fs** (*list*): vibrational energies for the final state (in meV)
- **molecule** (*str*): gas-phase molecule involved. Only required for adsorption steps. Default value: None
- **area_site** (*float*): area of adsorption site (in Å<sup>2</sup>). Only required for adsorption steps.
  Default value: None

The following columns are **optional**:
- **neighboring** (*str*): connectivity between sites involved, e.g. 1-2. Default value: None
- **prox_factor** (*float*): proximity factor. Default value: 0.5
- **angles** (*str*): Angle between sites in Zacros format, e.g. '1-2-3:180'. Default value: None

Example:

| index           | sites | site_types |neighboring|area_site| initial               | final                 |activ_eng| molecule | vib_energies_is                                                                                    | vib_energies_fs                                                                                      | vib_energies_ts                                                                           |prox_factor|
|-----------------|-------|------------|-----------|---------|-----------------------|-----------------------|---------|----------|----------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|-----------|
| CO_adsorption   | 1     | topC       |           |5.34     | ['1 * 1']             | ['1 CO* 1']           |0.0      | CO       | [264.160873]                                                                                       | [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]                                    | []                                                                                        |0.0        |
| O2_adsorption   | 2     | topC topC  |1-2        |5.34     | ['1 * 1', '2 * 1']    | ['1 O* 1', '2 O* 1']  |0.0      | O2       | [194.973022]                                                                                       | [79.738187, 77.981497, 40.487926, 39.798116, 38.056578, 37.441762]                                   | []                                                                                        |0.0        |
| CO2_adsorption  | 1     | topC       |           |5.34     | ['1 * 1']             | ['1 CO2* 1']          |0.0      | CO2      | [294.059036, 163.752147, 78.494148, 78.310738]                                                     | [171.188002, 145.668886, 96.963691, 86.25514, 56.201368, 52.375682, 35.933392, 24.342963, 21.024922] | []                                                                                        |0.0        |
| CO+O_reaction   | 2     | topC topC  |1-2        |         | ['1 CO* 1', '2 O* 1'] | ['1 CO2* 1', '2 * 1'] |1.249    |          | [240.448231, 83.18955, 80.04067, 61.668486, 59.849388, 38.271338, 36.143131, 12.378844, 10.126178] | [171.188002, 145.668886, 96.963691, 86.25514, 56.201368, 52.375682, 35.933392, 24.342963, 21.024922] | [217.940927, 81.361728, 66.833494, 56.917831, 50.342099, 37.430358, 19.074043, 12.356398] |           |
| CO_diffusion    | 2     | topC topC  |1-2        |         | ['1 CO* 1', '2 * 1']  | ['1 * 1', '2 CO* 1']  |1.156    |          | [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]                                  | [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]                                    | [218.382388, 53.526855, 47.6122, 28.580404, 6.599679]                                     |           |
| O_diffusion     | 2     | topC topC  |1-2        |         | ['1 O* 1', '2 * 1']   | ['1 * 1', '2 O* 1']   |1.221    |          | [78.662275, 40.796289, 40.348665]                                                                  | [78.662275, 40.796289, 40.348665]                                                                    | [56.617104, 49.715199]                                                                    |           |

#### 3. Prepare an energetics model

The information on the energetics model is contained in a third DataFrame, where each row corresponds to an cluster.

```{important}
The row index has to be the name of the cluster. 
```

The following columns are **mandatory**:
- **cluster_eng** (*float*): cluster formation energy (in eV)
- **site_types** (*str*): the types of each site in the pattern
- **lattice_state** (*list*): cluster configuration in Zacros format, e.g. ['1 CO* 1','2 CO* 1']

The following columns are **optional**:
- **neighboring** (*str*): connectivity between sites involved, e.g. 1-2. Default value: None
- **angles** (*str*): Angle between sites in Zacros format, e.g. '1-2-3:180'. Default value: None
- **graph_multiplicity** (*int*): symmetry number of the cluster, e.g. 2. Default value: 1

Example:

| index        |cluster_eng| sites |site_types|lattice_state             |neighboring| graph_multiplicity |
|--------------|-----------|-------|----------|--------------------------|-----------|--------------------|
| CO2_point    |-1.576     | 1     |tC        |['1 CO2* 1']              |           |                    |
| CO_point     |0.233      | 1     |tC        |['1 CO* 1']               |           |                    |
| O_point      |-1.333     | 1     |tC        |['1 O* 1']                |           |                    |
| CO2+CO2_pair |-0.062     | 2     |tC tC     |['1 CO2* 1', '2 CO2* 1']  |1-2        | 2                  |
| CO2+CO_pair  |-0.184     | 2     |tC tC     |['1 CO2* 1', '2 CO* 1']   |1-2        |                    |
| CO2+O_pair   |-0.162     | 2     |tC tC     |['1 CO2* 1', '2 O* 1']    |1-2        |                    |
| CO+CO_pair   |0.177      | 2     |tC tC     |['1 CO* 1', '2 CO* 1']    |1-2        | 2                  |
| CO+O_pair    |-0.032     | 2     |tC tC     |['1 CO* 1', '2 O* 1']     |1-2        |                    |
| O+O_pair     |0.034      | 2     |tC tC     |['1 O* 1', '2 O* 1']      |1-2        | 2                  |


#### 4. Prepare a lattice model

Finally, a lattice model is needed to create a KMCModel. The lattice model is stored as a 
{py:func}`zacrostools.lattice_input.LatticeModel` object. 
Currently, the only way to create a lattice model is by reading a lattice_input.dat file:

    from zacrostools.lattice_input import LatticeModel

    lattice_model = LatticeModel.from_file('lattice_inputs/lattice_input_for_HfC.dat')

Example:

![lattice](https://github.com/hprats/ZacrosTools/blob/main/images/lattice.png?raw=true)


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

#### 5. Create the KMC model

With all this information, a KMC model can be created as follows:

    from zacrostools.kmc_model import KMCModel
    from zacrostools.lattice_input import LatticeModel
    
    kmc_model = KMCModel(gas_data=pd.read_csv(f'gas_data.csv', index_col=0),
                         mechanism_data=pd.read_csv(f'mechanism.csv', index_col=0),
                         energetics_data=pd.read_csv(f'energetics.csv', index_col=0),
                         lattice_model=LatticeModel.from_file(path=f"lattice_input_for_HfC.dat"))

### Generation of Zacros input files

Once the KMC model is created, the user can generate all the Zacros input files at a range of temperatures and partial
pressures as follows:

    for pCO in np.logspace(-3, 1, 10):
        for pO in np.logspace(-6, -2, 10):
            for temperature in np.linspace(500, 800, 10):
                kmc_model.create_job_dir(path=f"pCO_{pCO:.3e}_pO_{pO:.3e}_T_{temperature:.3f}",
                                         temperature=temperature,
                                         pressure={'CO': pCO, 'O': pO, 'CO2': 0.0},
                                         report='on event 10000',
                                         stop={'max_steps': 'infinity', 'max_time': 'infinity', 'wall_time': 86400})

The {py:func}`zacrostools.kmc_model.KMCModel.create_job_dir` function allows to select the reporting parameters, the 
stopping criteria, as well as manual scaling factors for specific steps or enabling automatic scaling for fast 
processes.

### Creating a DataFrame

#### From Python dictionaries

The required DataFrames can be created from Python dictionaries as follows:

##### Gas-phase species

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
               'gas_energy': 2.60}}
    
    gas_data = pd.DataFrame()
    new_row = pd.Series([], dtype='object')
    for molecule in gas_molecules:
        new_row = pd.Series(gas_molecules[molecule])
        new_row.name = molecule
        gas_data = pd.concat([gas_data, new_row.to_frame().T])

##### Reaction model

    import pandas as pd
    
    steps = {
        'CO_adsorption': {'site_types': 'tC',
                          'initial': ['1 * 1'],
                          'final': ['1 CO* 1'],
                          'activ_eng': 0.0,
                          'vib_energies_is': [264.16],
                          'vib_energies_ts': [],
                          'vib_energies_fs': [240.50, 82.74, 60.13, 60.08, 7.27, 6.55],
                          'molecule': 'CO',
                          'area_site': 5.34,
                          'prox_factor': 0.0},
        'CO+O_reaction': {'site_types': 'tC tC',
                          'initial': ['1 CO* 1', '2 O* 1'],
                          'final': ['1 CO2* 1', '2 * 1'],
                          'activ_eng': 1.249,
                          'vib_energies_is': [240.45, 83.19, 80.04, 61.66, 59.84, 38.27, 36.14, 12.37, 10.12],
                          'vib_energies_ts': [217.94, 81.36, 66.83, 56.91, 50.34, 37.43, 19.07, 12.35],
                          'vib_energies_fs': [171.18, 145.66, 96.96, 86.25, 56.20, 52.37, 35.93, 24.34, 21.02],
                          'neighboring': '1-2'}}
    
    reaction_data = pd.DataFrame()
    new_row = pd.Series([], dtype='object')
    for step in steps:
        new_row = pd.Series(steps[step])
        new_row.name = step
        reaction_data = pd.concat([reaction_data, new_row.to_frame().T])

##### Energetic model

    import pandas as pd
    
    clusters = {
        'CO_point': {'site_types': 'tC',
                     'lattice_state': ['1 CO* 1'],
                     'cluster_eng': 0.233},
        'CO+CO_pair': {'site_types': 'tC tC',
                       'neighboring': '1-2',
                       'lattice_state': ['1 CO* 1', '2 CO* 1'],
                       'cluster_eng': 0.177}}
    
    energetics_data = pd.DataFrame()
    new_row = pd.Series([], dtype='object')
    for cluster in clusters:
        new_row = pd.Series(clusters[cluster])
        new_row.name = cluster
        energetics_data = pd.concat([energetics_data, new_row.to_frame().T])

## Contributors

Hector Prats

## API

```{eval-rst}
.. autofunction:: zacrostools.kmc_model.KMCModel
```

```{eval-rst}
.. autofunction:: zacrostools.kmc_model.KMCModel.create_job_dir
```

```{eval-rst}
.. autofunction:: zacrostools.lattice_input.LatticeModel
```
