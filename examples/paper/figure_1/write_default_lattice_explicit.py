from zacrostools.lattice_model import LatticeModel

# Define cell vectors
cell_vectors = ((2.59807, 0.0), (0.0, 1.50))

# Define site positions
sites = {
    'top': [(0, 0), (0.5, 0.5)],
}


# Create the LatticeModel instance
lattice_model = LatticeModel(
    lattice_type='periodic_cell',
    cell_vectors=cell_vectors,
    sites=sites,
    coordinate_type='direct',
    copies=[10, 10],
    neighboring_structure='from_distances',
    max_distances={'top-top': 2.0},
)

lattice_model.write_lattice_input(output_dir='default_lattice_explicit')
