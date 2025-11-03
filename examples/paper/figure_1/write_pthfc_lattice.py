from zacrostools.lattice_model import LatticeModel

# Create distance cutoff dictionary
site_pairs = ['tC-tC', 'tC-tM', 'tM-tM', 'Pt-Pt', 'Pt-tC', 'Pt-tM']
max_distances = {k: 4.0 for k in site_pairs}

lattice_model = LatticeModel(
    lattice_type='periodic_cell',
    cell_vectors=((3.27, 0), (0, 3.27)),
    sites={'tC': (0.25, 0.25), 'tM': (0.75, 0.75)},
    copies=[10, 10],
    neighboring_structure='from_distances',
    max_distances=max_distances)

# New unit cell as 4x4 repetition of original unit cell
lattice_model.repeat_lattice_model(4, 4)

# Replace four tC sites by Pt sites
pt_site_coords = [(0.3125, 0.3125), (0.3125, 0.5625),
                  (0.5625, 0.3125), (0.5625, 0.5625)]
for coord in pt_site_coords:
    lattice_model.change_site_type(
        direct_coords=coord, new_site_type='Pt')

# Remove the tM site in the middle of the four Pt sites
lattice_model.remove_site(direct_coords=(0.4375, 0.4375))

# Write the lattice_input.dat file in a folder named 'PtHfC'
lattice_model.write_lattice_input(output_dir='pthfc_lattice')
