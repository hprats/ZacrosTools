from random import randint
from typing import Union, Optional
from pathlib import Path

from zacrostools.write_functions import write_header
from zacrostools.lattice_model import LatticeModel
from zacrostools.energetics_model import EnergeticsModel
from zacrostools.reaction_model import ReactionModel
from zacrostools.gas_model import GasModel
from zacrostools.custom_exceptions import KMCModelError
from zacrostools.custom_exceptions import enforce_types


class KMCModel:
    """
    Represents a Kinetic Monte Carlo (KMC) model.

    Parameters
    ----------
    gas_model : GasModel
        An instance containing information about the gas molecules.
    reaction_model : ReactionModel
        An instance containing information about the reaction model.
    energetics_model : EnergeticsModel
        An instance containing information about the energetic model.
    lattice_model : LatticeModel
        An instance containing information about the lattice model.

    Raises
    ------
    KMCModelError
        If there are inconsistencies in the model configurations.
    """

    @enforce_types
    def __init__(self,
                 gas_model: GasModel,
                 reaction_model: ReactionModel,
                 energetics_model: EnergeticsModel,
                 lattice_model: LatticeModel):
        self.job_dir: Optional[Path] = None
        self.gas_model = gas_model
        self.reaction_model = reaction_model
        self.energetics_model = energetics_model
        self.lattice_model = lattice_model
        self.check_errors()

    def check_errors(self):
        """
        Check for data consistency after initialization.

        Raises
        ------
        KMCModelError
            If there are inconsistencies in the model configurations.
        """
        if self.lattice_model.lattice_type == 'default_choice':
            if 'site_types' in self.reaction_model.df.columns:
                raise KMCModelError("Remove 'site_types' from the reaction model when using a default lattice.")
            if 'site_types' in self.energetics_model.df.columns:
                raise KMCModelError("Remove 'site_types' from the energetic model when using a default lattice.")
        else:
            if 'site_types' not in self.reaction_model.df.columns:
                raise KMCModelError("'site_types' are missing in the reaction model.")
            if 'site_types' not in self.energetics_model.df.columns:
                raise KMCModelError("'site_types' are missing in the energetic model.")

    @enforce_types
    def create_job_dir(self,
                       # Mandatory arguments
                       job_path: str,
                       temperature: Union[float, int],
                       pressure: dict,
                       # Optional arguments
                       reporting_scheme: Union[dict, None] = None,
                       stopping_criteria: Union[dict, None] = None,
                       manual_scaling: Union[dict, None] = None,
                       stiffness_scaling_algorithm: Union[str, None] = None,
                       stiffness_scalable_steps: Union[list, None] = None,
                       stiffness_scalable_symmetric_steps: Union[list, None] = None,
                       stiffness_scaling_tags: Union[dict, None] = None,
                       sig_figs_energies: int = 8,
                       sig_figs_pe: int = 8,
                       sig_figs_lattice: int = 8,
                       random_seed: Union[int, None] = None):
        """
        Create a job directory and write necessary input files for the KMC simulation.

        Parameters
        ----------
        job_path : str
            The path for the job directory where input files will be written.
        temperature : float or int
            Reaction temperature (in K).
        pressure : dict
            Partial pressures of all gas species (in bar), e.g., `{'CO': 1.0, 'O2': 0.001}`.
        reporting_scheme : dict, optional
            Reporting scheme in Zacros format. Must contain the following keys:
            `'snapshots'`, `'process_statistics'`, and `'species_numbers'`.
            Default is `{'snapshots': 'on event 10000', 'process_statistics': 'on event 10000', 'species_numbers': 'on event 10000'}`.
        stopping_criteria : dict, optional
            Stopping criteria in Zacros format. Must contain the following keys:
            `'max_steps'`, `'max_time'`, and `'wall_time'`.
            Default is `{'max_steps': 'infinity', 'max_time': 'infinity', 'wall_time': 86400}`.
        manual_scaling : dict, optional
            Step names (keys) and their corresponding manual scaling factors (values), e.g.,
            `{'CO_diffusion': 1.0e-1, 'O_diffusion': 1.0e-2}`.
            Default is `{}`.
        stiffness_scaling_algorithm : str, optional
            Algorithm used for stiffness scaling. Possible values are `None` (default), `'legacy'`, or `'prats2024'`.
            Default is `None`.
        stiffness_scalable_steps : list of str, optional
            Steps that will be marked as `'stiffness_scalable'` in `mechanism_input.dat`.
            Default is `[]`.
        stiffness_scalable_symmetric_steps : list of str, optional
            Steps that will be marked as `'stiffness_scalable_symmetric'` in `mechanism_input.dat`.
            Default is `[]`.
        stiffness_scaling_tags : dict, optional
            Keywords controlling the dynamic scaling algorithm and their corresponding values, e.g.,
            `{'check_every': 500, 'min_separation': 400.0, 'max_separation': 600.0}`.
            Default is `{}`.
        sig_figs_energies : int, optional
            Number of significant figures used when writing `'cluster_eng'` in `energetics_input.dat`,
            `'activ_eng'` in `mechanism_input.dat`, and `'gas_energies'` in `simulation_input.dat`.
            Default is `8`.
        sig_figs_pe : int, optional
            Number of significant figures used when writing `'pre_expon'` and `'pe_ratio'` in `mechanism_input.dat`.
            Default is `8`.
        sig_figs_lattice : int, optional
            Number of significant figures used when writing coordinates in `lattice_input.dat`.
            Default is `8`.
        random_seed : int, optional
            The integer seed of the random number generator. If not specified, ZacrosTools will generate one.
            Default is `None`.

        Raises
        ------
        KMCModelError
            If there are inconsistencies in the stiffness scaling configuration or during file writing.
        """

        # Parse and validate parameters
        parsed_params = self._parse_parameters(
            reporting_scheme=reporting_scheme,
            stopping_criteria=stopping_criteria,
            manual_scaling=manual_scaling,
            stiffness_scaling_algorithm=stiffness_scaling_algorithm,
            stiffness_scalable_steps=stiffness_scalable_steps,
            stiffness_scalable_symmetric_steps=stiffness_scalable_symmetric_steps,
            stiffness_scaling_tags=stiffness_scaling_tags
        )

        # Unpack parsed parameters
        reporting_scheme = parsed_params['reporting_scheme']
        stopping_criteria = parsed_params['stopping_criteria']
        manual_scaling = parsed_params['manual_scaling']
        stiffness_scaling_algorithm = parsed_params['stiffness_scaling_algorithm']
        stiffness_scalable_steps = parsed_params['stiffness_scalable_steps']
        stiffness_scalable_symmetric_steps = parsed_params['stiffness_scalable_symmetric_steps']
        stiffness_scaling_tags = parsed_params['stiffness_scaling_tags']

        self.job_dir = Path(job_path)
        if not self.job_dir.exists():
            self.job_dir.mkdir(parents=True, exist_ok=True)
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
                output_dir=self.job_dir,
                temperature=temperature,
                gas_model=self.gas_model,
                manual_scaling=manual_scaling,
                stiffness_scalable_steps=stiffness_scalable_steps,
                stiffness_scalable_symmetric_steps=stiffness_scalable_symmetric_steps,
                sig_figs_energies=sig_figs_energies,
                sig_figs_pe=sig_figs_pe)
            self.energetics_model.write_energetics_input(
                output_dir=self.job_dir,
                sig_figs_energies=sig_figs_energies)
            self.lattice_model.write_lattice_input(
                output_dir=self.job_dir,
                sig_figs=sig_figs_lattice)
        else:
            print(f'{self.job_dir} already exists (nothing done)')

    def _parse_parameters(self,
                          reporting_scheme,
                          stopping_criteria,
                          manual_scaling,
                          stiffness_scaling_algorithm,
                          stiffness_scalable_steps,
                          stiffness_scalable_symmetric_steps,
                          stiffness_scaling_tags):
        """
        Parse and validate the parameters provided to create_job_dir.

        Returns
        -------
        dict
            A dictionary containing parsed and validated parameters.

        Raises
        ------
        KMCModelError
            If any of the parameters fail validation.
        """

        # Define allowed keys and defaults for reporting_scheme
        allowed_reporting_keys = {'snapshots', 'process_statistics', 'species_numbers'}
        default_reporting_scheme = {
            'snapshots': 'on event 10000',
            'process_statistics': 'on event 10000',
            'species_numbers': 'on event 10000'
        }

        if reporting_scheme is None:
            reporting_scheme = default_reporting_scheme
        else:
            # Filter out invalid keys and apply defaults
            reporting_scheme = {key: reporting_scheme.get(key, default_reporting_scheme[key])
                                for key in allowed_reporting_keys}

        allowed_stopping_keys = {'max_steps', 'max_time', 'wall_time'}
        default_stopping_criteria = {
            'max_steps': 'infinity',
            'max_time': 'infinity',
            'wall_time': 86400
        }

        if stopping_criteria is None:
            stopping_criteria = default_stopping_criteria
        else:
            # Filter out invalid keys and apply defaults
            stopping_criteria = {key: stopping_criteria.get(key, default_stopping_criteria[key])
                                 for key in allowed_stopping_keys}

        if manual_scaling is None:
            manual_scaling = {}

        allowed_scaling_algorithms = {'legacy', 'prats2024'}
        if stiffness_scaling_algorithm is not None:
            if stiffness_scaling_algorithm not in allowed_scaling_algorithms:
                raise KMCModelError(
                    f"Invalid stiffness_scaling_algorithm '{stiffness_scaling_algorithm}'. "
                    f"Allowed values are 'legacy' or 'prats2024'.")

        if stiffness_scaling_algorithm is None:
            if stiffness_scalable_steps or stiffness_scalable_symmetric_steps or stiffness_scaling_tags:
                stiffness_scaling_algorithm = 'legacy'
            else:
                stiffness_scaling_algorithm = None

        if stiffness_scalable_steps is None:
            stiffness_scalable_steps = []

        if stiffness_scalable_symmetric_steps is None:
            stiffness_scalable_symmetric_steps = []

        if stiffness_scaling_tags is None:
            stiffness_scaling_tags = {}

        if stiffness_scaling_algorithm == 'legacy':
            allowed_tags = {
                'check_every',
                'min_separation',
                'max_separation',
                'max_qequil_separation',
                'tol_part_equil_ratio',
                'stiffn_coeff_threshold',
                'scaling_factor'
            }
        elif stiffness_scaling_algorithm == 'prats2024':
            allowed_tags = {
                'check_every',
                'min_separation',
                'max_separation',
                'tol_part_equil_ratio',
                'upscaling_factor',
                'upscaling_limit',
                'downscaling_limit',
                'min_noccur'
            }
        else:
            allowed_tags = set()

        if stiffness_scaling_tags:
            if stiffness_scaling_algorithm is None:
                raise KMCModelError(
                    "stiffness_scaling_tags provided but no stiffness_scaling_algorithm selected.")
            invalid_tags = set(stiffness_scaling_tags.keys()) - allowed_tags
            if invalid_tags:
                raise KMCModelError(
                    f"Invalid stiffness_scaling_tags keys for algorithm '{stiffness_scaling_algorithm}': "
                    f"{invalid_tags}. Allowed keys are: {allowed_tags}.")

        if stiffness_scaling_algorithm in allowed_scaling_algorithms:
            if not stiffness_scalable_steps and not stiffness_scalable_symmetric_steps:
                raise KMCModelError(
                    "stiffness_scaling_algorithm selected but no steps are stiffness scalable.")

        return {
            'reporting_scheme': reporting_scheme,
            'stopping_criteria': stopping_criteria,
            'manual_scaling': manual_scaling,
            'stiffness_scaling_algorithm': stiffness_scaling_algorithm,
            'stiffness_scalable_steps': stiffness_scalable_steps,
            'stiffness_scalable_symmetric_steps': stiffness_scalable_symmetric_steps,
            'stiffness_scaling_tags': stiffness_scaling_tags
        }

    def write_simulation_input(self, temperature, pressure, reporting_scheme, stopping_criteria,
                               stiffness_scaling_algorithm, stiffness_scalable_steps,
                               stiffness_scalable_symmetric_steps, stiffness_scaling_tags,
                               sig_figs_energies, random_seed):
        """Writes the simulation_input.dat file."""

        gas_specs_names = list(self.gas_model.df.index)
        surf_specs = self.get_surf_specs()
        write_header(f"{self.job_dir}/simulation_input.dat")
        try:
            with open(f"{self.job_dir}/simulation_input.dat", 'a') as infile:
                # Handle random seed
                if random_seed is None:
                    infile.write('random_seed\t'.expandtabs(26) + str(randint(100000, 999999)) + '\n')
                else:
                    infile.write('random_seed\t'.expandtabs(26) + str(random_seed) + '\n')

                # Write temperature
                infile.write('temperature\t'.expandtabs(26) + str(float(temperature)) + '\n')

                # Write total pressure
                p_tot = sum(pressure.values())
                infile.write('pressure\t'.expandtabs(26) + str(float(p_tot)) + '\n')

                # Write number of gas species and their names
                infile.write('n_gas_species\t'.expandtabs(26) + str(len(gas_specs_names)) + '\n')
                infile.write('gas_specs_names\t'.expandtabs(26) + " ".join(str(x) for x in gas_specs_names) + '\n')

                # Write gas energies and molecular weights
                tags_dict = ['gas_energy', 'gas_molec_weight']
                tags_zacros = ['gas_energies', 'gas_molec_weights']
                for tag1, tag2 in zip(tags_dict, tags_zacros):
                    tag_list = [self.gas_model.df.loc[x, tag1] for x in gas_specs_names]
                    if tag1 == 'gas_energy':
                        formatted_tag_list = [f'{x:.{sig_figs_energies}f}' for x in tag_list]
                        infile.write(f'{tag2}\t'.expandtabs(26) + " ".join(formatted_tag_list) + '\n')
                    else:
                        infile.write(f'{tag2}\t'.expandtabs(26) + " ".join(str(x) for x in tag_list) + '\n')

                # Write gas molar fractions
                try:
                    gas_molar_frac_list = [pressure[x] / p_tot for x in gas_specs_names]
                except KeyError as ke:
                    print(f"Key not found in 'pressure' dictionary: {ke}")
                    print(f"When calling KMCModel.create_job_dir(), 'pressure' dictionary must contain the names of all "
                          f"gas species ")
                    gas_molar_frac_list = [0.0 for _ in gas_specs_names]  # Assign zero fractions for missing species

                infile.write(f'gas_molar_fracs\t'.expandtabs(26) + " ".join(str(x) for x in gas_molar_frac_list) + '\n')

                # Write number of surface species and their names and dentates
                infile.write('n_surf_species\t'.expandtabs(26) + str(len(surf_specs)) + '\n')
                infile.write('surf_specs_names\t'.expandtabs(26) + " ".join(str(x) for x in surf_specs.keys()) + '\n')
                infile.write('surf_specs_dent\t'.expandtabs(26) + " ".join(str(x) for x in surf_specs.values()) + '\n')

                # Write reporting scheme
                for tag in ['snapshots', 'process_statistics', 'species_numbers']:
                    infile.write((tag + '\t').expandtabs(26) + str(reporting_scheme.get(tag, '')) + '\n')

                # Write stopping criteria
                for tag in ['max_steps', 'max_time', 'wall_time']:
                    infile.write((tag + '\t').expandtabs(26) + str(stopping_criteria.get(tag, '')) + '\n')

                # Handle stiffness scaling
                if stiffness_scalable_steps or stiffness_scalable_symmetric_steps:
                    if stiffness_scaling_algorithm is None:
                        infile.write(f"enable_stiffness_scaling\n")
                    else:
                        infile.write(
                            'enable_stiffness_scaling\t'.expandtabs(26) + stiffness_scaling_algorithm + '\n')
                    for tag in stiffness_scaling_tags:
                        infile.write((tag + '\t').expandtabs(26) + str(stiffness_scaling_tags[tag]) + '\n')
                infile.write(f"finish\n")
        except IOError as e:
            raise KMCModelError(f"Failed to write to 'simulation_input.dat': {e}")

    def get_surf_specs(self):
        """
        Identify all surface species and their corresponding dentates from the `energetics_model` DataFrame.

        Used to write `'surf_specs_names'` and `'surf_specs_dent'` in the `simulation_input.dat` file.

        Returns
        -------
        dict
            A dictionary with surface species names as keys and dentates as values.

        Raises
        ------
        KMCModelError
            If the `lattice_state` format is invalid.
        """
        surf_specs = {}
        for cluster in self.energetics_model.df.index:
            lattice_state = self.energetics_model.df.loc[cluster, 'lattice_state']
            for site in lattice_state:
                # Assuming the format is '1 CO* 1' or similar
                parts = site.split()
                if len(parts) >= 3:
                    surf_specs_name = parts[1]
                    try:
                        surf_specs_dent = int(parts[2])
                    except ValueError:
                        raise KMCModelError(
                            f"Invalid dentate value in lattice_state for cluster '{cluster}': {parts[2]}")
                    # Update the surf_specs dictionary
                    if surf_specs_name not in surf_specs or (
                            surf_specs_name in surf_specs and surf_specs_dent > surf_specs[surf_specs_name]):
                        surf_specs[surf_specs_name] = surf_specs_dent
                else:
                    raise KMCModelError(
                        f"Invalid lattice_state format for cluster '{cluster}': {site}")
        return surf_specs
