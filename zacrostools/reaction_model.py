import ast
from pathlib import Path
from typing import Union, Optional
import pandas as pd
from zacrostools.write_functions import write_header
from zacrostools.calc_functions import calc_ads, calc_surf_proc
from zacrostools.custom_exceptions import ReactionModelError, enforce_types
from zacrostools.gas_model import GasModel


class ReactionModel:
    """
    Represents a KMC reaction model.

    Parameters
    ----------
    mechanism_data : pandas.DataFrame
        Information on the reaction model. The reaction name is taken as the index of each row.

        **Required columns**:

        - **initial** (list): Initial configuration in Zacros format, e.g., `['1 CO* 1', '2 * 1']`.
        - **final** (list): Final configuration in Zacros format, e.g., `['1 C* 1', '2 O* 1']`.
        - **activ_eng** (float): Activation energy (in eV).
        - **vib_energies_is** (list of float): Vibrational energies for the initial state (in meV). Do not include the ZPE.
        - **vib_energies_fs** (list of float): Vibrational energies for the final state (in meV). Do not include the ZPE.

        **Mandatory for adsorption steps**:

        - **molecule** (str): Gas-phase molecule involved. Only required for adsorption steps.
        - **area_site** (float): Area of adsorption site (in Å²). Only required for adsorption steps.

        **Mandatory for activated adsorption steps and surface reaction steps**:

        - **vib_energies_ts** (list of float): Vibrational energies for the transition state (in meV).
          For non-activated adsorption steps, this value can be either undefined or an empty list, i.e., `[]`.

        **Optional columns**:

        - **site_types** (str): The types of each site in the pattern. Required if `lattice_type is 'periodic_cell'`.
        - **neighboring** (str): Connectivity between sites involved, e.g., `'1-2'`. Default is `None`.
        - **prox_factor** (float): Proximity factor. Default is `None`.
        - **angles** (str): Angle between sites in Zacros format, e.g., `'1-2-3:180'`. Default is `None`.
        - **graph_multiplicity** (int or float): Graph multiplicity of the step. The computed pre-exponential factor
          will be divided by `graph_multiplicity`. Should be used in steps with the same initial and final configuration
          (symmetric steps), such as diffusions to the same site type. For instance, diffusion of A* from top to top
          should have a value of `2`. Default is `1`.

    Raises
    ------
    ReactionModelError
        If `mechanism_data` is not provided, contains duplicates, or is invalid.

    Examples
    --------
    Example DataFrame:

    | index             | site_types | initial                  | final                    | activ_eng | vib_energies_is    | vib_energies_fs    | molecule | area_site | vib_energies_ts   | neighboring | prox_factor | angles        | graph_multiplicity |
    |-------------------|------------|--------------------------|--------------------------|-----------|--------------------|--------------------|----------|-----------|-------------------|-------------|-------------|---------------|--------------------|
    | CO_adsorption     | '1'        | ['1 * 1']                | ['1 CO* 1']              | 0.0       | [200.0, 300.0]     | [150.0, 250.0]     | 'CO'     | 6.5       | []                | NaN         | NaN         | NaN           | NaN                |
    | Surface_reaction  | '1 1'      | ['1 CO* 1', '2 O* 1']    | ['1 * 1', '2 * 1']       | 0.5       | [200.0, 300.0, 400.0] | [150.0, 250.0, 350.0] | NaN      | NaN       | [250.0, 350.0, 450.0] | '1-2'       | 0.8         | '1-2-3:180'   | 2                  |

    """

    REQUIRED_COLUMNS = {
        'initial',
        'final',
        'activ_eng',
        'vib_energies_is',
        'vib_energies_fs'
    }
    REQUIRED_ADS_COLUMNS = {'molecule', 'area_site'}
    REQUIRED_ACTIVATED_COLUMNS = {'vib_energies_ts'}
    OPTIONAL_COLUMNS = {'site_types', 'neighboring', 'prox_factor', 'angles', 'graph_multiplicity'}
    LIST_COLUMNS = ['initial', 'final', 'vib_energies_is', 'vib_energies_fs', 'vib_energies_ts']

    @enforce_types
    def __init__(self, mechanism_data: pd.DataFrame = None):
        """
        Initialize the ReactionModel.

        Parameters
        ----------
        mechanism_data : pandas.DataFrame
            DataFrame containing the reaction mechanism data.

        Raises
        ------
        ReactionModelError
            If `mechanism_data` is not provided, contains duplicates, or is invalid.
        """
        if mechanism_data is None:
            raise ReactionModelError("mechanism_data must be provided as a Pandas DataFrame.")
        self.df = mechanism_data.copy()
        self._validate_dataframe()

    @classmethod
    def from_dict(cls, steps_dict: dict):
        """
        Create a ReactionModel instance from a dictionary.

        Parameters
        ----------
        steps_dict : dict
            Dictionary where keys are step names and values are dictionaries of step properties.

        Returns
        -------
        ReactionModel
            An instance of ReactionModel.

        Raises
        ------
        ReactionModelError
            If the instance cannot be created from the provided dictionary due to duplicates or invalid data.
        """
        try:
            df = pd.DataFrame.from_dict(steps_dict, orient='index')

            # Check for duplicate step names
            if df.index.duplicated().any():
                duplicates = df.index[df.index.duplicated()].unique().tolist()
                raise ReactionModelError(f"Duplicate step names found in dictionary: {duplicates}")

            return cls.from_df(df)
        except ReactionModelError:
            raise
        except Exception as e:
            raise ReactionModelError(f"Failed to create ReactionModel from dictionary: {e}")

    @classmethod
    def from_csv(cls, csv_path: Union[str, Path]):
        """
        Create a ReactionModel instance by reading a CSV file.

        Parameters
        ----------
        csv_path : str or Path
            Path to the CSV file.

        Returns
        -------
        ReactionModel
            An instance of ReactionModel.

        Raises
        ------
        ReactionModelError
            If the CSV file cannot be read, contains duplicates, or the data is invalid.
        """
        try:
            csv_path = Path(csv_path)
            if not csv_path.is_file():
                raise ReactionModelError(f"The CSV file '{csv_path}' does not exist.")

            df = pd.read_csv(csv_path, index_col=0, dtype=str)

            # Check for duplicate step names
            if df.index.duplicated().any():
                duplicates = df.index[df.index.duplicated()].unique().tolist()
                raise ReactionModelError(f"Duplicate step names found in CSV: {duplicates}")

            # Parse list-like columns
            for col in cls.LIST_COLUMNS:
                if col in df.columns:
                    df[col] = df[col].apply(cls._parse_list_cell)
                else:
                    # For 'vib_energies_ts', it might be missing if not applicable
                    if col in cls.REQUIRED_ACTIVATED_COLUMNS:
                        # If 'vib_energies_ts' is mandatory but missing, validation will catch it
                        pass
                    else:
                        # For non-mandatory list columns, assign empty lists if missing
                        df[col] = [[] for _ in range(len(df))]

            # Convert numerical columns to appropriate types
            numeric_columns = ['area_site', 'activ_eng', 'prox_factor', 'graph_multiplicity']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            return cls.from_df(df)
        except ReactionModelError:
            raise
        except Exception as e:
            raise ReactionModelError(f"Failed to create ReactionModel from CSV file: {e}")

    @classmethod
    def from_df(cls, df: pd.DataFrame):
        """
        Create a ReactionModel instance from a Pandas DataFrame.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame containing mechanism data.

        Returns
        -------
        ReactionModel
            An instance of ReactionModel.

        Raises
        ------
        ReactionModelError
            If the DataFrame contains duplicates or is invalid.
        """
        # Check for duplicate step names
        if df.index.duplicated().any():
            duplicates = df.index[df.index.duplicated()].unique().tolist()
            raise ReactionModelError(f"Duplicate step names found in DataFrame: {duplicates}")

        return cls(mechanism_data=df)

    @staticmethod
    def _parse_list_cell(cell: str) -> list:
        """
        Parse a cell expected to contain a list.

        If the cell is NaN or empty, returns an empty list.
        Otherwise, evaluates the string to a Python list.

        Parameters
        ----------
        cell : str
            The cell content as a string.

        Returns
        -------
        list
            The parsed list, or empty list if the cell is NaN or empty.

        Raises
        ------
        ReactionModelError
            If the cell cannot be parsed into a list.
        """
        if pd.isna(cell) or cell.strip() == '':
            return []
        try:
            return ast.literal_eval(cell)
        except (ValueError, SyntaxError) as e:
            raise ReactionModelError(f"Failed to parse list from cell: {cell}. Error: {e}")

    def _validate_dataframe(self, df: Optional[pd.DataFrame] = None):
        """
        Validate that the DataFrame contains the required columns and correct data types.

        Parameters
        ----------
        df : pandas.DataFrame, optional
            The DataFrame to validate. If None, uses `self.df`.

        Raises
        ------
        ReactionModelError
            If validation fails.
        """
        if df is None:
            df = self.df

        # Check for duplicate step names
        if df.index.duplicated().any():
            duplicates = df.index[df.index.duplicated()].unique().tolist()
            raise ReactionModelError(f"Duplicate step names found: {duplicates}")

        missing_columns = self.REQUIRED_COLUMNS - set(df.columns)
        if missing_columns:
            raise ReactionModelError(f"Missing required columns: {missing_columns}")

        # Validate data types for list columns
        for col in self.LIST_COLUMNS:
            if col in df.columns:
                if not df[col].apply(lambda x: isinstance(x, list)).all():
                    invalid_steps = df[~df[col].apply(lambda x: isinstance(x, list))].index.tolist()
                    raise ReactionModelError(f"Column '{col}' must contain lists. Invalid steps: {invalid_steps}")
            else:
                raise ReactionModelError(f"Missing required column: '{col}'")

        # Validate data types for numeric columns
        for col in ['area_site', 'activ_eng', 'prox_factor', 'graph_multiplicity']:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    invalid_steps = df[~df[col].apply(lambda x: isinstance(x, (int, float)))].index.tolist()
                    raise ReactionModelError(f"Column '{col}' must contain numeric values. Invalid steps: {invalid_steps}")

        # Validate 'site_types' column if present
        if 'site_types' in df.columns:
            if not df['site_types'].apply(lambda x: isinstance(x, str) or pd.isna(x)).all():
                invalid_steps = df[~df['site_types'].apply(lambda x: isinstance(x, str) or pd.isna(x))].index.tolist()
                raise ReactionModelError(
                    f"Column 'site_types' must contain string or NaN values. Invalid steps: {invalid_steps}")

        # Validate 'neighboring' column if present
        if 'neighboring' in df.columns:
            if not df['neighboring'].apply(lambda x: isinstance(x, str) or pd.isna(x)).all():
                invalid_steps = df[~df['neighboring'].apply(lambda x: isinstance(x, str) or pd.isna(x))].index.tolist()
                raise ReactionModelError("Column 'neighboring' must contain string values or NaN.")

        # Validate 'angles' column if present
        if 'angles' in df.columns:
            if not df['angles'].apply(lambda x: isinstance(x, str) or pd.isna(x)).all():
                invalid_steps = df[~df['angles'].apply(lambda x: isinstance(x, str) or pd.isna(x))].index.tolist()
                raise ReactionModelError("Column 'angles' must contain string values or NaN.")

        # Assign default values for optional columns if missing
        if 'graph_multiplicity' not in df.columns:
            df['graph_multiplicity'] = 1
        else:
            df['graph_multiplicity'] = df['graph_multiplicity'].fillna(1)

    def write_mechanism_input(self,
                              output_dir: Union[str, Path],
                              temperature: float,
                              gas_model: GasModel,
                              manual_scaling: dict = None,
                              stiffness_scalable_steps: list = None,
                              stiffness_scalable_symmetric_steps: list = None,
                              sig_figs_energies: int = 8,
                              sig_figs_pe: int = 8):
        """
        Write the `mechanism_input.dat` file.

        Parameters
        ----------
        output_dir : str or Path
            Directory path where the file will be written.
        temperature : float
            Temperature in Kelvin for pre-exponential calculations.
        gas_model : GasModel
            Instance of GasModel containing gas-phase molecule data.
        manual_scaling : dict, optional
            Dictionary for manual scaling factors per step. Default is `{}`.
        stiffness_scalable_steps : list, optional
            List of steps that are stiffness scalable. Default is `[]`.
        stiffness_scalable_symmetric_steps : list, optional
            List of steps that are stiffness scalable and symmetric. Default is `[]`.
        sig_figs_energies : int, optional
            Number of significant figures for activation energies. Default is `8`.
        sig_figs_pe : int, optional
            Number of significant figures for pre-exponential factors. Default is `8`.

        Raises
        ------
        ReactionModelError
            If there are inconsistencies in the data or during file writing.
        """
        # Handle default arguments
        if manual_scaling is None:
            manual_scaling = {}
        if stiffness_scalable_steps is None:
            stiffness_scalable_steps = []
        if stiffness_scalable_symmetric_steps is None:
            stiffness_scalable_symmetric_steps = []

        # Check for inconsistent stiffness scaling configuration
        if len(stiffness_scalable_steps) > 0 and len(stiffness_scalable_symmetric_steps) > 0:
            overlapping_steps = set(stiffness_scalable_steps).intersection(set(stiffness_scalable_symmetric_steps))
            if overlapping_steps:
                raise ReactionModelError(
                    f"Steps {overlapping_steps} cannot be in both 'stiffness_scalable_steps' and "
                    f"'stiffness_scalable_symmetric_steps'."
                )

        # Convert output_dir to Path object if it's a string
        output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir

        # Ensure the output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "mechanism_input.dat"
        write_header(output_file)
        try:
            with output_file.open('a') as infile:
                infile.write('mechanism\n\n')
                infile.write('############################################################################\n\n')
                for step in self.df.index:
                    initial_state = self.df.loc[step, 'initial']
                    final_state = self.df.loc[step, 'final']

                    if len(initial_state) != len(final_state):
                        raise ReactionModelError(
                            f"Error in '{step}': Number of sites in initial state ({len(initial_state)}) "
                            f"does not match final state ({len(final_state)})."
                        )

                    infile.write(f"reversible_step {step}\n\n")

                    molecule = self.df.loc[step].get('molecule', None)
                    if pd.notna(molecule):
                        infile.write(f"  gas_reacs_prods {molecule} -1\n")

                    infile.write(f"  sites {len(initial_state)}\n")

                    neighboring = self.df.loc[step].get('neighboring', None)
                    if pd.notna(neighboring):
                        infile.write(f"  neighboring {neighboring}\n")

                    infile.write("  initial\n")
                    for element in initial_state:
                        infile.write(f"    {' '.join(element.split())}\n")

                    infile.write("  final\n")
                    for element in final_state:
                        infile.write(f"    {' '.join(element.split())}\n")

                    site_types = self.df.loc[step].get('site_types', None)
                    if pd.notna(site_types):
                        infile.write(f"  site_types {site_types}\n")

                    # Obtain pe_fwd and pe_ratio from get_pre_expon
                    pe_fwd, pe_ratio = self.get_pre_expon(
                        step=step,
                        temperature=temperature,
                        gas_model=gas_model,
                        manual_scaling=manual_scaling
                    )

                    # Write pre_expon and pe_ratio
                    if step in manual_scaling:
                        infile.write(f"  pre_expon {pe_fwd:.{sig_figs_pe}e}   # scaled {manual_scaling[step]:.8e}\n")
                    else:
                        infile.write(f"  pre_expon {pe_fwd:.{sig_figs_pe}e}\n")

                    infile.write(f"  pe_ratio {pe_ratio:.{sig_figs_pe}e}\n")
                    activ_eng = self.df.loc[step, 'activ_eng']
                    infile.write(f"  activ_eng {activ_eng:.{sig_figs_energies}f}\n")

                    # Write optional keywords only if they are provided
                    for keyword in ['prox_factor', 'angles']:
                        value = self.df.loc[step].get(keyword, None)
                        if pd.notna(value):
                            infile.write(f"  {keyword} {value}\n")

                    if step in stiffness_scalable_steps:
                        infile.write(f"  stiffness_scalable \n")
                    if step in stiffness_scalable_symmetric_steps:
                        infile.write(f"  stiffness_scalable_symmetric \n")

                    infile.write("\nend_reversible_step\n\n")
                    infile.write('############################################################################\n\n')
                infile.write("end_mechanism\n")

        except IOError as e:
            raise ReactionModelError(f"Failed to write to '{output_file}': {e}")

    def get_step_type(self, step: str) -> str:
        """
        Determine the type of a given step based on its properties.

        Parameters
        ----------
        step : str
            The name of the reaction step.

        Returns
        -------
        str
            The type of the step:
            - 'non_activated_adsorption'
            - 'activated_adsorption'
            - 'surface_reaction'

        Raises
        ------
        ReactionModelError
            If the step type cannot be determined.
        """
        molecule = self.df.loc[step].get('molecule', None)
        if pd.isna(molecule) or molecule is None:
            return 'surface_reaction'
        vib_energies_ts = self.df.loc[step, 'vib_energies_ts']
        if not isinstance(vib_energies_ts, list):
            raise ReactionModelError(f"Invalid 'vib_energies_ts' for step {step}. Must be a list.")
        if len(vib_energies_ts) == 0:
            return 'non_activated_adsorption'
        else:
            return 'activated_adsorption'

    def get_pre_expon(self, step: str, temperature: float, gas_model: GasModel, manual_scaling: dict) -> tuple:
        """
        Calculate the forward pre-exponential and the pre-exponential ratio.

        These values are required for the `mechanism_input.dat` file.

        Parameters
        ----------
        step : str
            The name of the reaction step.
        temperature : float
            Temperature in Kelvin.
        gas_model : GasModel
            Instance of GasModel containing gas-phase molecule data.
        manual_scaling : dict
            Dictionary for manual scaling factors per step.

        Returns
        -------
        tuple
            A tuple containing `(pe_fwd, pe_ratio)`.

        Raises
        ------
        ReactionModelError
            If vibrational energies contain 0.0 or other calculation errors.
        """
        vib_energies_is = self.df.loc[step, 'vib_energies_is']
        vib_energies_ts = self.df.loc[step, 'vib_energies_ts']
        vib_energies_fs = self.df.loc[step, 'vib_energies_fs']

        # Check for zero vibrational energies
        for energy_list, label in zip(
                [vib_energies_is, vib_energies_ts, vib_energies_fs],
                ['initial state', 'transition state', 'final state']
        ):
            if any(e == 0.0 for e in energy_list):
                raise ReactionModelError(f"Vibrational energy of 0.0 found in {label} of step {step}.")

        step_type = self.get_step_type(step)

        if 'adsorption' in step_type:
            molecule = self.df.loc[step, 'molecule']
            try:
                molec_data = gas_model.df.loc[molecule]
                molec_mass = molec_data['gas_molec_weight']
                inertia_moments = molec_data['inertia_moments']
                sym_number = molec_data['sym_number']
                degeneracy = molec_data['degeneracy']
                if step_type == 'non_activated_adsorption':
                    vib_energies_ts = []
                pe_fwd, pe_rev = calc_ads(
                    area_site=self.df.loc[step, 'area_site'],
                    molec_mass=molec_mass,
                    temperature=temperature,
                    vib_energies_is=vib_energies_is,
                    vib_energies_ts=vib_energies_ts,
                    vib_energies_fs=vib_energies_fs,
                    inertia_moments=inertia_moments,
                    sym_number=int(sym_number),
                    degeneracy=degeneracy
                )
            except KeyError as e:
                raise ReactionModelError(f"Missing gas data for molecule '{molecule}': {e}")
        else:  # surface reaction
            pe_fwd, pe_rev = calc_surf_proc(
                temperature=temperature,
                vib_energies_is=vib_energies_is,
                vib_energies_ts=vib_energies_ts,
                vib_energies_fs=vib_energies_fs
            )

        # Apply manual scaling if applicable
        if step in manual_scaling:
            pe_fwd *= manual_scaling[step]
            pe_rev *= manual_scaling[step]

        # Apply graph multiplicity if applicable
        graph_multiplicity = self.df.loc[step].get('graph_multiplicity', 1)
        if graph_multiplicity is not None and not pd.isna(graph_multiplicity):
            pe_fwd /= float(graph_multiplicity)
            pe_rev /= float(graph_multiplicity)

        if pe_rev == 0:
            raise ReactionModelError(f"Pre-exponential ratio division by zero for step {step}.")
        pe_ratio = pe_fwd / pe_rev

        return pe_fwd, pe_ratio

    def add_step(self, step_info: dict = None, step_series: pd.Series = None):
        """
        Add a new reaction step to the model.

        Parameters
        ----------
        step_info : dict, optional
            Dictionary containing step properties. Must include a key `'step_name'` to specify the step's name.
        step_series : pandas.Series, optional
            Pandas Series containing step properties. Must include `'step_name'` as part of the Series data.

        Raises
        ------
        ReactionModelError
            If neither `step_info` nor `step_series` is provided, or if required fields are missing,
            or if the step already exists.
        """
        if step_info is not None and step_series is not None:
            raise ReactionModelError("Provide either 'step_info' or 'step_series', not both.")

        if step_info is None and step_series is None:
            raise ReactionModelError("Either 'step_info' or 'step_series' must be provided.")

        if step_info is not None:
            if 'step_name' not in step_info:
                raise ReactionModelError("Missing 'step_name' in step_info dictionary.")
            step_name = step_info.pop('step_name')
            new_data = step_info
        else:
            if 'step_name' not in step_series:
                raise ReactionModelError("Missing 'step_name' in step_series.")
            step_name = step_series.pop('step_name')
            new_data = step_series.to_dict()

        # Parse 'initial', 'final', and vibrational energies using _parse_list_cell
        for list_col in ['initial', 'final', 'vib_energies_is', 'vib_energies_fs', 'vib_energies_ts']:
            if list_col in new_data:
                new_data[list_col] = self._parse_list_cell(new_data[list_col])
            else:
                if list_col in self.REQUIRED_COLUMNS:
                    raise ReactionModelError(f"Missing required column '{list_col}' in new step '{step_name}'.")
                else:
                    new_data[list_col] = []

        # Convert 'graph_multiplicity' to numeric if present
        if 'graph_multiplicity' in new_data:
            try:
                if pd.isna(new_data['graph_multiplicity']) or new_data['graph_multiplicity'] == '':
                    new_data['graph_multiplicity'] = 1
                else:
                    new_data['graph_multiplicity'] = float(new_data['graph_multiplicity'])
            except ValueError:
                raise ReactionModelError(f"'graph_multiplicity' for step '{step_name}' must be numeric.")
        else:
            new_data['graph_multiplicity'] = 1

        # Assign default values for optional columns if missing or NaN (excluding 'prox_factor')
        for optional_col in self.OPTIONAL_COLUMNS - {'prox_factor'}:
            if optional_col not in new_data or pd.isna(new_data[optional_col]):
                new_data[optional_col] = None

        # Ensure 'prox_factor' is handled correctly
        if 'prox_factor' not in new_data or pd.isna(new_data['prox_factor']):
            new_data['prox_factor'] = None

        new_row = pd.Series(new_data, name=step_name)

        # Validate required columns
        missing_columns = self.REQUIRED_COLUMNS - set(new_row.index)
        if missing_columns:
            raise ReactionModelError(f"Missing required columns in the new step: {missing_columns}")

        # Additional validation for adsorption steps
        if pd.notna(new_row.get('molecule', pd.NA)):
            missing_ads_columns = self.REQUIRED_ADS_COLUMNS - set(new_row.index)
            if missing_ads_columns:
                raise ReactionModelError(f"Missing required adsorption columns in the new step: {missing_ads_columns}")

        # Additional validation for activated steps
        vib_energies_ts = new_row.get('vib_energies_ts', [])
        if isinstance(vib_energies_ts, list) and len(vib_energies_ts) > 0:
            missing_activated_columns = self.REQUIRED_ACTIVATED_COLUMNS - set(new_row.index)
            if missing_activated_columns:
                raise ReactionModelError(f"Missing required columns for activated step: {missing_activated_columns}")
        elif not isinstance(vib_energies_ts, list):
            raise ReactionModelError(f"'vib_energies_ts' must be a list for step '{step_name}'.")

        # Check for duplicate step name
        if step_name in self.df.index:
            raise ReactionModelError(f"Step '{step_name}' already exists in the model.")

        temp_df = pd.concat([self.df, new_row.to_frame().T], ignore_index=False)

        # Validate the temporary DataFrame
        try:
            self._validate_dataframe(temp_df)
        except ReactionModelError as e:
            raise ReactionModelError(f"Invalid data for new step '{step_name}': {e}")

        self.df = temp_df

    def remove_steps(self, step_names: list):
        """
        Remove existing reaction steps from the model.

        Parameters
        ----------
        step_names : list
            List of step names to be removed.

        Raises
        ------
        ReactionModelError
            If any of the step names do not exist in the model.
        """
        missing_steps = [name for name in step_names if name not in self.df.index]
        if missing_steps:
            raise ReactionModelError(f"The following steps do not exist and cannot be removed: {missing_steps}")

        self.df = self.df.drop(step_names)
