import numpy as np
import matplotlib.pyplot as plt


def plot_periodic_lattice(filename, site_styles, ax=None, line_width=1.0):
    """
    Plot a periodic lattice from a Zacros lattice input file.

    Parameters
    ----------
    filename : str
        Path to the lattice input file (e.g., 'lattice_input.dat') following the Zacros format.
    site_styles : dict
        Dictionary mapping site type identifiers to style dictionaries. Each style dictionary
        may include the following keys:
            - 'color': Color for the site (default: 'black').
            - 'marker': Marker style for the site (default: 'x').
            - 'size': Size of the marker (default: 100).
    ax : matplotlib.axes.Axes, optional
        Matplotlib Axes object on which to plot the lattice. If not provided, a new figure
        and axes are created.
    line_width : float, optional
        Width of the lines used to plot the edges and the unit cell boundaries. Default is 1.0.

    Examples
    --------
    >>> site_styles = {
    ...     'A': {'color': 'blue', 'marker': 'o', 'size': 100},
    ...     'B': {'color': 'red', 'marker': 's', 'size': 150}
    ... }
    >>> ax = plot_periodic_lattice('lattice_input.dat', site_styles)
    >>> plt.show()

    """
    # Initialize variables
    cell_vectors = []
    site_types = []
    site_type_names = []
    site_coordinates = []
    neighboring_structure = []
    n_cell_sites = 0
    n_site_types = 0
    in_cell_vectors = False
    in_site_type_names = False
    in_site_types = False
    in_site_coordinates = False
    in_neighboring_structure = False

    # Periodicity translations mapping
    periodicity_translations = {
        'self': (0, 0),
        'east': (1, 0),
        'west': (-1, 0),
        'north': (0, 1),
        'south': (0, -1),
        'northeast': (1, 1),
        'northwest': (-1, 1),
        'southeast': (1, -1),
        'southwest': (-1, -1),
    }

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            if line.startswith('cell_vectors'):
                in_cell_vectors = True
                continue
            if in_cell_vectors:
                parts = line.strip().split()
                if len(parts) == 2:
                    cell_vectors.append([float(parts[0]), float(parts[1])])
                    if len(cell_vectors) == 2:
                        in_cell_vectors = False
                continue
            if line.startswith('n_cell_sites'):
                parts = line.strip().split()
                n_cell_sites = int(parts[1])
                continue
            if line.startswith('n_site_types'):
                parts = line.strip().split()
                n_site_types = int(parts[1])
                continue
            if line.startswith('site_type_names'):
                # Extract site type names from the same line
                parts = line.strip().split()
                site_type_names.extend(parts[1:])
                # Check if more names need to be read
                if len(site_type_names) < n_site_types:
                    in_site_type_names = True
                continue
            if in_site_type_names:
                parts = line.strip().split()
                site_type_names.extend(parts)
                if len(site_type_names) >= n_site_types:
                    in_site_type_names = False
                continue
            if line.startswith('site_types'):
                # Extract site types from the same line
                parts = line.strip().split()
                site_types.extend(parts[1:])
                # Check if more site types need to be read
                if len(site_types) < n_cell_sites:
                    in_site_types = True
                continue
            if in_site_types:
                parts = line.strip().split()
                site_types.extend(parts)
                if len(site_types) >= n_cell_sites:
                    in_site_types = False
                continue
            if line.startswith('site_coordinates'):
                in_site_coordinates = True
                continue
            if in_site_coordinates:
                parts = line.strip().split()
                if len(parts) == 2:
                    site_coordinates.append([float(parts[0]), float(parts[1])])
                    if len(site_coordinates) >= n_cell_sites:
                        in_site_coordinates = False
                continue
            if line.startswith('neighboring_structure'):
                in_neighboring_structure = True
                continue
            if in_neighboring_structure:
                if line.startswith('end_neighboring_structure'):
                    in_neighboring_structure = False
                    continue
                else:
                    neighboring_structure.append(line.strip())
                continue

    # Convert cell vectors to numpy arrays
    cell_vector_a = np.array(cell_vectors[0])
    cell_vector_b = np.array(cell_vectors[1])

    # Build site data
    sites = {}
    for idx in range(n_cell_sites):
        site_index = idx + 1  # Sites are 1-indexed
        u, v = site_coordinates[idx]
        site_type = site_types[idx]
        # Compute cartesian coordinates
        coord = u * cell_vector_a + v * cell_vector_b
        sites[(site_index, 0, 0)] = {
            'direct_coord': (u, v),
            'cartesian_coord': coord,
            'site_type': site_type
        }

    # Build edges and collect periodic sites
    edges = []
    for line in neighboring_structure:
        # Parse the neighboring structure line
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        sites_pair, periodicity = parts
        site_i_str, site_j_str = sites_pair.split('-')
        site_i = int(site_i_str)
        site_j = int(site_j_str)
        n_a, n_b = periodicity_translations.get(periodicity, (0, 0))

        # Site keys
        site_i_key = (site_i, 0, 0)
        site_j_key = (site_j, n_a, n_b)

        # Add site_j to sites if not already present
        if site_j_key not in sites:
            u_j, v_j = site_coordinates[site_j - 1]
            # Compute cartesian coordinates with translation
            translation_vector = n_a * cell_vector_a + n_b * cell_vector_b
            coord_j = u_j * cell_vector_a + v_j * cell_vector_b + translation_vector
            site_type_j = site_types[site_j - 1]
            sites[site_j_key] = {
                'direct_coord': (u_j, v_j),
                'cartesian_coord': coord_j,
                'site_type': site_type_j
            }

        # Add edge
        edges.append((site_i_key, site_j_key))

    # Prepare the axis
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    else:
        fig = ax.figure  # Get the figure from the provided axis

    # Plot edges
    for edge in edges:
        site_i_key, site_j_key = edge
        coord_i = sites[site_i_key]['cartesian_coord']
        coord_j = sites[site_j_key]['cartesian_coord']
        x_values = [coord_i[0], coord_j[0]]
        y_values = [coord_i[1], coord_j[1]]
        ax.plot(x_values, y_values, color='black', linewidth=line_width)

    # Plot sites
    for site_key, site_info in sites.items():
        coord = site_info['cartesian_coord']
        site_type = site_info['site_type']
        # Get style for this site type
        style = site_styles.get(site_type, {'color': 'black', 'marker': 'x', 'size': 100})
        color = style.get('color', 'black')
        marker = style.get('marker', 'x')
        size = style.get('size', 100)
        ax.scatter(coord[0], coord[1], color=color, marker=marker, s=size, zorder=5)

    # Draw the unit cell boundaries with dashed black lines
    # Define the corners of the unit cell
    origin = np.array([0, 0])
    corner_a = cell_vector_a
    corner_b = cell_vector_b
    corner_c = cell_vector_a + cell_vector_b

    # Create arrays of the x and y coordinates of the corners in order
    unit_cell_x = [origin[0], corner_a[0], corner_c[0], corner_b[0], origin[0]]
    unit_cell_y = [origin[1], corner_a[1], corner_c[1], corner_b[1], origin[1]]

    # Plot the unit cell boundaries
    ax.plot(unit_cell_x, unit_cell_y, linestyle='--', color='black', linewidth=1)

    # Set plot limits
    all_coords = np.array([site['cartesian_coord'] for site in sites.values()])
    unit_cell_corners = np.array([origin, corner_a, corner_b, corner_c])
    min_x = min(all_coords[:, 0].min(), unit_cell_corners[:, 0].min()) - 1
    max_x = max(all_coords[:, 0].max(), unit_cell_corners[:, 0].max()) + 1
    min_y = min(all_coords[:, 1].min(), unit_cell_corners[:, 1].min()) - 1
    max_y = max(all_coords[:, 1].max(), unit_cell_corners[:, 1].max()) + 1
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)

    # Set axes labels
    ax.set_xlabel('x (Å)')
    ax.set_ylabel('y (Å)')

    # Set ticks on both sides
    ax.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True, labeltop=False)
    ax.tick_params(axis='y', which='both', left=True, right=False, labelleft=True, labelright=False)

    # Set tick positions on both sides
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # Optionally, set equal aspect ratio
    ax.set_aspect('equal')

    # Return the axis for further customization if needed
    return ax

