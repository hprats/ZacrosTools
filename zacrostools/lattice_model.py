from pathlib import Path
from typing import Union, Optional, List, Tuple, Dict, Any
import numpy as np
from zacrostools.write_functions import write_header
from zacrostools.custom_exceptions import LatticeModelError
from zacrostools.parse_input_files import parse_lattice_input_file


class LatticeModel:
    """
    Represents a KMC lattice model for Zacros.

    Parameters
    ----------
    lattice_type : str
        Type of lattice structure. Must be one of the following:
        - 'default_choice'
        - 'periodic_cell'
        - 'explicit'

    default_lattice_type : str, optional
        Required if `lattice_type` is 'default_choice'.
        One of 'triangular_periodic', 'rectangular_periodic', 'hexagonal_periodic'.

    lattice_constant : float, optional
        Required if `lattice_type` is 'default_choice'.
        The lattice constant.

    copies : list of int, optional
        Required for 'default_choice' and 'periodic_cell'.
        Number of copies in horizontal and vertical directions, e.g., `[10, 10]`.

    cell_vectors : tuple of tuple of float, optional
        Required if `lattice_type` is 'periodic_cell'.
        Two unit vectors defining the unit cell, e.g., `((2.5, 0.0), (0.0, 2.5))`.

    sites : dict, optional
        Required if `lattice_type` is 'periodic_cell'.
        Dictionary mapping site types to their coordinates.
        Values can be either a single tuple or a list of tuples.
        Example:
        ```
        {
            'A': [(0.0, 0.0)],
            'B': [(0.5, 0.5)]
        }
        ```

    coordinate_type : str, optional
        Required if `lattice_type` is 'periodic_cell'.
        Coordinate system used for site positions: 'direct' or 'cartesian'.
        Defaults to 'direct'.

    neighboring_structure : Union[str, dict], optional
        Required if `lattice_type` is 'periodic_cell'.
        - If a dictionary, it maps site pair strings to a list of relationship keywords.
          Example: `{'1-2': ['self'], '1-1': ['north', 'east']}`
        - If 'from_distances', the user must provide a `max_distances` dictionary to
          generate the neighboring structure automatically.

    max_distances : dict, optional
        Required if `neighboring_structure='from_distances'`.
        Dictionary mapping site type pairs to maximum allowed distances.
        Example: `{'A-A': 3.0, 'A-B': 3.0, 'B-B': 3.0}`

    Examples
    --------
    **Default Choice Lattice**

    ```python
    lattice_model = LatticeModel(
        lattice_type='default_choice',
        default_lattice_type='triangular_periodic',
        lattice_constant=2.5,
        copies=[20, 20]
    )
    ```

    **Periodic Cell Lattice**

    ```python
    lattice_model = LatticeModel(
        lattice_type='periodic_cell',
        cell_vectors=((2.5, 0.0), (0.0, 2.5)),
        sites={
            'A': [(0.0, 0.0)],
            'B': [(0.5, 0.5)]
        },
        coordinate_type='direct',
        copies=[10, 10],
        neighboring_structure='from_distances',
        max_distances={
            'A-A': 3.0,
            'A-B': 3.0,
            'B-B': 3.0
        }
    )
    ```

    Alternatively, when specifying the `neighboring_structure` directly:

    ```python
    neighboring_structure = {
        '1-1': ['north', 'east'],
        '1-2': ['self'],
        '2-1': ['north', 'east', 'northeast'],
        '2-2': ['north', 'east']
    }

    lattice_model = LatticeModel(
        lattice_type='periodic_cell',
        cell_vectors=((3.27, 0.0), (0.0, 3.27)),
        sites={
            'tC': [(0.25, 0.25)],
            'tM': [(0.75, 0.75)]
        },
        coordinate_type='direct',
        copies=[10, 10],
        neighboring_structure=neighboring_structure
    )
    ```

    Raises
    ------
    LatticeModelError
        If required parameters are missing or invalid.
    """

    ALLOWED_LATTICE_TYPES = {'default_choice', 'periodic_cell', 'explicit'}
    ALLOWED_DEFAULT_LATTICE_TYPES = {'triangular_periodic', 'rectangular_periodic', 'hexagonal_periodic'}
    ALLOWED_COORDINATE_TYPES = {'direct', 'cartesian'}
    ALLOWED_NEIGHBORING_KEYWORDS = {'self', 'north', 'northeast', 'east', 'southeast'}
    DIRECTIONS = {
        'east': (1, 0),
        'north': (0, 1),
        'northeast': (1, 1),
        'southeast': (1, -1)
    }

    def __init__(self,
                 lattice_type: str,
                 default_lattice_type: Optional[str] = None,
                 lattice_constant: Optional[float] = None,
                 copies: Optional[List[int]] = None,
                 cell_vectors: Optional[Tuple[Tuple[float, float], Tuple[float, float]]] = None,
                 sites: Optional[Dict[str, Union[Tuple[float, float], List[Tuple[float, float]]]]] = None,
                 coordinate_type: str = 'direct',
                 neighboring_structure: Optional[Union[str, Dict[str, Union[str, List[str]]]]] = None,
                 max_distances: Optional[Dict[str, float]] = None):

        # Validate lattice_type
        if lattice_type not in self.ALLOWED_LATTICE_TYPES:
            raise LatticeModelError(
                f"Invalid lattice_type '{lattice_type}'. "
                f"Allowed types are: {', '.join(self.ALLOWED_LATTICE_TYPES)}."
            )
        self.lattice_type = lattice_type

        if lattice_type == 'default_choice':
            # Validate required parameters for 'default_choice'
            if default_lattice_type is None:
                raise LatticeModelError("For 'default_choice' lattice_type, 'default_lattice_type' must be provided.")
            if default_lattice_type not in self.ALLOWED_DEFAULT_LATTICE_TYPES:
                raise LatticeModelError(
                    f"Invalid default_lattice_type '{default_lattice_type}'. "
                    f"Allowed types are: {', '.join(self.ALLOWED_DEFAULT_LATTICE_TYPES)}."
                )
            if lattice_constant is None:
                raise LatticeModelError("For 'default_choice' lattice_type, 'lattice_constant' must be provided.")
            if not isinstance(lattice_constant, (int, float)):
                raise LatticeModelError("'lattice_constant' must be a float.")
            if copies is None:
                raise LatticeModelError("For 'default_choice' lattice_type, 'copies' must be provided.")
            if (not isinstance(copies, list) or len(copies) != 2 or
                    not all(isinstance(i, int) for i in copies)):
                raise LatticeModelError("'copies' must be a list of two integers.")

            self.default_lattice_type = default_lattice_type
            self.lattice_constant = float(lattice_constant)
            self.copies = copies

            # Attributes specific to 'default_choice' are set; others are None
            self.cell_vectors = None
            self.sites = None
            self.coordinate_type = None
            self.neighboring_structure = None
            self.max_distances = None

        elif lattice_type == 'periodic_cell':
            # Validate required parameters for 'periodic_cell'
            if cell_vectors is None:
                raise LatticeModelError("For 'periodic_cell' lattice_type, 'cell_vectors' must be provided.")
            if (not isinstance(cell_vectors, tuple) or len(cell_vectors) != 2 or
                    not all(isinstance(vec, tuple) and len(vec) == 2 for vec in cell_vectors)):
                raise LatticeModelError(
                    "'cell_vectors' must be a tuple of two tuples, each containing two floats."
                )
            if sites is None:
                raise LatticeModelError("For 'periodic_cell' lattice_type, 'sites' must be provided.")
            if not isinstance(sites, dict):
                raise LatticeModelError(
                    "'sites' must be a dictionary with site type names as keys and coordinate tuples or lists of coordinate tuples as values."
                )
            # Normalize 'sites' to ensure all values are lists of tuples
            normalized_sites = {}
            for site_type, coords in sites.items():
                if isinstance(coords, tuple):
                    # Single tuple provided; convert to list
                    normalized_sites[site_type] = [coords]
                elif isinstance(coords, list):
                    # List of tuples; validate each
                    if not all(isinstance(coord, tuple) and len(coord) == 2 and
                               all(isinstance(c, (int, float)) for c in coord) for coord in coords):
                        raise LatticeModelError(
                            f"All coordinates for site type '{site_type}' must be tuples of two floats."
                        )
                    normalized_sites[site_type] = coords
                else:
                    raise LatticeModelError(
                        f"Coordinates for site type '{site_type}' must be either a tuple or a list of tuples."
                    )
            self.sites = normalized_sites

            if coordinate_type not in self.ALLOWED_COORDINATE_TYPES:
                raise LatticeModelError(
                    f"Invalid coordinate_type '{coordinate_type}'. "
                    f"Allowed types are: {', '.join(self.ALLOWED_COORDINATE_TYPES)}."
                )
            if copies is None:
                raise LatticeModelError("For 'periodic_cell' lattice_type, 'copies' must be provided.")
            if (not isinstance(copies, list) or len(copies) != 2 or
                    not all(isinstance(i, int) for i in copies)):
                raise LatticeModelError("'copies' must be a list of two integers.")

            # Assign attributes that are required before handling neighboring_structure
            self.coordinate_type = coordinate_type
            self.copies = copies
            self.cell_vectors = cell_vectors

            # Validate neighboring_structure
            if neighboring_structure is None:
                raise LatticeModelError("For 'periodic_cell' lattice_type, 'neighboring_structure' must be provided.")
            if isinstance(neighboring_structure, dict):
                # Validate each key-value pair in neighboring_structure
                for pair, keywords in neighboring_structure.items():
                    if not isinstance(pair, str) or not self._is_valid_pair_key(pair):
                        raise LatticeModelError(
                            f"Invalid key '{pair}' in 'neighboring_structure'. Keys must be strings in the format 'int-int', e.g., '1-2'."
                        )
                    if isinstance(keywords, str):
                        keywords = [keywords]
                    if not isinstance(keywords, list):
                        raise LatticeModelError(
                            f"Values in 'neighboring_structure' must be strings or lists of strings. Invalid value for key '{pair}'."
                        )
                    for keyword in keywords:
                        if keyword not in self.ALLOWED_NEIGHBORING_KEYWORDS:
                            raise LatticeModelError(
                                f"Invalid keyword '{keyword}' for 'neighboring_structure'. "
                                f"Allowed keywords are: {', '.join(self.ALLOWED_NEIGHBORING_KEYWORDS)}."
                            )
                self.neighboring_structure = neighboring_structure
                self.max_distances = None  # Not used when providing a dict directly
            elif isinstance(neighboring_structure, str) and neighboring_structure == 'from_distances':
                if max_distances is None:
                    raise LatticeModelError(
                        "When 'neighboring_structure' is set to 'from_distances', 'max_distances' must be provided."
                    )
                if not isinstance(max_distances, dict):
                    raise LatticeModelError("'max_distances' must be a dictionary mapping site type pairs to distances.")
                # Validate max_distances
                for pair, distance in max_distances.items():
                    if not isinstance(pair, str) or not self._is_valid_site_type_pair(pair):
                        raise LatticeModelError(
                            f"Invalid key '{pair}' in 'max_distances'. Keys must be strings in the format 'SiteType1-SiteType2', e.g., 'tC-tM'."
                        )
                    if not isinstance(distance, (int, float)) or distance <= 0:
                        raise LatticeModelError(
                            f"Invalid distance '{distance}' for pair '{pair}' in 'max_distances'. Must be a positive number."
                        )
                # Generate neighboring_structure based on max_distances
                self.neighboring_structure = self._generate_neighboring_structure_from_distances(max_distances)
                self.max_distances = max_distances  # Store max_distances for future recalculations
            else:
                raise LatticeModelError(
                    "Invalid 'neighboring_structure' parameter. Must be either a dictionary or the string 'from_distances'."
                )

            # Attributes specific to 'periodic_cell' are set; others are None
            self.default_lattice_type = None
            self.lattice_constant = None

            # Perform additional validations
            self._validate_periodic_cell()

    @classmethod
    def from_file(cls, input_file: Union[str, Path]):
        """
        Create a LatticeModel instance by reading a `lattice_input.dat` file.

        Parameters
        ----------
        input_file : Union[str, Path]
            Path to the lattice input file.

        Returns
        -------
        LatticeModel
            An instance of LatticeModel initialized with parameters extracted from the file.

        Raises
        ------
        LatticeModelError
            If the file cannot be read, the lattice block is missing, or if required parameters are invalid or missing.
        """
        parsed_data = parse_lattice_input_file(input_file)

        lattice_type = parsed_data['lattice_type']

        if lattice_type == 'default_choice':
            return cls(
                lattice_type='default_choice',
                default_lattice_type=parsed_data['default_lattice_type'],
                lattice_constant=parsed_data['lattice_constant'],
                copies=parsed_data['copies']
            )

        elif lattice_type == 'periodic_cell':
            return cls(
                lattice_type='periodic_cell',
                cell_vectors=parsed_data['cell_vectors'],
                sites=parsed_data['sites'],
                coordinate_type=parsed_data.get('coordinate_type', 'direct'),
                copies=parsed_data['copies'],
                neighboring_structure=parsed_data['neighboring_structure']
            )

        elif lattice_type == 'explicit':
            raise LatticeModelError("The 'explicit' lattice_type is not yet supported.")

        else:
            raise LatticeModelError(f"Unsupported lattice_type '{lattice_type}'.")

    def _is_valid_pair_key(self, pair: str) -> bool:
        """
        Validate that the pair key is in the format 'int-int'.

        Parameters
        ----------
        pair : str
            The pair string to validate.

        Returns
        -------
        bool
            True if valid, False otherwise.
        """
        parts = pair.split('-')
        if len(parts) != 2:
            return False
        return parts[0].isdigit() and parts[1].isdigit()

    def _is_valid_site_type_pair(self, pair: str) -> bool:
        """
        Validate that the site type pair key is in the format 'SiteType1-SiteType2'.

        Parameters
        ----------
        pair : str
            The site type pair string to validate.

        Returns
        -------
        bool
            True if valid, False otherwise.
        """
        parts = pair.split('-')
        if len(parts) != 2:
            return False
        return all(isinstance(part, str) and part for part in parts)

    def _validate_periodic_cell(self):
        """
        Validate the properties specific to the 'periodic_cell' lattice type.

        Raises
        ------
        LatticeModelError
            If any of the site coordinates are invalid based on the coordinate type.
        """
        if self.coordinate_type == 'direct':
            # Ensure all coordinates are between 0 and 1
            for site_type, coords_list in self.sites.items():
                for coord in coords_list:
                    if not (0.0 <= coord[0] <= 1.0 and 0.0 <= coord[1] <= 1.0):
                        raise LatticeModelError(
                            f"Direct coordinates for site '{site_type}' must be between 0 and 1. "
                            f"Invalid coordinate: {coord}"
                        )
        elif self.coordinate_type == 'cartesian':
            # No specific range validation for cartesian coordinates
            pass
        else:
            raise LatticeModelError(f"Unsupported coordinate_type '{self.coordinate_type}'.")

    def _generate_neighboring_structure_from_distances(self, max_distances: Dict[str, float]) -> Dict[str, List[str]]:
        """
        Generate the neighboring_structure based on distance criteria.

        Parameters
        ----------
        max_distances : dict
            Mapping of site type pairs to maximum allowed distances in angstroms.
            Example: `{'A-A': 4.0, 'A-B': 3.0, 'B-B': 2.0}`

        Returns
        -------
        dict
            Generated neighboring_structure mapping site pairs to a list of relationship keywords.

        Raises
        ------
        LatticeModelError
            If site types in max_distances do not exist in the defined sites.
        """
        # Create a list of all sites with their types and coordinates
        site_list: List[Dict[str, Any]] = []
        for site_type in self.sites:
            for coord in self.sites[site_type]:
                site_list.append({'type': site_type, 'coord': coord})

        num_sites = len(site_list)
        if num_sites == 0:
            raise LatticeModelError("No sites defined in 'sites'.")

        # Assign indices to sites starting from 1
        for idx, site in enumerate(site_list, start=1):
            site['index'] = idx

        # Convert cell_vectors to numpy arrays for calculations
        alpha = np.array(self.cell_vectors[0])  # Vector α
        beta = np.array(self.cell_vectors[1])  # Vector β

        # Prepare dictionary to hold neighboring relations
        neighboring_structure: Dict[str, List[str]] = {}

        # Precompute Cartesian coordinates for all sites
        for site in site_list:
            site['cartesian'] = site['coord'][0] * alpha + site['coord'][1] * beta

        # Function to compute distance between two points
        def distance(p1: np.ndarray, p2: np.ndarray) -> float:
            return np.linalg.norm(p1 - p2)

        # Iterate over all unique pairs within the unit cell for 'self' relations
        for i in range(num_sites):
            for j in range(i + 1, num_sites):
                site_i = site_list[i]
                site_j = site_list[j]
                pair_key = f"{site_i['index']}-{site_j['index']}"
                pair_types = f"{site_i['type']}-{site_j['type']}"

                # Check if this pair type exists in max_distances
                max_distance = self._get_max_distance(pair_types, max_distances)
                if max_distance is None:
                    continue  # No distance criteria defined for this pair

                # Calculate distance within the unit cell
                dist = distance(site_i['cartesian'], site_j['cartesian'])
                if dist <= max_distance:
                    if pair_key not in neighboring_structure:
                        neighboring_structure[pair_key] = []
                    neighboring_structure[pair_key].append('self')

        # Directions and their corresponding shift vectors in direct coordinates
        directions = self.DIRECTIONS

        for direction, shift in directions.items():
            shift_vector = np.array(shift)
            # Calculate the Cartesian shift based on cell_vectors
            cartesian_shift = shift_vector[0] * alpha + shift_vector[1] * beta

            # Iterate over all pairs between original sites and shifted sites
            for site in site_list:
                for target_site in site_list:
                    pair_key = f"{site['index']}-{target_site['index']}"
                    pair_types = f"{site['type']}-{target_site['type']}"

                    # Check if this pair type exists in max_distances
                    max_distance = self._get_max_distance(pair_types, max_distances)
                    if max_distance is None:
                        continue  # No distance criteria defined for this pair

                    # Calculate shifted position of target_site
                    shifted_position = target_site['cartesian'] + cartesian_shift
                    dist = distance(site['cartesian'], shifted_position)
                    if dist <= max_distance:
                        if pair_key not in neighboring_structure:
                            neighboring_structure[pair_key] = []
                        if direction not in neighboring_structure[pair_key]:
                            neighboring_structure[pair_key].append(direction)

        return neighboring_structure

    def _get_max_distance(self, pair_types: str, max_distances: Dict[str, float]) -> Optional[float]:
        """
        Retrieve the maximum distance for a given pair of site types, considering symmetry.

        Parameters
        ----------
        pair_types : str
            Pair of site types in the format 'type1-type2'.
        max_distances : dict
            Mapping of site type pairs to maximum distances.

        Returns
        -------
        Optional[float]
            The maximum distance if defined, else None.
        """
        # Check the pair as is
        if pair_types in max_distances:
            return max_distances[pair_types]
        # Check the symmetric pair
        reversed_pair = '-'.join(pair_types.split('-')[::-1])
        return max_distances.get(reversed_pair, None)

    def write_lattice_input(self,
                            output_dir: Union[str, Path],
                            sig_figs: int = 8):
        """
        Writes the `lattice_input.dat` file based on the lattice type.

        Parameters
        ----------
        output_dir : Union[str, Path]
            Directory path where the file will be written.
        sig_figs : int, optional
            Number of significant figures for numerical values. Default is 8.

        Raises
        ------
        LatticeModelError
            If file writing fails or if `lattice_type` is unsupported.
        """
        # Convert output_dir to Path object if it's a string
        output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir

        # Ensure the output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "lattice_input.dat"
        write_header(output_file)

        try:
            with output_file.open('a') as infile:
                if self.lattice_type == 'default_choice':
                    infile.write("lattice default_choice\n\n")
                    infile.write(f"  {self.default_lattice_type} {self.lattice_constant:.{sig_figs}f} "
                                 f"{self.copies[0]} {self.copies[1]}\n")
                    infile.write("\nend_lattice\n")
                elif self.lattice_type == 'periodic_cell':
                    infile.write("lattice periodic_cell\n\n")
                    # Write cell_vectors
                    infile.write("  cell_vectors\n")
                    for vec in self.cell_vectors:
                        infile.write(f"    {vec[0]:.{sig_figs}f} {vec[1]:.{sig_figs}f}\n")
                    # Write repeat_cell
                    infile.write(f"  repeat_cell {self.copies[0]} {self.copies[1]}\n")

                    # Calculate n_cell_sites, n_site_types, site_type_names, site_types, site_coordinates
                    site_type_names = list(self.sites.keys())
                    n_site_types = len(site_type_names)
                    site_types = []
                    site_coordinates = []

                    # Assign indices to sites
                    site_indices = {}
                    current_index = 1
                    for site_type in site_type_names:
                        for coord in self.sites[site_type]:
                            site_types.append(site_type)
                            site_coordinates.append(coord)
                            site_indices[(coord[0], coord[1])] = current_index
                            current_index += 1

                    n_cell_sites = len(site_coordinates)

                    # Write n_cell_sites
                    infile.write(f"  n_cell_sites {n_cell_sites}\n")
                    # Write n_site_types
                    infile.write(f"  n_site_types {n_site_types}\n")
                    # Write site_type_names
                    infile.write(f"  site_type_names {' '.join(site_type_names)}\n")
                    # Write site_types
                    infile.write(f"  site_types {' '.join(site_types)}\n")
                    # Write site_coordinates
                    infile.write("  site_coordinates\n")
                    for coord in site_coordinates:
                        infile.write(f"    {coord[0]:.{sig_figs}f} {coord[1]:.{sig_figs}f}\n")

                    # Write neighboring_structure
                    infile.write("  neighboring_structure\n")
                    for pair, keywords in self.neighboring_structure.items():
                        if isinstance(keywords, str):
                            keywords = [keywords]
                        for keyword in keywords:
                            infile.write(f"    {pair} {keyword}\n")
                    infile.write("  end_neighboring_structure\n")

                    # End lattice
                    infile.write("\nend_lattice\n")
                else:
                    # Placeholder for other lattice types
                    raise LatticeModelError(f"Lattice type '{self.lattice_type}' is not yet supported.")
        except IOError as e:
            raise LatticeModelError(f"Failed to write to '{output_file}': {e}")

    def repeat_lattice_model(self, a: int, b: int):
        """
        Create a new unit cell by repeating the original unit cell `a` times along the first cell vector
        and `b` times along the second cell vector.

        Parameters
        ----------
        a : int
            Number of repetitions along the first cell vector.
        b : int
            Number of repetitions along the second cell vector.

        Raises
        ------
        LatticeModelError
            If `lattice_type` is not 'periodic_cell', `neighboring_structure` is not 'from_distances',
            or if `a` or `b` are not positive integers.
        """
        if self.lattice_type != 'periodic_cell':
            raise LatticeModelError("repeat_lattice_model method is only available for 'periodic_cell' lattice_type.")
        if self.max_distances is None:
            raise LatticeModelError("repeat_lattice_model method requires 'neighboring_structure' to be 'from_distances' with 'max_distances' provided.")
        if not (isinstance(a, int) and a > 0 and isinstance(b, int) and b > 0):
            raise LatticeModelError("'a' and 'b' must be positive integers.")

        # Scale cell vectors
        original_alpha, original_beta = self.cell_vectors
        new_alpha = (original_alpha[0] * a, original_alpha[1] * a)
        new_beta = (original_beta[0] * b, original_beta[1] * b)
        self.cell_vectors = (new_alpha, new_beta)

        # Generate new sites by repeating the unit cell
        new_sites = {}
        for site_type, coords in self.sites.items():
            new_sites[site_type] = []
            for (x, y) in coords:
                for i in range(a):
                    for j in range(b):
                        new_x = (x + i) / a
                        new_y = (y + j) / b
                        # Ensure the coordinates wrap around within [0,1)
                        new_x = new_x % 1.0
                        new_y = new_y % 1.0
                        new_sites[site_type].append((new_x, new_y))
        self.sites = new_sites

        # Recalculate neighboring_structure
        if self.max_distances is not None:
            self.neighboring_structure = self._generate_neighboring_structure_from_distances(self.max_distances)
        elif isinstance(self.neighboring_structure, dict):
            # If neighboring_structure was manually provided as a dict, decide if it needs to be updated
            # For simplicity, we'll keep it unchanged. Alternatively, you can regenerate it.
            pass
        else:
            raise LatticeModelError(
                "Invalid 'neighboring_structure' parameter. Must be either a dictionary or the string 'from_distances'."
            )

    def remove_site(self, direct_coords: Tuple[float, float], tolerance: float = 1e-8):
        """
        Remove a site from the lattice model based on its direct coordinates and update the neighboring structure.

        Parameters
        ----------
        direct_coords : Tuple[float, float]
            A tuple containing the direct x and y coordinates of the site to remove.
        tolerance : float, optional
            Tolerance for coordinate matching. Default is 1e-8.

        Raises
        ------
        LatticeModelError
            If `lattice_type` is not 'periodic_cell', if `neighboring_structure` is not 'from_distances',
            or if the site with the given coordinates is not found.
        """
        if self.lattice_type != 'periodic_cell':
            raise LatticeModelError("remove_site method is only available for 'periodic_cell' lattice_type.")
        if self.max_distances is None:
            raise LatticeModelError("remove_site method requires 'neighboring_structure' to be 'from_distances' with 'max_distances' provided.")

        # Unpack direct_coords
        x, y = direct_coords

        # Find the site to remove
        found = False
        for site_type, coords_list in list(self.sites.items()):
            for idx, coord in enumerate(coords_list):
                if np.isclose(coord[0], x, atol=tolerance) and np.isclose(coord[1], y, atol=tolerance):
                    # Remove the site
                    del self.sites[site_type][idx]
                    # Remove site_type key if no more sites
                    if not self.sites[site_type]:
                        del self.sites[site_type]
                    found = True
                    break
            if found:
                break

        if not found:
            raise LatticeModelError(f"No site found with coordinates ({x}, {y}).")

        # Recalculate neighboring_structure
        self.neighboring_structure = self._generate_neighboring_structure_from_distances(self.max_distances)

    def change_site_type(self, direct_coords: Tuple[float, float], new_site_type: str, tolerance: float = 1e-8):
        """
        Change the site type of a specific site based on its direct coordinates and update the neighboring structure.

        Parameters
        ----------
        direct_coords : Tuple[float, float]
            A tuple containing the direct x and y coordinates of the site to change.
        new_site_type : str
            The new site type name to assign to the specified site.
        tolerance : float, optional
            Tolerance for coordinate matching. Default is 1e-8.

        Raises
        ------
        LatticeModelError
            If `lattice_type` is not 'periodic_cell', if `neighboring_structure` is not 'from_distances',
            if the site with the given coordinates is not found, or if the `new_site_type` is invalid.
        """
        if self.lattice_type != 'periodic_cell':
            raise LatticeModelError("change_site_type method is only available for 'periodic_cell' lattice_type.")
        if self.max_distances is None:
            raise LatticeModelError("change_site_type method requires 'neighboring_structure' to be 'from_distances' with 'max_distances' provided.")
        if not isinstance(new_site_type, str) or not new_site_type:
            raise LatticeModelError("new_site_type must be a non-empty string.")

        # Unpack direct_coords
        x, y = direct_coords

        # Find the site to change
        found = False
        for site_type, coords_list in list(self.sites.items()):
            for idx, coord in enumerate(coords_list):
                if np.isclose(coord[0], x, atol=tolerance) and np.isclose(coord[1], y, atol=tolerance):
                    # Change the site type
                    del self.sites[site_type][idx]
                    if not self.sites[site_type]:
                        del self.sites[site_type]
                    # Add to new_site_type
                    if new_site_type in self.sites:
                        self.sites[new_site_type].append(coord)
                    else:
                        self.sites[new_site_type] = [coord]
                    found = True
                    break
            if found:
                break

        if not found:
            raise LatticeModelError(f"No site found with coordinates ({x}, {y}).")

        # Recalculate neighboring_structure
        self.neighboring_structure = self._generate_neighboring_structure_from_distances(self.max_distances)
