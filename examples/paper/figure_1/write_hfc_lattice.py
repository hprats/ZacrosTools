from zacrostools.lattice_model import LatticeModel

# Create distance cutoff dictionary
site_pairs = ['tC-tC', 'tC-tM', 'tM-tM']
max_distances = {k: 4.0 for k in site_pairs}

lattice_model = LatticeModel(
    lattice_type='periodic_cell',
    cell_vectors=((3.27, 0.0), (0.0, 3.27)),
    sites={'tC': (0.25, 0.25), 'tM': (0.75, 0.75)},
    coordinate_type='direct',
    copies=[10, 10],
    neighboring_structure='from_distances',
    max_distances=max_distances)

lattice_model.write_lattice_input(output_dir='hfc_lattice')
