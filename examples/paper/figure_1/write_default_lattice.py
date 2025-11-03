from zacrostools.lattice_model import LatticeModel

# Create a default triangular lattice
lattice_model = LatticeModel(
    lattice_type='default_choice',
    default_lattice_type='hexagonal_periodic',
    lattice_constant=1.5,
    copies=[10, 10]
)


lattice_model.write_lattice_input(output_dir='default_lattice')
