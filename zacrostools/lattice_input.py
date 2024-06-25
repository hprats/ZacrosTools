from zacrostools.write_functions import write_header
from zacrostools.custom_exceptions import LatticeModelError, enforce_types


class LatticeModel:
    """A class that represents a lattice model.

    Parameters
    ----------
    lines: list of str
        Lines that will be printed in the lattice_input.dat.
    """

    @enforce_types
    def __init__(self, lines: list = None, lattice_type: str = None):
        self.lines = lines
        self.lattice_type = lattice_type

    @classmethod
    @enforce_types
    def from_file(cls, path: str):
        """Create a LatticeModel by reading an existing lattice_input.dat file.

        Parameters
        ----------
        path: str
            Path to the directory where the lattice_input.dat file is located


        Returns
        -------
        lattice_model: LatticeModel

        """

        lattice_lines = []
        start_pattern_detected = False
        end_pattern_detected = False

        with open(path, 'r') as infile:

            while not start_pattern_detected:
                line = infile.readline()
                if 'default_choice' in line or 'periodic_cell' in line or 'explicit' in line:
                    lattice_lines.append(line)
                    start_pattern_detected = True

            if 'default_choice' in line:
                lattice_type = 'default'
            elif 'periodic_cell' in line:
                lattice_type = 'custom_periodic'
            else:
                lattice_type = 'custom_non_periodic'

            while not end_pattern_detected:
                line = infile.readline()
                if 'end_lattice' in line:
                    lattice_lines.append(line)
                    end_pattern_detected = True
                else:
                    lattice_lines.append(line)

        lattice_model = cls(lines=lattice_lines, lattice_type=lattice_type)
        return lattice_model

    @enforce_types
    def write_lattice_input(self, path: str):
        """Write the lattice_input.dat file.

        Parameters
        ----------
        path: str
            Path to the directory where the lattice_input.dat file will be written.

        """
        write_header(f"{path}/lattice_input.dat")
        with open(f"{path}/lattice_input.dat", 'a') as infile:
            for line in self.lines:
                infile.write(line)

    @enforce_types
    def repeat_cell(self, repeat_cell: list):
        """Modify the value of the repeat_cell keyword in the lattice_input.dat file.

        Parameters
        ----------
        repeat_cell: list of int, optional
            Updates the repeat_cell keyword in lattice_input.dat file.

        """
        if self.lattice_type == 'custom_non_periodic':
            raise LatticeModelError("repeat_cell()' method can not be used with custom non-periodic lattices.")
        i = 0
        line = self.lines[i]
        if self.lattice_type == 'custom_periodic':
            while 'repeat_cell' not in line:
                i += 1
                line = self.lines[i]
            self.lines[i] = f'   repeat_cell {repeat_cell[0]} {repeat_cell[1]}\n'
        else:
            while not any(keyword in line for keyword in
                          ['triangular_periodic', 'rectangular_periodic', 'hexagonal_periodic']):
                i += 1
                line = self.lines[i]
            keyword = line.split()[0]
            lattice_constant = line.split()[1]
            self.lines[i] = f'   {keyword} {lattice_constant} {repeat_cell[0]} {repeat_cell[1]}\n'
