from random import randint
from typing import Union, Optional
from pathlib import Path

from zacrostools.header import write_header
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
                       job_path: str,
                       temperature: Union[float, int],
                       pressure: dict,
                       reporting_scheme: Optional[dict] = None,
                       stopping_criteria: Optional[dict] = None,
                       manual_scaling: Optional[dict] = None,
                       stiffness_scaling_algorithm: Optional[str] = None,
                       stiffness_scalable_steps: Union[list, str, None] = None,
                       stiffness_scalable_symmetric_steps: Optional[list] = None,
                       stiffness_scaling_tags: Optional[dict] = None,
                       additional_keywords: Optional[list] = None,
                       sig_figs_energies: int = 8,
                       sig_figs_pe: int = 8,
                       sig_figs_lattice: int = 8,
                       random_seed: Optional[int] = None,
                       version: Union[float, int] = 5.0):
        """
        Create a job directory and write the necessary input files for the KMC simulation.

        Parameters
        ----------
        job_path : str
            The path for the job directory where input files will be written.
        temperature : float or int
            Reaction temperature (in K).
        pressure : dict
            Partial pressures of all gas species (in bar), e.g., {'CO': 1.0, 'O2': 0.001}.
        reporting_scheme : dict, optional
            Reporting scheme in Zacros format. Must contain the following keys:
            'snapshots', 'process_statistics', and 'species_numbers'.
            Default is {'snapshots': 'on event 10000',
                        'process_statistics': 'on event 10000',
                        'species_numbers': 'on event 10000'}.
        stopping_criteria : dict, optional
            Stopping criteria in Zacros format. Must contain the following keys:
            'max_steps', 'max_time', and 'wall_time'.
            Default is {'max_steps': 'infinity',
                        'max_time': 'infinity',
                        'wall_time': 86400}.
        manual_scaling : dict, optional
            Dictionary mapping step names to their corresponding manual scaling factors, e.g.,
            {'CO_diffusion': 1.0e-1, 'O_diffusion': 1.0e-2}. Default is {}.
        stiffness_scaling_algorithm : str, optional
            Algorithm used for stiffness scaling. Allowed values are None (default), 'legacy', or 'prats2024'.
        stiffness_scalable_steps : list of str or 'all', optional
            Steps that will be marked as 'stiffness_scalable' in mechanism_input.dat.
            Can be provided as a list of step names or the string 'all' to indicate that all steps
            (except those specified in stiffness_scalable_symmetric_steps) are stiffness scalable.
            Default is [].
        stiffness_scalable_symmetric_steps : list of str, optional
            Steps that will be marked as 'stiffness_scalable_symmetric' in mechanism_input.dat.
            Default is [].
        stiffness_scaling_tags : dict, optional
            Keywords controlling the dynamic stiffness scaling algorithm and their corresponding values, e.g.,
            {'check_every': 500, 'min_separation': 400.0, ...}.
            The correct types are: integer for 'check_every' and 'min_noccur', and float for all others.
            Default is {}
        additional_keywords : list of str, optional
            Additional keywords to append to simulation_input.dat that are currently not supported by zacrostools,
            e.g., ['event_report on']. Each keyword will be written on its own line.
            Default is None.
        sig_figs_energies : int, optional
            Number of significant figures for energy values in input files.
            Default is 8.
        sig_figs_pe : int, optional
            Number of significant figures for pre-exponential factors in mechanism_input.dat.
            Default is 8.
        sig_figs_lattice : int, optional
            Number of significant figures for coordinates in lattice_input.dat.
            Default is 8.
        random_seed : int, optional
            The seed for the random number generator. If not specified, a random seed will be generated.
            Default is None.
        version : float or int, optional
            The Zacros version. Can be a single integer (e.g. 4) or float (e.g. 4.2 or 5.1).
        """
        # Parse and validate parameters
        parsed_params = self._parse_parameters(
            reporting_scheme=reporting_scheme,
            stopping_criteria=stopping_criteria,
            manual_scaling=manual_scaling,
            stiffness_scaling_algorithm=stiffness_scaling_algorithm,
            stiffness_scalable_steps=stiffness_scalable_steps,
            stiffness_scalable_symmetric_steps=stiffness_scalable_symmetric_steps,
            stiffness_scaling_tags=stiffness_scaling_tags,
            version=version
        )

        # Unpack parsed parameters
        reporting_scheme = parsed_params['reporting_scheme']
        stopping_criteria = parsed_params['stopping_criteria']
        manual_scaling = parsed_params['manual_scaling']
        stiffness_scaling_algorithm = parsed_params['stiffness_scaling_algorithm']
        stiffness_scalable_steps = parsed_params['stiffness_scalable_steps']
        stiffness_scalable_symmetric_steps = parsed_params['stiffness_scalable_symmetric_steps']
        stiffness_scaling_tags = parsed_params['stiffness_scaling_tags']

        additional_keywords = additional_keywords or []

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
                additional_keywords=additional_keywords,
                sig_figs_energies=sig_figs_energies,
                random_seed=random_seed,
                version=version)
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
                          stiffness_scaling_tags,
                          version):
        """
        Parse and validate the parameters provided to create_job_dir.
        """
        # [Reporting scheme and stopping criteria processing as before...]
        allowed_reporting_keys = {'snapshots', 'process_statistics', 'species_numbers'}
        default_reporting_scheme = {
            'snapshots': 'on event 10000',
            'process_statistics': 'on event 10000',
            'species_numbers': 'on event 10000'
        }
        if reporting_scheme is None:
            reporting_scheme = default_reporting_scheme
        else:
            reporting_scheme = {key: reporting_scheme.get(key, default_reporting_scheme[key])
                                for key in allowed_reporting_keys}

        allowed_stopping_keys = {'max_steps', 'max_time', 'wall_time'}
        default_stopping_criteria = {
            'max_steps': 'infinity',
            'max_time': float(1.0e+10),
            'wall_time': 86400
        }
        if stopping_criteria is None:
            stopping_criteria = default_stopping_criteria
        else:
            stopping_criteria = {key: stopping_criteria.get(key, default_stopping_criteria[key])
                                 for key in allowed_stopping_keys}

        # Validate 'max_steps', 'max_time' and 'wall_time'
        if 'max_steps' in stopping_criteria:
            ms = stopping_criteria['max_steps']
            if ms != 'infinity' and not isinstance(ms, int):
                raise KMCModelError(
                    f"'max_steps' must be either 'infinity' or an integer, got {ms}."
                )
        if 'max_time' in stopping_criteria:
            mt = stopping_criteria['max_time']
            if mt != 'infinity' and not isinstance(mt, float):
                raise KMCModelError(
                    f"'max_time' must be either 'infinity' or a float, got {mt}."
                )
        if 'wall_time' in stopping_criteria:
            wt = stopping_criteria['wall_time']
            if not isinstance(wt, int):
                raise KMCModelError(
                    f"'wall_time' must be an integer, got {wt}."
                )

        # Manual scaling
        if manual_scaling is None:
            manual_scaling = {}

        # Handle stiffness_scalable_steps if set to 'all'
        if isinstance(stiffness_scalable_steps, str):
            if stiffness_scalable_steps.lower() == 'all':
                # Assign all step names from the reaction model except those in stiffness_scalable_symmetric_steps
                all_steps = list(self.reaction_model.df.index)
                stiffness_scalable_steps = [step for step in all_steps
                                            if step not in stiffness_scalable_symmetric_steps]
            else:
                raise KMCModelError(
                    "Invalid value for stiffness_scalable_steps: if provided as a string, only 'all' is allowed."
                )

        # Version-specific stiffness scaling validation
        if stiffness_scalable_steps is None:
            stiffness_scalable_steps = []
        if stiffness_scalable_symmetric_steps is None:
            stiffness_scalable_symmetric_steps = []
        if stiffness_scaling_tags is None:
            stiffness_scaling_tags = {}

        if float(version) < 3.0:
            if (stiffness_scaling_algorithm is not None or
                    (stiffness_scalable_steps not in (None, []) and len(stiffness_scalable_steps) > 0) or
                    (stiffness_scalable_symmetric_steps not in (None, []) and len(
                        stiffness_scalable_symmetric_steps) > 0) or
                    (stiffness_scaling_tags not in (None, {}) and len(stiffness_scaling_tags) > 0)):
                raise KMCModelError("Stiffness scaling is not implemented for Zacros versions lower than 3.")
        elif 3.0 <= float(version) < 5.0:
            if stiffness_scaling_algorithm is not None:
                print(
                    "Warning: 'stiffness_scaling_algorithm' parameter is not allowed for Zacros versions lower than 5. Ignoring it.")
                stiffness_scaling_algorithm = None
            if stiffness_scalable_symmetric_steps not in (None, []) and len(stiffness_scalable_symmetric_steps) > 0:
                print(
                    "Warning: 'stiffness_scalable_symmetric_steps' parameter is not allowed for Zacros versions lower than 5. Ignoring it.")
                stiffness_scalable_symmetric_steps = []
        else:
            allowed_scaling_algorithms = {'legacy', 'prats2024'}
            if stiffness_scaling_algorithm is not None:
                if stiffness_scaling_algorithm not in allowed_scaling_algorithms:
                    raise KMCModelError(
                        f"Invalid stiffness_scaling_algorithm '{stiffness_scaling_algorithm}'. "
                        f"Allowed values are 'legacy' or 'prats2024'."
                    )
            if stiffness_scaling_algorithm is None:
                if stiffness_scalable_steps or stiffness_scalable_symmetric_steps or stiffness_scaling_tags:
                    stiffness_scaling_algorithm = 'legacy'
                else:
                    stiffness_scaling_algorithm = None

        if float(version) >= 5.0:
            if stiffness_scaling_algorithm in {'legacy', 'prats2024'}:
                if not stiffness_scalable_steps and not stiffness_scalable_symmetric_steps:
                    raise KMCModelError(
                        "stiffness_scaling_algorithm selected but no steps are stiffness scalable."
                    )
        # Validate stiffness scaling tags
        if float(version) >= 5.0:
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
        else:
            allowed_tags = {
                'check_every',
                'min_separation',
                'max_separation',
                'max_qequil_separation',
                'tol_part_equil_ratio',
                'stiffn_coeff_threshold',
                'scaling_factor'
            }

        if stiffness_scaling_tags:
            invalid_tags = set(stiffness_scaling_tags.keys()) - allowed_tags
            if invalid_tags:
                raise KMCModelError(
                    f"Invalid stiffness_scaling_tags keys for Zacros version {version}: "
                    f"{invalid_tags}. Allowed keys are: {allowed_tags}."
                )
            for tag, value in stiffness_scaling_tags.items():
                if tag in ['check_every', 'min_noccur']:
                    if not isinstance(value, int):
                        raise KMCModelError(
                            f"Invalid type for stiffness_scaling_tags '{tag}': expected int, got {type(value).__name__}."
                        )
                else:
                    if not isinstance(value, float):
                        raise KMCModelError(
                            f"Invalid type for stiffness_scaling_tags '{tag}': expected float, got {type(value).__name__}."
                        )

        return {
            'reporting_scheme': reporting_scheme,
            'stopping_criteria': stopping_criteria,
            'manual_scaling': manual_scaling,
            'stiffness_scaling_algorithm': stiffness_scaling_algorithm,
            'stiffness_scalable_steps': stiffness_scalable_steps,
            'stiffness_scalable_symmetric_steps': stiffness_scalable_symmetric_steps,
            'stiffness_scaling_tags': stiffness_scaling_tags
        }

    def write_simulation_input(self,
                               temperature,
                               pressure,
                               reporting_scheme,
                               stopping_criteria,
                               stiffness_scaling_algorithm,
                               stiffness_scalable_steps,
                               stiffness_scalable_symmetric_steps,
                               stiffness_scaling_tags,
                               additional_keywords=None,
                               sig_figs_energies=None,
                               random_seed=None,
                               version=None):
        """
        Writes the simulation_input.dat file.
        """
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

                # Handle stiffness scaling based on version:
                if float(version) >= 5.0:
                    if stiffness_scalable_steps or stiffness_scalable_symmetric_steps:
                        if stiffness_scaling_algorithm is None:
                            infile.write("enable_stiffness_scaling\n")
                        else:
                            infile.write('enable_stiffness_scaling\t'.expandtabs(26) + stiffness_scaling_algorithm + '\n')
                        for tag in stiffness_scaling_tags:
                            infile.write((tag + '\t').expandtabs(26) + str(stiffness_scaling_tags[tag]) + '\n')
                else:
                    if stiffness_scalable_steps:
                        infile.write("enable_stiffness_scaling\n")
                        for tag in stiffness_scaling_tags:
                            infile.write((tag + '\t').expandtabs(26) + str(stiffness_scaling_tags[tag]) + '\n')

                # Write any additional keywords
                for kw in additional_keywords:
                    infile.write(f"{kw}\n")

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
                    if surf_specs_name not in surf_specs or (
                            surf_specs_name in surf_specs and surf_specs_dent > surf_specs[surf_specs_name]):
                        surf_specs[surf_specs_name] = surf_specs_dent
                else:
                    raise KMCModelError(
                        f"Invalid lattice_state format for cluster '{cluster}': {site}")
        return surf_specs
