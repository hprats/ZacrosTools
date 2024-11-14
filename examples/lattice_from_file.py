from zacrostools.lattice_model import LatticeModel

# Create a LatticeModel instance from an existing lattice_input.dat file
lattice_model = LatticeModel.from_file(input_file='lattice_input_test.dat')

lattice_model.write_lattice_input(output_dir='.')
