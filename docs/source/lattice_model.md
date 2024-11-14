# Lattice Model

The `LatticeModel` class in ZacrosTools represents the lattice structure on which the Kinetic Monte Carlo (KMC) simulation will run. It allows you to define various types of lattices, specify site types and coordinates, and set up neighboring structures. This flexibility enables modeling of complex surface geometries and interactions in Zacros simulations.

## Overview

The `LatticeModel` supports different lattice types:

- **`default_choice`**: Predefined lattice structures (e.g., triangular, rectangular).
- **`periodic_cell`**: Custom periodic unit cells with specified cell vectors and sites.
- **`explicit`**: Explicitly defined lattice structures (not yet implemented).

### Allowed Lattice Types

- `'default_choice'`
- `'periodic_cell'`
- `'explicit'` (Note: As per the current implementation, `'explicit'` is not yet supported.)

---

## Creating a LatticeModel

There are three primary ways to create a `LatticeModel`:

1. **Using the Default Lattice Choice**
2. **Defining a Custom Periodic Cell**
3. **Loading from an Existing Lattice Input File**

### 1. Using the Default Lattice Choice

This method allows you to select from predefined lattice types and specify basic parameters.

#### Required Parameters

- **`lattice_type`**: Set to `'default_choice'`.
- **`default_lattice_type`** (`str`): Choose from `'triangular_periodic'`, `'rectangular_periodic'`, or `'hexagonal_periodic'`.
- **`lattice_constant`** (`float`): The lattice constant (e.g., in Ångströms).
- **`copies`** (`List[int]`): Number of repetitions along the horizontal and vertical directions.

#### Example

```python
from zacrostools.lattice_model import LatticeModel

# Create a default triangular lattice
lattice_model = LatticeModel(
    lattice_type='default_choice',
    default_lattice_type='triangular_periodic',
    lattice_constant=2.5,
    copies=[10, 10]
)
```

### 2. Defining a Custom Periodic Cell

This method allows you to define a custom lattice by specifying the unit cell vectors, site types, and neighboring structures.

#### Required Parameters

- **`lattice_type`**: Set to `'periodic_cell'`.
- **`cell_vectors`** (`Tuple[Tuple[float, float], Tuple[float, float]]`): Two vectors defining the unit cell.
- **`sites`** (`Dict[str, Union[Tuple[float, float], List[Tuple[float, float]]]]`): Mapping of site types to their coordinates within the unit cell.
- **`coordinate_type`** (`str`, optional): `'direct'` or `'cartesian'`. Defaults to `'direct'`.
- **`copies`** (`List[int]`): Number of repetitions along the horizontal and vertical directions.
- **`neighboring_structure`** (`Union[str, Dict[str, Union[str, List[str]]]]`): Defines the neighboring relationships between sites.
  - If set to `'from_distances'`, you must provide `max_distances`.
  - If providing a dictionary, it maps site pairs to a list of relationship keywords.
- **`max_distances`** (`Dict[str, float]`, required if `neighboring_structure='from_distances'`): Defines maximum distances for neighbor pairs.

#### Neighboring Structure Format

When specifying the `neighboring_structure` directly as a dictionary:

- **Keys**: Site pairs in the format `'1-2'`, where numbers represent site indices.
- **Values**: A list of relationship keywords (e.g., `['north', 'east']`).

This allows multiple relationships to be specified for the same site pair.

#### Example with Direct Neighboring Structure

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

#### Example with Automatic Neighboring Structure Generation

```python
from zacrostools.lattice_model import LatticeModel

# Define cell vectors
cell_vectors = ((2.5, 0.0), (0.0, 2.5))

# Define site positions
sites = {
    'A': [(0.0, 0.0)],
    'B': [(0.5, 0.5)]
}

# Define maximum distances for neighbor pairs
max_distances = {
    'A-A': 3.0,
    'A-B': 3.0,
    'B-B': 3.0
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

### 3. Loading from an Existing Lattice Input File

This method allows you to create a `LatticeModel` by reading a previously created `lattice_input.dat` file. This is particularly useful when you want to reuse lattice configurations or when the lattice file was provided by another user.

#### Method

```python
lattice_model = LatticeModel.from_file(input_file)
```

- **`input_file`** (`str` or `Path`): Path to the existing `lattice_input.dat` file.

#### Notes

- The method reads the `lattice` block from the file, which starts with the `lattice` keyword and ends with `end_lattice`.
- The method supports `'default_choice'` and `'periodic_cell'` lattice types.
- If the lattice type is `'explicit'`, a `LatticeModelError` will be raised as this type is not yet supported.
- The method ignores any content outside the `lattice` block.

#### Example

```python
from zacrostools.lattice_model import LatticeModel

# Load a LatticeModel from an existing lattice_input.dat file
lattice_model = LatticeModel.from_file(input_file='path/to/lattice_input.dat')

# Write the lattice input file (optional, e.g., to a new directory)
lattice_model.write_lattice_input(output_dir='kmc_simulation')
```

---

## Methods for Modifying the Lattice

The `LatticeModel` class provides methods to modify the lattice after creation.

### Repeating the Lattice Model

You can expand the unit cell by repeating it along the cell vectors.

#### Method

```python
lattice_model.repeat_lattice_model(a, b)
```

- **`a`** (`int`): Number of repetitions along the first cell vector.
- **`b`** (`int`): Number of repetitions along the second cell vector.

#### Example

```python
# Repeat the lattice 2 times along alpha and 3 times along beta
lattice_model.repeat_lattice_model(a=2, b=3)
```

### Removing a Site

You can remove a specific site based on its coordinates.

#### Method

```python
lattice_model.remove_site(direct_coords, tolerance=1e-8)
```

- **`direct_coords`** (`Tuple[float, float]`): The direct coordinates of the site to remove.
- **`tolerance`** (`float`, optional): Tolerance for coordinate matching.

#### Example

```python
# Remove a site at position (0.5, 0.5)
lattice_model.remove_site(direct_coords=(0.5, 0.5))
```

### Changing the Site Type

You can change the type of a specific site.

#### Method

```python
lattice_model.change_site_type(direct_coords, new_site_type, tolerance=1e-8)
```

- **`direct_coords`** (`Tuple[float, float]`): The direct coordinates of the site.
- **`new_site_type`** (`str`): The new site type to assign.
- **`tolerance`** (`float`, optional): Tolerance for coordinate matching.

#### Example

```python
# Change the site type at position (0.0, 0.0) to 'B'
lattice_model.change_site_type(direct_coords=(0.0, 0.0), new_site_type='B')
```

---

## Writing the Lattice Input File

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

## Full Examples

### Example 1: Creating a Default Triangular Lattice

```python
from zacrostools.lattice_model import LatticeModel

# Create a default triangular lattice
lattice_model = LatticeModel(
    lattice_type='default_choice',
    default_lattice_type='triangular_periodic',
    lattice_constant=2.5,
    copies=[20, 20]
)

# Write the lattice input file
lattice_model.write_lattice_input(output_dir='kmc_simulation')
```

### Example 2: Defining a Custom Periodic Cell with Direct Neighboring Structure

```python
from zacrostools.lattice_model import LatticeModel

# Define cell vectors (in Ångströms)
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

# Write the lattice input file
lattice_model.write_lattice_input(output_dir='kmc_simulation')
```

**Generated `lattice_input.dat`:**

```
lattice periodic_cell

  cell_vectors
    3.27000000 0.00000000
    0.00000000 3.27000000
  repeat_cell 10 10
  n_cell_sites 2
  n_site_types 2
  site_type_names tC tM
  site_types tC tM
  site_coordinates
    0.25000000 0.25000000
    0.75000000 0.75000000
  neighboring_structure
    1-2 self
    1-1 north
    1-1 east
    2-1 north
    2-1 east
    2-1 northeast
    2-2 north
    2-2 east
  end_neighboring_structure

end_lattice
```

### Example 3: Defining a Custom Periodic Cell with Automatic Neighboring Structure Generation

```python
from zacrostools.lattice_model import LatticeModel

# Define cell vectors (in Ångströms)
cell_vectors = ((2.5, 0.0), (0.0, 2.5))

# Define site positions
sites = {
    'A': [(0.0, 0.0), (0.5, 0.5)],
    'B': [(0.25, 0.25), (0.75, 0.75)]
}

# Define maximum distances for neighbor pairs (in Ångströms)
max_distances = {
    'A-A': 3.0,
    'A-B': 3.0,
    'B-B': 3.0
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

# Write the lattice input file
lattice_model.write_lattice_input(output_dir='kmc_simulation')
```

### Example 4: Loading a LatticeModel from an Existing Lattice Input File

```python
from zacrostools.lattice_model import LatticeModel

# Load a LatticeModel from an existing lattice_input.dat file
lattice_model = LatticeModel.from_file(input_file='lattice_input_Cu111.dat')

# Optionally, you can modify the lattice or write it to a new location
lattice_model.write_lattice_input(output_dir='kmc_simulation')
```

---

## Additional Notes

- **Coordinate Types**:
  - **`direct`**: Coordinates are given in terms of the unit cell vectors (values between 0 and 1).
  - **`cartesian`**: Coordinates are given in absolute units (e.g., Ångströms).

- **Neighboring Structure**:
  - When specifying `neighboring_structure`, you can either provide a dictionary mapping site pairs to a list of relationship keywords or use `'from_distances'` to automatically generate the neighboring structure based on `max_distances`.
  - **Direct Specification**: Allows precise control over neighboring relationships.
    - **Format**:
      - **Keys**: Site pairs in the format `'site_index1-site_index2'` (e.g., `'1-2'`).
      - **Values**: List of relationship keywords (e.g., `['north', 'east']`).
  - **Automatic Generation**: Generates neighboring relationships based on distances.
    - Requires `max_distances` to define interaction cutoffs for site type pairs.

- **Allowed Neighboring Keywords**:
  - `'self'`, `'north'`, `'northeast'`, `'east'`, `'southeast'`

- **Site Indices**:
  - Site indices start from `1` and are assigned based on the order of site definitions.
  - The combination of `site_indices` and `site_coordinates` determines the mapping.

- **Site Types**:
  - Site types are user-defined labels (e.g., `'A'`, `'B'`) that can be used to differentiate between different kinds of sites on the lattice.

---

## Next Steps

With the `LatticeModel` defined, you can proceed to:

- **Define the Gas Model**: Specify gas-phase species using the `GasModel`.
- **Set Up the Energetics Model**: Provide cluster energetics with the `EnergeticsModel`.
- **Define the Reaction Model**: Outline reaction mechanisms using the `ReactionModel`.
- **Assemble the KMC Model**: Integrate all components into a `KMCModel` for simulation.

For detailed guidance on these steps, refer to the respective sections in the documentation.

---

**Note:** The `LatticeModel` is a critical component of the KMC simulation setup. Ensure that the lattice parameters and neighboring structures accurately represent the physical system you are modeling.

---

**Updates Based on Recent Changes:**

- **New `from_file` Class Method**:
  - You can now create a `LatticeModel` by reading an existing `lattice_input.dat` file.
  - This feature enhances flexibility, allowing you to reuse lattice configurations or incorporate lattices provided by others.
  - The method supports both `'default_choice'` and `'periodic_cell'` lattice types.

- **Neighboring Structure Format Change**:
  - The `neighboring_structure` can now accept multiple relationship keywords for the same site pair.
  - This is especially useful when the same site pair has multiple interactions (e.g., both `'north'` and `'east'`).
  - This change allows for more complex and precise definitions of neighboring relationships.

- **Usage Implications**:
  - When defining the `neighboring_structure` directly, ensure that the values are either a single string or a list of strings representing the relationship keywords.
  - This format aligns with the requirements of the `lattice_input.dat` file and provides greater flexibility in modeling complex lattices.

---

**Example of Defining Multiple Relationships for a Site Pair:**

```python
neighboring_structure = {
    '1-1': ['north', 'east'],          # Site 1 has 'north' and 'east' neighbors of site 1
    '1-2': ['self'],                   # Site 1 and Site 2 are neighbors in 'self' (within the unit cell)
    '2-1': ['north', 'east', 'northeast'],  # Site 2 has multiple relationships with Site 1
    '2-2': ['north', 'east']           # Site 2 has 'north' and 'east' neighbors of site 2
}
```

**Note:** This format allows for a comprehensive and detailed specification of neighboring interactions, which is essential for accurately modeling physical systems with complex geometries.
