import os
import ast
import pandas as pd
from random import randint

import zacrostools.lattice_input
from zacrostools.write_functions import write_header
from zacrostools.mechanism_input import ReactionModel
from zacrostools.energetics_input import EnergeticModel
from zacrostools.custom_exceptions import *


def process_cell(cell):
    """ If the DataFrame is created from a CSV file, transform the cells that are read as str to list. Moreover, if a
    cell is empty (e.g. vib_energies_ts), set it to []"""
    if isinstance(cell, list):
        return cell
    elif isinstance(cell, str):
        try:
            # Attempt to parse the string as a list
            parsed_cell = ast.literal_eval(cell)
            # Ensure the parsed cell is actually a list
            if isinstance(parsed_cell, list):
                return parsed_cell
        except (ValueError, SyntaxError):
            raise ReactionModelError(f"Cell is not a list: {cell}.")
    elif pd.isna(cell) or cell == '':
        return []
    # Return an empty list if parsing fails or if the cell is of an unexpected type
    return []


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

    @enforce_types
    def __init__(self, gas_data: pd.DataFrame, mechanism_data: pd.DataFrame, energetics_data: pd.DataFrame,
                 lattice_model: zacrostools.lattice_input.LatticeModel):
        self.path = None

        """ If the DataFrame is created from a CSV file, transform the cells that are read as str to list and set empty 
        sells to []"""

        for column_name in ['inertia_moments', 'vib_energies']:
            if column_name in gas_data.columns:
                gas_data[column_name] = gas_data[column_name].apply(process_cell)
        self.gas_data = gas_data

        for column_name in ['initial', 'final', 'vib_energies_is', 'vib_energies_ts', 'vib_energies_fs']:
            if column_name in mechanism_data.columns:
                mechanism_data[column_name] = mechanism_data[column_name].apply(process_cell)
        self.reaction_model = ReactionModel(mechanism_data=mechanism_data)

        for column_name in ['lattice_state']:
            if column_name in energetics_data.columns:
                energetics_data[column_name] = energetics_data[column_name].apply(process_cell)
        self.energetic_model = EnergeticModel(energetics_data=energetics_data)

        self.lattice_model = lattice_model

        self.check_errors()

    def check_errors(self):
        """Checks for data consistency after initialization."""
        if self.lattice_model.lattice_type == 'default':
            if 'site_types' in self.reaction_model.df.columns:
                raise ReactionModelError("Remove 'site_types' from the reaction model when using a default lattice.")
            if 'site_types' in self.energetic_model.df.columns:
                raise EnergeticModelError("Remove 'site_types' from the energetic model when using a default lattice.")
        if self.lattice_model.lattice_type != 'default':
            if 'site_types' not in self.reaction_model.df.columns:
                raise ReactionModelError("'site_types' are missing in the reaction model.")
            if 'site_types' not in self.energetic_model.df.columns:
                raise EnergeticModelError("'site_types' are missing in the energetic model.")

    @enforce_types
    def create_job_dir(self,
                       # Mandatory arguments
                       path: str, temperature: Union[float, int], pressure: dict,
                       # Optional arguments
                       reporting_scheme: Union[dict, None] = None,
                       stopping_criteria: Union[dict, None] = None,
                       manual_scaling: Union[dict, None] = None,
                       stiffness_scaling_algorithm: Union[str, None] = None,
                       stiffness_scalable_steps: Union[list, None] = None,
                       stiffness_scalable_symmetric_steps: Union[list, None] = None,
                       stiffness_scaling_tags: Union[dict, None] = None,
                       sig_figs_energies: int = 16, sig_figs_pe: int = 16,
                       random_seed: Union[int, None] = None):
        """

        Parameters
        ----------
        path: str
            The path for the job directory where input files will be written
        temperature: float
            Reaction temperature (in K)
        pressure: dict
            Partial pressures of all gas species (in bar), e.g. {'CO': 1.0, 'O2': 0.001}
        reporting_scheme: dict, optional
            Reporting scheme in Zacros format. Must contain the following keys: 'snapshots', 'process_statistics' and
            'species_numbers'
            Default value: {'snapshots': 'on event 10000', 'process_statistics': 'on event 10000',
            'species_numbers': 'on event 10000'}
        stopping_criteria: dict, optional
            Stopping criteria in Zacros format. Must contain the following keys: 'max_steps', 'max_time' and 'wall_time'
            Default value: {'max_steps': 'infinity', 'max_time': 'infinity', 'wall_time': 86400}
        manual_scaling: dict, optional
            Step names (keys) and their corresponding manual scaling factors (values) e.g. {'CO_diffusion': 1.0e-1,
            'O_diffusion': 1.0e-2}
            Default value: {}
        stiffness_scaling_algorithm: str, optional
            Algorithm used for stiffness scaling. Possible values are None (default), legacy or prats2024
            Default value: None
        stiffness_scalable_steps: list of str, optional
            Steps that will be marked as 'stiffness_scalable' in mechanism_input.dat.
            Default value: []
        stiffness_scalable_symmetric_steps: list of str, optional
            Steps that will be marked as 'stiffness_scalable_symmetric' in mechanism_input.dat.
            Default value: []
        stiffness_scaling_tags: dict, optional
            Keywords controlling the dynamic scaling algorithm and their corresponding values, e.g. {'check_every': 500,
            'min_separation': 400.0, 'max_separation': 600.0}.
            Default value: {}
        sig_figs_energies: int, optional
            Number of significant figures used when writing 'cluster_eng' in energetics_input.dat and 'activ_eng' in
            mechanism_input.dat.
            Default value: 16
        sig_figs_pe: int, optional
            Number of significant figures used when writing 'pre_expon' and 'pe_ratio' in mechanism_input.dat.
            Default value: 16
        random_seed: int, optional
            The integer seed of the random number generator. If not specified, ZacrosTools will generate one.
            Default value: None
        """

        if reporting_scheme is None:
            reporting_scheme = {'snapshots': 'on event 10000', 'process_statistics': 'on event 10000',
                                'species_numbers': 'on event 10000'}
        if stopping_criteria is None:
            stopping_criteria = {'max_steps': 'infinity', 'max_time': 'infinity', 'wall_time': 86400}
        if manual_scaling is None:
            manual_scaling = {}
        if stiffness_scalable_steps is None:
            stiffness_scalable_steps = []
        if stiffness_scalable_symmetric_steps is None:
            stiffness_scalable_symmetric_steps = []
        if stiffness_scaling_tags is None:
            stiffness_scaling_tags = {}
        if len(stiffness_scaling_tags) > 0:
            if len(stiffness_scalable_steps) == 0 and len(stiffness_scalable_symmetric_steps) == 0:
                raise InconsistentDataError("'stiffness_scaling_tags' defined but no steps are stiffness scalable")
        self.path = path
        if not os.path.exists(self.path):
            os.mkdir(self.path)
            self.write_simulation_input(
                temperature=temperature,
                pressure=pressure,
                reporting_scheme=reporting_scheme,
                stopping_criteria=stopping_criteria,
                stiffness_scaling_algorithm=stiffness_scaling_algorithm,
                stiffness_scalable_steps=stiffness_scalable_steps,
                stiffness_scalable_symmetric_steps=stiffness_scalable_symmetric_steps,
                stiffness_scaling_tags=stiffness_scaling_tags,
                sig_figs_energies=sig_figs_energies,
                random_seed=random_seed)
            self.reaction_model.write_mechanism_input(
                path=self.path,
                temperature=temperature,
                gas_data=self.gas_data,
                manual_scaling=manual_scaling,
                stiffness_scalable_steps=stiffness_scalable_steps,
                stiffness_scalable_symmetric_steps=stiffness_scalable_symmetric_steps,
                sig_figs_energies=sig_figs_energies,
                sig_figs_pe=sig_figs_pe)
            self.energetic_model.write_energetics_input(path=self.path,
                                                        sig_figs_energies=sig_figs_energies)
            self.lattice_model.write_lattice_input(path=self.path)
        else:
            print(f'{self.path} already exists (nothing done)')

    def write_simulation_input(self, temperature, pressure, reporting_scheme, stopping_criteria,
                               stiffness_scaling_algorithm, stiffness_scalable_steps,
                               stiffness_scalable_symmetric_steps, stiffness_scaling_tags,
                               sig_figs_energies, random_seed):
        """Writes the simulation_input.dat file"""

        allowed_stiffness_scaling_algorithms = [
            'legacy',
            'prats2024'
        ]

        allowed_stiffness_scaling_tags = [
            'check_every',
            'min_separation',
            'max_separation',
            'max_qequil_separation',
            'tol_part_equil_ratio',
            'stiffn_coeff_threshold',
            'scaling_factor',
            'upscaling_factor',
            'upscaling_limit',
            'downscaling_limit',
            'min_noccur'
        ]

        gas_specs_names = [x for x in self.gas_data.index]
        surf_specs = self.get_surf_specs()
        write_header(f"{self.path}/simulation_input.dat")
        with open(f"{self.path}/simulation_input.dat", 'a') as infile:
            if random_seed is None:
                infile.write('random_seed\t'.expandtabs(26) + str(randint(100000, 999999)) + '\n')
            else:
                infile.write('random_seed\t'.expandtabs(26) + str(random_seed) + '\n')
            infile.write('temperature\t'.expandtabs(26) + str(float(temperature)) + '\n')
            p_tot = sum(pressure.values())
            infile.write('pressure\t'.expandtabs(26) + str(float(p_tot)) + '\n')
            infile.write('n_gas_species\t'.expandtabs(26) + str(len(gas_specs_names)) + '\n')
            infile.write('gas_specs_names\t'.expandtabs(26) + " ".join(str(x) for x in gas_specs_names) + '\n')
            tags_dict = ['gas_energy', 'gas_molec_weight']
            tags_zacros = ['gas_energies', 'gas_molec_weights']
            for tag1, tag2 in zip(tags_dict, tags_zacros):
                tag_list = [self.gas_data.loc[x, tag1] for x in gas_specs_names]
                if tag1 == 'gas_energy':
                    formatted_tag_list = [f'{x:.{sig_figs_energies}f}' for x in tag_list]
                    infile.write(f'{tag2}\t'.expandtabs(26) + " ".join(formatted_tag_list) + '\n')
                else:
                    infile.write(f'{tag2}\t'.expandtabs(26) + " ".join(str(x) for x in tag_list) + '\n')
            try:
                gas_molar_frac_list = [pressure[x] / p_tot for x in gas_specs_names]
            except KeyError as ke:
                print(f"Key not found in 'pressure' dictionary: {ke}")
                print(f"When calling KMCModel.create_job_dir(), 'pressure' dictionary must contain the names of all "
                      f"gas species ")
            infile.write(f'gas_molar_fracs\t'.expandtabs(26) + " ".join(str(x) for x in gas_molar_frac_list) + '\n')
            infile.write('n_surf_species\t'.expandtabs(26) + str(len(surf_specs)) + '\n')
            infile.write('surf_specs_names\t'.expandtabs(26) + " ".join(str(x) for x in surf_specs.keys()) + '\n')
            infile.write('surf_specs_dent\t'.expandtabs(26) + " ".join(str(x) for x in surf_specs.values()) + '\n')
            for tag in ['snapshots', 'process_statistics', 'species_numbers']:
                infile.write((tag + '\t').expandtabs(26) + str(reporting_scheme[tag]) + '\n')
            for tag in ['max_steps', 'max_time', 'wall_time']:
                infile.write((tag + '\t').expandtabs(26) + str(stopping_criteria[tag]) + '\n')
            if len(stiffness_scalable_steps) > 0 or len(stiffness_scalable_symmetric_steps) > 0:
                if stiffness_scaling_algorithm is None:
                    infile.write(f"enable_stiffness_scaling\n")
                else:
                    infile.write(
                        'enable_stiffness_scaling\t'.expandtabs(26) + stiffness_scaling_algorithm + '\n')
                for tag in stiffness_scaling_tags:
                    if tag in allowed_stiffness_scaling_tags:
                        infile.write((tag + '\t').expandtabs(26) + str(stiffness_scaling_tags[tag]) + '\n')
                    else:
                        raise InconsistentDataError(f"Invalid tag in 'stiffness_scaling_tags': {tag}")
            infile.write(f"finish\n")

    def get_surf_specs(self):
        # Identify all surf_specs and their corresponding dentates from the energetic_model dataframe
        # Used to write 'surf_specs_names' and 'surf_specs_dent' in the simulation_input.dat file
        surf_specs = {}
        for cluster in self.energetic_model.df.index:
            lattice_state = self.energetic_model.df.loc[cluster, 'lattice_state']
            for site in lattice_state:
                if '&' not in site:
                    surf_specs_name = site.split()[1]
                    surf_specs_dent = int(site.split()[2])
                    if surf_specs_name not in surf_specs or (
                            surf_specs_name in surf_specs and surf_specs_dent > surf_specs[surf_specs_name]):
                        surf_specs[surf_specs_name] = surf_specs_dent
        return surf_specs
