# 4. Create a Lattice Model

The `LatticeModel` represents the lattice structure on which adsorbates can bind, and supports different lattice types:

- **`default_choice`**: Predefined lattice structures (e.g., triangular, rectangular or hexagonal).
- **`periodic_cell`**: Custom periodic unit cells with specified cell vectors and sites.
- **`explicit`**: Explicitly defined lattice structures (not yet implemented).

#### Allowed lattice types

- `'default_choice'`
- `'periodic_cell'`
- `'explicit'` (Note: As per the current implementation, `'explicit'` is not yet supported.)

---

#### How to create it

There are three primary ways to create a `LatticeModel`, as detailed below.

##### Using a default lattice

This method allows you to select from predefined lattice types and specify basic parameters. 

Required parameters:
- **`lattice_type`**: Set to `'default_choice'`.
- **`default_lattice_type`** (`str`): Choose from `'triangular_periodic'`, `'rectangular_periodic'`, or `'hexagonal_periodic'`.
- **`lattice_constant`** (`float`): The lattice constant (Å).
- **`copies`** (`List[int]`): Number of repetitions along the horizontal and vertical directions.

```python
from zacrostools.lattice_model import LatticeModel

lattice_model = LatticeModel(
    lattice_type='default_choice',
    default_lattice_type='triangular_periodic',
    lattice_constant=2.5,
    copies=[10, 10]
)
```

##### Defining a custom periodic cell

This method allows you to define a custom lattice by specifying the unit cell vectors, site types, and neighboring structures.

Required parameters:
- **`lattice_type`**: Set to `'periodic_cell'`.
- **`cell_vectors`** (`Tuple[Tuple[float, float], Tuple[float, float]]`): Two vectors defining the unit cell.
- **`sites`** (`Dict[str, Union[Tuple[float, float], List[Tuple[float, float]]]]`): Mapping of site types to their coordinates within the unit cell.
- **`coordinate_type`** (`str`, optional): `'direct'` or `'cartesian'`. Defaults to `'direct'`.
- **`copies`** (`List[int]`): Number of repetitions along the horizontal and vertical directions.
- **`neighboring_structure`** (`Union[str, Dict[str, Union[str, List[str]]]]`): Defines the neighboring relationships between sites.
  - If set to `'from_distances'`, you must provide `max_distances`.
  - If providing a dictionary, it maps site pairs to a list of relationship keywords.
- **`max_distances`** (`Dict[str, float]`, required if `neighboring_structure='from_distances'`): Defines maximum distances for neighbor pairs.

The following examples show two different ways to create the lattice model for a HfC(001) surface, as described in the image below:

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/lattice_model_HfC.png?raw=true" alt="Molecules produced" width="500"/> </div>

1. Specifying a neighboring structure:

```python
from zacrostools.lattice_model import LatticeModel

# Define cell vectors
cell_vectors = ((3.27, 0.0), (0.0, 3.27))

# Define site positions
sites = {
    'tC': [(0.25, 0.25)],
    'tM': [(0.75, 0.75)]
}

# Define neighboring structure directly
neighboring_structure = {
    '1-2': ['self'],
    '1-1': ['north', 'east'],
    '2-1': ['north', 'east', 'northeast'],
    '2-2': ['north', 'east']
}

# Create the LatticeModel instance
lattice_model = LatticeModel(
    lattice_type='periodic_cell',
    cell_vectors=cell_vectors,
    sites=sites,
    coordinate_type='direct',
    copies=[10, 10],
    neighboring_structure=neighboring_structure
)
```

2. Generating the neighboring structure automatically

```python
from zacrostools.lattice_model import LatticeModel

# Define cell vectors
cell_vectors = ((3.27, 0.0), (0.0, 3.27))

# Define site positions
sites = {
    'tC': [(0.25, 0.25)],
    'tM': [(0.75, 0.75)]
}

# Define maximum distances for neighbor pairs
max_distances = {
    'tC-tC': 3.0,
    'tM-tM': 3.0,
    'tC-tM': 3.0
}

# Create the LatticeModel instance
lattice_model = LatticeModel(
    lattice_type='periodic_cell',
    cell_vectors=cell_vectors,
    sites=sites,
    coordinate_type='direct',
    copies=[10, 10],
    neighboring_structure='from_distances',
    max_distances=max_distances
)
```

##### Loading from an existing lattice input file

This method allows you to create a `LatticeModel` by reading a previously created `lattice_input.dat` file. This is particularly useful when you want to reuse lattice configurations or when the lattice file was provided by another user.

Required parameters:
- **`input_file`** (`str` or `Path`): Path to the existing `lattice_input.dat` file.

```python
from zacrostools.lattice_model import LatticeModel

lattice_model = LatticeModel.from_file(input_file='path/to/lattice_input.dat')
```

Notes for this method:
- It reads the `lattice` block from the file, which starts with the `lattice` keyword and ends with `end_lattice`.
- Supports `'default_choice'` and `'periodic_cell'` lattice types.
- If the lattice type is `'explicit'`, a `LatticeModelError` will be raised as this type is not yet supported.
- Ignores any content outside the `lattice` block.


---

#### Repeating the `LatticeModel`

You can expand the unit cell by repeating it along the cell vectors.

Required parameters:
- **`a`** (`int`): Number of repetitions along the first cell vector.
- **`b`** (`int`): Number of repetitions along the second cell vector.

```python
# Repeat the lattice 2 times along alpha and 3 times along beta
lattice_model.repeat_lattice_model(a=2, b=3)
```

#### Removing a site

You can remove a specific site based on its coordinates.

Required parameters:
- **`direct_coords`** (`Tuple[float, float]`): The direct coordinates of the site to remove.
- **`tolerance`** (`float`, optional): Tolerance for coordinate matching.

```python
# Remove a site at position (0.5, 0.5)
lattice_model.remove_site(direct_coords=(0.5, 0.5))
```

#### Changing the site type

Required parameters:
- **`direct_coords`** (`Tuple[float, float]`): The direct coordinates of the site.
- **`new_site_type`** (`str`): The new site type to assign.
- **`tolerance`** (`float`, optional): Tolerance for coordinate matching.

```python
# Change the site type at position (0.0, 0.0) to 'B'
lattice_model.change_site_type(direct_coords=(0.0, 0.0), new_site_type='B')
```

---

#### Writing the `lattice_input.dat` file

The `LatticeModel` can generate the `lattice_input.dat` file required by Zacros.

### Method

```python
lattice_model.write_lattice_input(output_dir, sig_figs=8)
```

- **`output_dir`** (`str` or `Path`): Directory where the file will be written.
- **`sig_figs`** (`int`, optional): Number of significant figures for numerical values.

#### Example

```python
# Write the lattice_input.dat file to the specified directory
lattice_model.write_lattice_input(output_dir='kmc_simulation')
```

---

## Full example

This example shows how to create a lattice model for a Pt4 cluster supported on a HfC(001) surface, as described in the image below:

<div style="text-align: center;"> <img src="https://github.com/hprats/ZacrosTools/blob/main/docs/images/lattice_model_PtHfC.png?raw=true" alt="Molecules produced" width="600"/> </div>

```python
from zacrostools.lattice_model import LatticeModel

# Create a unit cell for PtHfC unit cell from a 4x4 cell of HfC
lattice_model = LatticeModel(
    lattice_type='periodic_cell',
    cell_vectors=((3.27, 0), (0, 3.27)),
    sites={'tC': (0.25, 0.25), 'tM': (0.75, 0.75)},
    copies=[10, 10],
    neighboring_structure='from_distances',
    max_distances={'tC-tC': 4.0, 'tC-tM': 4.0, 'tM-tM': 4.0, 'Pt-Pt': 4.0, 'Pt-tC': 4.0, 'Pt-tM': 4.0},
)
lattice_model.repeat_lattice_model(4, 4)

# Replace four tC sites by Pt sites
for coordinates in [(0.3125, 0.3125), (0.3125, 0.5625), (0.5625, 0.3125), (0.5625, 0.5625)]:
    lattice_model.change_site_type(direct_coords=coordinates, new_site_type='Pt') 

# Remove the tM site in the middle of the four Pt sites
lattice_model.remove_site(direct_coords=(0.4375, 0.4375)) 

# Define the number of copies of the unit cell for the simulation
lattice_model.copies = [3, 3]

# Write the lattice_input.dat file in a folder named 'PtHfC'
lattice_model.write_lattice_input(output_dir='PtHfC')
```

---

## Next steps

- Assemble the `KMCModel`
