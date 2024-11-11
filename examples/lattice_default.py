from zacrostools.lattice_model import LatticeModel


lattice_model = LatticeModel(lattice_type='default_choice',
                             default_lattice_type='hexagonal_periodic',
                             lattice_constant=4.0,
                             copies=[3, 3])

lattice_model.write_lattice_input(output_dir='.')
