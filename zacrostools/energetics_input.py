import ast
import pandas as pd
from zacrostools.write_functions import write_header
from zacrostools.custom_exceptions import EnergeticModelError, enforce_types


class EnergeticModel:
    """A class that represents a KMC energetic model.

    Parameters:

    energetics_data: Pandas DataFrame
        Information on the energetic model.
        The cluster name is taken as the index of each row.

        The following columns are required:
            - cluster_eng (float): cluster formation energy (in eV)
            - site_types (str): the types of each site in the pattern
            - lattice_state (list): cluster configuration in Zacros format, e.g. ['1 CO* 1','2 CO* 1']
        The following columns are optional:
            - neighboring (str): connectivity between sites involved, e.g. 1-2. Default value: None
            - angles (str): Angle between sites in Zacros format, e.g. '1-2-3:180'. Default value: None
            - graph_multiplicity (int): symmetry number of the cluster, e.g. 2. Default value: 1
    """

    @enforce_types
    def __init__(self, energetics_data: pd.DataFrame = None):
        self.df = energetics_data

    @classmethod
    def from_dictionary(cls, path):
        """Not implemented yet"""
        pass

    def write_energetics_input(self, path, sig_figs_energies):
        """Write the energetics_input.dat file"""
        write_header(f"{path}/energetics_input.dat")
        with open(f"{path}/energetics_input.dat", 'a') as infile:
            infile.write('energetics\n\n')
            infile.write('############################################################################\n\n')
            for cluster in self.df.index:
                infile.write(f"cluster {cluster}\n\n")
                lattice_state = ast.literal_eval(self.df.loc[cluster, 'lattice_state'])
                infile.write(f"  sites {len(lattice_state)}\n")
                if not pd.isnull(self.df.loc[cluster, 'neighboring']):
                    infile.write(f"  neighboring {self.df.loc[cluster, 'neighboring']}\n")
                infile.write(f"  lattice_state\n")
                for element in lattice_state:
                    infile.write(f"    {' '.join(element.split())}\n")
                if 'site_types' in self.df.columns:
                    if not pd.isna(self.df.loc[cluster, 'site_types']):
                        infile.write(f"  site_types {self.df.loc[cluster, 'site_types']}\n")
                if 'graph_multiplicity' in self.df.columns:
                    if not pd.isna(self.df.loc[cluster, 'graph_multiplicity']):
                        infile.write(f"  graph_multiplicity {int(self.df.loc[cluster, 'graph_multiplicity'])}\n")
                if 'angles' in self.df.columns:
                    if not pd.isna(self.df.loc[cluster, 'angles']):
                        infile.write(f"  angles {self.df.loc[cluster, 'angles']}\n")
                infile.write(f"  cluster_eng {self.df.loc[cluster, 'cluster_eng']:.{sig_figs_energies}f}\n\n")
                infile.write(f"end_cluster\n\n")
                infile.write('############################################################################\n\n')
            infile.write(f"end_energetics\n")
