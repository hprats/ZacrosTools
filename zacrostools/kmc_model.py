import os
import sys
from random import randint
from zacrostools.write_functions import write_header
from zacrostools.mechanism_input import ReactionModel
from zacrostools.energetics_input import EnergeticModel


class KMCModel:
    """A class that represents a KMC model.

    Parameters
    ----------
    gas_data: pd.DataFrame
        A Pandas DataFrame containing information about the gas molecules.
    mechanism_data: pd.DataFrame
        A Pandas DataFrame containing information about the reaction model.
    energetics_data: pd.DataFrame
        A Pandas DataFrame containing information about the energetic model.
    lattice_model: zacrostools.lattice_input.LatticeModel
        A lattice model
    """

    def __init__(self, gas_data, mechanism_data, energetics_data, lattice_model):
        self.path = None
        self.gas_data = gas_data
        self.reaction_model = ReactionModel(mechanism_data=mechanism_data)
        self.energetic_model = EnergeticModel(energetics_data=energetics_data)
        self.lattice_model = lattice_model

    def create_job_dir(self, path, temperature, pressure, reporting_scheme='on event 10000', stopping_criteria=None,
                       manual_scaling=None, auto_scaling_steps=None, auto_scaling_tags=None):
        """

        Parameters
        ----------
        path: str
            The path for the job directory where input files will be written
        temperature: float
            Reaction temperature (in K)
        pressure: dict
            Partial pressures of all gas species (in bar), e.g. {'CO': 1.0, 'O2': 0.001}
        reporting_scheme: str, optional
            Reporting scheme in Zacros format. Default value: 'on event 100000'
        stopping_criteria: dict, optional
            Stopping criteria in Zacros format. Must contain the following keys: 'max_steps', 'max_time' and 'wall_time'
            Default value: {'max_steps': 'infinity', 'max_time': 'infinity', 'wall_time': 86400}
        manual_scaling: dict, optional
            Step names (keys) and their corresponding manual scaling factors (values) e.g. {'CO_diffusion': 1.0e-1,
            'O_diffusion': 1.0e-2}
            Default value: {}
        auto_scaling_steps: list of str, optional
            Steps that will be marked as 'stiffness_scalable' in mechanism_input.dat.
            Default value: []
        auto_scaling_tags: dict, optional
            Keywords controlling the dynamic scaling algorithm and their corresponding values, e.g. {'check_every': 500,
            'min_separation': 400.0, 'max_separation': 600.0}.
            Default value: {}
        """

        if stopping_criteria is None:
            stopping_criteria = {'max_steps': 'infinity', 'max_time': 'infinity', 'wall_time': 86400}
        if manual_scaling is None:
            manual_scaling = {}
        if auto_scaling_steps is None:
            auto_scaling_steps = []
        if auto_scaling_tags is None:
            auto_scaling_tags = {}
        if len(auto_scaling_steps) == 0 and len(auto_scaling_tags) > 0:
            sys.exit('ERROR: auto_scaling_tags defined but no steps are stiffness scalable.')
        self.path = path
        if not os.path.exists(self.path):
            os.mkdir(self.path)
            self.write_simulation_input(temperature=temperature, pressure=pressure, reporting_scheme=reporting_scheme,
                                        stopping_criteria=stopping_criteria, auto_scaling_tags=auto_scaling_tags)
            self.reaction_model.write_mechanism_input(path=self.path, temperature=temperature, gas_data=self.gas_data,
                                                      manual_scaling=manual_scaling,
                                                      auto_scaling_steps=auto_scaling_steps)
            self.energetic_model.write_energetics_input(path=self.path)
            self.lattice_model.write_lattice_input(path=self.path)
        else:
            print(f'{self.path} already exists (nothing done)')

    def write_simulation_input(self, temperature, pressure, reporting_scheme, stopping_criteria, auto_scaling_tags):
        """Writes the simulation_input.dat file"""
        gas_specs_names = [x for x in self.gas_data.index]
        surf_specs_names = [x.replace('_point', '') for x in self.energetic_model.df.index if '_point' in x]
        surf_specs_names = [x + '*' * int(self.energetic_model.df.loc[f'{x}_point', 'sites']) for x in surf_specs_names]
        surf_specs_dent = [x.count('*') for x in surf_specs_names]
        write_header(f"{self.path}/simulation_input.dat")
        with open(f"{self.path}/simulation_input.dat", 'a') as infile:
            infile.write('random_seed\t'.expandtabs(26) + str(randint(100000, 999999)) + '\n')
            infile.write('temperature\t'.expandtabs(26) + str(float(temperature)) + '\n')
            p_tot = sum(pressure.values())
            infile.write('pressure\t'.expandtabs(26) + str(p_tot) + '\n')
            infile.write('n_gas_species\t'.expandtabs(26) + str(len(gas_specs_names)) + '\n')
            infile.write('gas_specs_names\t'.expandtabs(26) + " ".join(str(x) for x in gas_specs_names) + '\n')
            tags_dict = ['gas_energy', 'gas_molec_weight']
            tags_zacros = ['gas_energies', 'gas_molec_weights']
            for tag1, tag2 in zip(tags_dict, tags_zacros):
                tag_list = [self.gas_data.loc[x, tag1] for x in gas_specs_names]
                infile.write(f'{tag2}\t'.expandtabs(26) + " ".join(str(x) for x in tag_list) + '\n')
            try:
                gas_molar_frac_list = [pressure[x] / p_tot for x in gas_specs_names]
            except KeyError as ke:
                print(f"Key not found in 'pressure' dictionary: {ke}")
                print(f"When calling KMCModel.create_job_dir(), 'pressure' dictionary must contain the names of all "
                      f"gas species ")
            infile.write(f'gas_molar_fracs\t'.expandtabs(26) + " ".join(str(x) for x in gas_molar_frac_list) + '\n')
            infile.write('n_surf_species\t'.expandtabs(26) + str(len(surf_specs_names)) + '\n')
            infile.write('surf_specs_names\t'.expandtabs(26) + " ".join(str(x) for x in surf_specs_names) + '\n')
            infile.write('surf_specs_dent\t'.expandtabs(26) + " ".join(str(x) for x in surf_specs_dent) + '\n')
            for tag in ['snapshots', 'process_statistics', 'species_numbers']:
                infile.write((tag + '\t').expandtabs(26) + reporting_scheme + '\n')
            for tag in ['max_steps', 'max_time', 'wall_time']:
                infile.write((tag + '\t').expandtabs(26) + str(stopping_criteria[tag]) + '\n')
            if len(auto_scaling_tags) > 0:
                infile.write(f"enable_stiffness_scaling\n")
                for tag in auto_scaling_tags:
                    infile.write((tag + '\t').expandtabs(26) + str(auto_scaling_tags[tag]) + '\n')
            infile.write(f"finish\n")
