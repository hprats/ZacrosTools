# ZacrosTools

> [!WARNING]  
> This project is under development. The documentation is in preparation.

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

In ZacrosTools, a KMC model is represented as a KMCModel object `zacrostools.kmc_model.KMCModel`. 
In order to use ZacrosTools, three Pandas DataFrames have to be prepared in advance:

|      Name       |     Information      |
|:---------------:|:--------------------:|
|    gas_data     | gas species involved |
| mechanism_data  |    reaction model    |
| energetics_data |   energetics model   | 

The information required in each of these DataFrames is the following: 

### 1. gas_data

One row for every gas-phase species. The row index has to be the name of the species. 

The following columns are required:
- **type** (*str*): 'non_linear' or 'linear'
- **gas_molec_weight** (*float*): molecular weights (in amu) of the gas species
- **sym_number** (*int*): symmetry number of the molecule
- **degeneracy** (*int*): degeneracy of the ground state, for the calculation of the electronic partition
  function. Default value: 1
- **intertia_moments** (*list*): moments of inertia for the gas-phase molecule (in amu·Å^2).
  1 element for linear molecules, 3 elements for non-linear molecules.
  Can be obtained from ase.Atoms.get_moments_of_inertia()
- **gas_energy** (*float*): formation energy (in eV)

Example:

| index |type      |gas_molec_weight| sym_number | degeneracy | inertia_moments      |gas_energy|
|-------|----------|----------------|------------|------------|----------------------|----------|
| CO    |linear    |28.01           | 1          | 1          | [8.973619026272551]  |1.96      |
| O2    |linear    |32.0            | 2          | 3          | [12.178379354326061] |2.6       |


### 2. mechanism_data

One row for every elementary step. The row index has to be the name of the step.

The following columns are required:
- **site_types** (*str*): the types of each site in the pattern
- **initial** (*list*): initial configuration in Zacros format, e.g. ['1 CO* 1','2 * 1']
- **final** (*list*): final configuration in Zacros format, e.g. ['1 C* 1','2 O* 1']
- **activ_eng** (*float*): activation energy (in eV)
- **vib_energies_is** (*list*): vibrational energies for the initial state (in meV)
- **vib_energies_ts** (*list*): vibrational energies for the transition state (in meV).
  For non-activated adsorption, define this as an empty list i.e. []
- **vib_energies_fs** (*list*): vibrational energies for the final state (in meV)
- **molecule** (*str*): gas-phase molecule involved. Only required for adsorption steps. Default value: None
- **area_site** (*float*): area of adsorption site (in Å^2). Only required for adsorption steps.
  Default value: None

The following columns are optional:
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
| CO_dissociation | 2     | topC topC  |1-2        |         | ['1 CO* 1', '2 * 1']  | ['1 C* 1', '2 O* 1']  |2.176    |          | [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]                                  | [138.064404, 78.64274, 39.644889, 38.175445, 32.997051, 23.89371]                                    | [129.799624, 55.940895, 41.760039, 33.292377, 20.816034]                                  |           |
| CO_diffusion    | 2     | topC topC  |1-2        |         | ['1 CO* 1', '2 * 1']  | ['1 * 1', '2 CO* 1']  |1.156    |          | [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]                                  | [240.497465, 82.738219, 60.132962, 60.080258, 7.271753, 6.553359]                                    | [218.382388, 53.526855, 47.6122, 28.580404, 6.599679]                                     |           |
| C_diffusion     | 2     | topC topC  |1-2        |         | ['1 C* 1', '2 * 1']   | ['1 * 1', '2 C* 1']   |1.449    |          | [138.207451, 24.592242, 17.986572]                                                                 | [138.207451, 24.592242, 17.986572]                                                                   | [85.015794, 66.512731]                                                                    |           |
| O_diffusion     | 2     | topC topC  |1-2        |         | ['1 O* 1', '2 * 1']   | ['1 * 1', '2 O* 1']   |1.221    |          | [78.662275, 40.796289, 40.348665]                                                                  | [78.662275, 40.796289, 40.348665]                                                                    | [56.617104, 49.715199]                                                                    |           |

### 3. energetics_data

One row for every cluster. The row index has to be the name of the cluster.

> [!TIP]  
> It is recommended to add *_point* at the end of the cluster name for one-body terms (e.g. *CO_point*), and *_pair* 
> at the end of the name for two-body terms (e.g. *CO+CO_pair*).

The following columns are required:
- **cluster_eng** (*float*): cluster formation energy (in eV)
- **site_types** (*str*): the types of each site in the pattern
- **lattice_state** (*list*): cluster configuration in Zacros format, e.g. ['1 CO* 1','2 CO* 1']
The following columns are optional:
- **neighboring** (*str*): connectivity between sites involved, e.g. 1-2. Default value: None
- **angles** (*str*): Angle between sites in Zacros format, e.g. '1-2-3:180'. Default value: None
- **graph_multiplicity** (*int*): symmetry number of the cluster, e.g. 2. Default value: 1

Example:

| index        |cluster_eng| sites |site_types|lattice_state             |neighboring| graph_multiplicity |
|--------------|-----------|-------|----------|--------------------------|-----------|--------------------|
| CO2_point    |-1.576     | 1     |tC        |['1 CO2* 1']              |           |                    |
| CO_point     |0.233      | 1     |tC        |['1 CO* 1']               |           |                    |
| C_point      |2.452      | 1     |tC        |['1 C* 1']                |           |                    |
| O_point      |-1.333     | 1     |tC        |['1 O* 1']                |           |                    |
| CO2+CO2_pair |-0.062     | 2     |tC tC     |['1 CO2* 1', '2 CO2* 1']  |1-2        | 2                  |
| CO2+CO_pair  |-0.184     | 2     |tC tC     |['1 CO2* 1', '2 CO* 1']   |1-2        |                    |
| CO2+C_pair   |-0.168     | 2     |tC tC     |['1 CO2* 1', '2 C* 1']    |1-2        |                    |
| CO2+O_pair   |-0.162     | 2     |tC tC     |['1 CO2* 1', '2 O* 1']    |1-2        |                    |
| CO+CO_pair   |0.177      | 2     |tC tC     |['1 CO* 1', '2 CO* 1']    |1-2        | 2                  |
| CO+C_pair    |0.117      | 2     |tC tC     |['1 CO* 1', '2 C* 1']     |1-2        |                    |
| CO+O_pair    |-0.032     | 2     |tC tC     |['1 CO* 1', '2 O* 1']     |1-2        |                    |
| C+C_pair     |0.096      | 2     |tC tC     |['1 C* 1', '2 C* 1']      |1-2        | 2                  |
| C+O_pair     |-0.036     | 2     |tC tC     |['1 C* 1', '2 O* 1']      |1-2        |                    |
| O+O_pair     |0.034      | 2     |tC tC     |['1 O* 1', '2 O* 1']      |1-2        | 2                  |

### Lattice model

Finally, a lattice model is needed to create a KMCModel. Currently, the only way to create a lattice model is by reading
a lattice_input.dat file:

    from zacrostools.lattice_input import LatticeModel

    lattice_model = LatticeModel.from_file('lattice_inputs/lattice_input_Ni111.dat')

Example:

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


## Contributors

Hector Prats