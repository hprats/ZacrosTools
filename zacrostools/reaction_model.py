import ast
import warnings
from pathlib import Path
from typing import Union, Optional
import pandas as pd
from zacrostools.header import write_header
from zacrostools.custom_exceptions import ReactionModelError, enforce_types
from zacrostools.gas_model import GasModel
from zacrostools.calc_functions import pe_surface, pe_activated_ads, pe_nonactivated_ads, pe_nonactivated_desorption



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

        **Mandatory when any gas species participates (adsorption/desorption/exchange)**:
        - **area_site** (float): Area of the adsorption site (Å²). Required whenever gas species are involved.

        **Mandatory for steps involving gas-phase species in the initial state**:
        - **molecule_is** (str, optional): Gas species present in the initial state (e.g. adsorption).

        **Mandatory for steps involving gas-phase species in the final state**:
        - **molecule_fs** (str, optional): Gas species present in the final state (e.g. desorption).

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
        - **fixed_pre_expon** (float): Optional fixed **forward** pre-exponential factor to write as-is (no scaling / no graph multiplicity applied).
          Units must match Zacros expectations: surface/non-activated desorption in `s^-1`; adsorption (activated/non-activated) in `bar^-1·s^-1`.
        - **fixed_pe_ratio** (float): Optional fixed pre-exponential ratio `pe_fwd/pe_rev` to write as-is.
          Must be provided **together** with `fixed_pre_expon`.

        **Backward compatibility (deprecated)**:
        - **molecule** (str, optional): Deprecated. If present, it is treated as `molecule_is`
          and triggers a DeprecationWarning.

    """

    REQUIRED_COLUMNS = {
        'initial',
        'final',
        'activ_eng',
        'vib_energies_is',
        'vib_energies_fs'
    }
    REQUIRED_ADS_COLUMNS = {'area_site'}
    REQUIRED_ACTIVATED_COLUMNS = {'vib_energies_ts'}
    OPTIONAL_COLUMNS = {
        'site_types', 'neighboring', 'prox_factor', 'angles', 'graph_multiplicity',
        'molecule_is', 'molecule_fs', 'molecule',  # legacy 'molecule'
        'fixed_pre_expon', 'fixed_pe_ratio'
    }
    LIST_COLUMNS = ['initial', 'final', 'vib_energies_is', 'vib_energies_fs', 'vib_energies_ts']

    @enforce_types
    def __init__(self, mechanism_data: pd.DataFrame = None):
        if mechanism_data is None:
            raise ReactionModelError("mechanism_data must be provided as a Pandas DataFrame.")
        self.df = mechanism_data.copy()
        self._normalize_gas_columns()  # handle deprecated 'molecule' and ensure new columns exist
        self._validate_dataframe()

    @classmethod
    def from_dict(cls, steps_dict: dict):
        """Create a ReactionModel instance from a dictionary."""
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
        """Create a ReactionModel instance by reading a CSV file."""
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
                    # If TS vib energies are mandatory in a given context, validation will catch it later
                    df[col] = [[] for _ in range(len(df))]

            # Convert numerical columns to appropriate types
            numeric_columns = ['area_site', 'activ_eng', 'prox_factor', 'graph_multiplicity',
                               'fixed_pre_expon', 'fixed_pe_ratio']
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
        """Create a ReactionModel instance from a Pandas DataFrame."""
        # Check for duplicate step names
        if df.index.duplicated().any():
            duplicates = df.index[df.index.duplicated()].unique().tolist()
            raise ReactionModelError(f"Duplicate step names found in DataFrame: {duplicates}")

        return cls(mechanism_data=df)


    def add_step(self, step_info: dict) -> None:
        """
        Add a new step to the reaction model.

        Parameters
        ----------
        step_info : dict
            Dictionary describing the step. Must include 'step_name' and the tags
            for the step (e.g., 'initial', 'final', 'activ_eng', vib lists, etc.).
            Example:
                {
                    'step_name': 'new_step',
                    'activ_eng': 2.0,
                    'final': ['1 * 1'],
                    'initial': ['1 CO* 1'],
                    'vib_energies_is': [150, 200],
                    'vib_energies_fs': [100, 150],
                    'vib_energies_ts': [125],
                    'site_types': 'tC'
                }
        """
        if not isinstance(step_info, dict):
            raise ReactionModelError("add_step expects a dict 'step_info'.")

        step_name = step_info.get('step_name', None)
        if not step_name or not isinstance(step_name, str):
            raise ReactionModelError("The new step must include a valid 'step_name' string.")

        if step_name in self.df.index:
            raise ReactionModelError(f"A step named '{step_name}' already exists.")

        # Only allow known columns
        allowed = set(self.REQUIRED_COLUMNS) | set(self.OPTIONAL_COLUMNS) | set(self.LIST_COLUMNS)
        provided_keys = set(step_info.keys()) - {'step_name'}
        unknown = provided_keys - allowed
        if unknown:
            raise ReactionModelError(
                f"Unknown keys in 'step_info' for step '{step_name}': {sorted(unknown)}.\n"
                f"Allowed: {sorted(allowed)}"
            )

        # Ensure the dataframe has all allowed columns so we can assign safely
        for col in allowed:
            if col not in self.df.columns:
                if col in self.LIST_COLUMNS:
                    self.df[col] = [[] for _ in range(len(self.df))]
                elif col == 'graph_multiplicity':
                    self.df[col] = 1
                else:
                    self.df[col] = pd.NA

        # Build a complete row respecting defaults
        row_data = {}
        for col in self.df.columns:
            if col in self.LIST_COLUMNS:
                val = step_info.get(col, [])
                if not isinstance(val, list):
                    raise ReactionModelError(
                        f"Column '{col}' must be a list for step '{step_name}'. Got: {type(val)}"
                    )
                row_data[col] = val
            elif col == 'graph_multiplicity':
                row_data[col] = step_info.get(col, self.df[col].dtype.type(1) if hasattr(self.df[col].dtype, 'type') else 1)
            else:
                row_data[col] = step_info.get(col, pd.NA)

        # Minimal presence checks before full validation
        for must in ('initial', 'final', 'activ_eng', 'vib_energies_is', 'vib_energies_fs'):
            if must not in step_info:
                raise ReactionModelError(f"Missing required key '{must}' in step '{step_name}'.")

        # If either fixed_* provided, both must be provided
        fpe = row_data.get('fixed_pre_expon', pd.NA)
        fpr = row_data.get('fixed_pe_ratio', pd.NA)
        if (pd.notna(fpe) and pd.isna(fpr)) or (pd.notna(fpr) and pd.isna(fpe)):
            raise ReactionModelError(
                f"Step '{step_name}': both 'fixed_pre_expon' and 'fixed_pe_ratio' must be provided together."
            )

        self.df.loc[step_name] = row_data
        self._normalize_gas_columns()

        # Coerce numeric columns if present
        for col in ['area_site', 'activ_eng', 'prox_factor', 'graph_multiplicity']:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

        # Ensure vib_energies_ts always a list (empty allowed)
        if 'vib_energies_ts' in self.df.columns:
            self.df['vib_energies_ts'] = self.df['vib_energies_ts'].apply(
                lambda v: v if isinstance(v, list) else ([] if pd.isna(v) else v)
            )

        # Validate entire table (catches missing area_site when gas present, etc.)
        self._validate_dataframe()


    def remove_steps(self, steps_to_remove: list[str]) -> None:
        """
        Remove existing steps from the model.

        Parameters
        ----------
        steps_to_remove : list of str
            Names (index) of steps to remove.
        """
        if not isinstance(steps_to_remove, (list, tuple)) or not steps_to_remove:
            raise ReactionModelError("remove_steps expects a non-empty list of step names.")

        missing = [s for s in steps_to_remove if s not in self.df.index]
        if missing:
            raise ReactionModelError(f"Steps not found and cannot be removed: {missing}")

        self.df = self.df.drop(index=list(steps_to_remove))


    @staticmethod
    def _parse_list_cell(cell: str) -> list:
        """
        Parse a cell expected to contain a list.If the cell is NaN or empty, returns an empty list.
        Otherwise, evaluates the string to a Python list.
        """
        if pd.isna(cell) or cell.strip() == '':
            return []
        try:
            return ast.literal_eval(cell)
        except (ValueError, SyntaxError) as e:
            raise ReactionModelError(f"Failed to parse list from cell: {cell}. Error: {e}")

    def _normalize_gas_columns(self):
        """
        Ensure 'molecule_is' and 'molecule_fs' exist.
        If deprecated 'molecule' exists and 'molecule_is' is empty for a row,
        migrate its value to 'molecule_is' and emit a DeprecationWarning.
        """
        # Ensure columns exist
        for col in ('molecule_is', 'molecule_fs'):
            if col not in self.df.columns:
                self.df[col] = pd.NA

        if 'molecule' in self.df.columns:
            # Migrate row-wise where appropriate
            for idx, row in self.df.iterrows():
                mol = row.get('molecule', pd.NA)
                mol_is = row.get('molecule_is', pd.NA)
                if pd.notna(mol) and (pd.isna(mol_is) or mol_is in (None, '')):
                    # Move deprecated 'molecule' -> 'molecule_is'
                    self.df.at[idx, 'molecule_is'] = mol
                    warnings.warn(
                        f"[ReactionModel] Step '{idx}': 'molecule' is deprecated; "
                        f"treating it as 'molecule_is'. Please update your inputs.",
                        DeprecationWarning,
                        stacklevel=2,
                    )
            # Keep the deprecated column, but do not rely on it anywhere else

    def _validate_dataframe(self, df: Optional[pd.DataFrame] = None):
        """Validate that the DataFrame contains the required columns and correct data types."""
        if df is None:
            df = self.df

        # Check for duplicate step names
        if df.index.duplicated().any():
            duplicates = df.index[df.index.duplicated()].unique().tolist()
            raise ReactionModelError(f"Duplicate step names found: {duplicates}")

        missing_columns = self.REQUIRED_COLUMNS - set(df.columns)
        if missing_columns:
            raise ReactionModelError(f"Missing required columns: {missing_columns}")

        # Ensure vib_energies_ts always exists as a list
        if 'vib_energies_ts' not in df.columns:
            df['vib_energies_ts'] = [[] for _ in range(len(df))]
        else:
            df['vib_energies_ts'] = df['vib_energies_ts'].apply(
                lambda v: v if isinstance(v, list) else ([] if pd.isna(v) else v)
            )

        # Validate data types for list columns
        for col in self.LIST_COLUMNS:
            if col in df.columns:
                if not df[col].apply(lambda x: isinstance(x, list)).all():
                    invalid_steps = df[~df[col].apply(lambda x: isinstance(x, list))].index.tolist()
                    raise ReactionModelError(f"Column '{col}' must contain lists. Invalid steps: {invalid_steps}")
            else:
                raise ReactionModelError(f"Missing required column: '{col}'")

        # Validate numeric columns (if present)
        for col in ['area_site', 'activ_eng', 'prox_factor', 'graph_multiplicity',
                    'fixed_pre_expon', 'fixed_pe_ratio']:
            if col in df.columns:
                non_num = df[col].apply(lambda x: not (pd.isna(x) or isinstance(x, (int, float))))
                if non_num.any():
                    invalid_steps = df[non_num].index.tolist()
                    raise ReactionModelError(
                        f"Column '{col}' must contain numeric values or NaN. Invalid: {invalid_steps}")

        # Validate 'site_types', 'neighboring', 'angles' if present
        for col in ['site_types', 'neighboring', 'angles', 'molecule_is', 'molecule_fs', 'molecule']:
            if col in df.columns:
                ok = df[col].apply(lambda x: isinstance(x, str) or pd.isna(x))
                if not ok.all():
                    invalid_steps = df[~ok].index.tolist()
                    raise ReactionModelError(f"Column '{col}' must contain string values or NaN. Invalid: {invalid_steps}")

        # Assign default values for optional columns if missing
        if 'graph_multiplicity' not in df.columns:
            df['graph_multiplicity'] = 1
        else:
            df['graph_multiplicity'] = df['graph_multiplicity'].fillna(1)

        # Whenever any gas species participates, area_site must be provided
        if 'area_site' in df.columns:
            needs_area = df.apply(
                lambda r: pd.notna(r.get('molecule_is', pd.NA)) or pd.notna(r.get('molecule_fs', pd.NA)) or
                          pd.notna(r.get('molecule', pd.NA)),
                axis=1
            )
            missing_area = needs_area & df['area_site'].isna()
            if missing_area.any():
                bad = df[missing_area].index.tolist()
                raise ReactionModelError(
                    f"'area_site' is required when gas species participate. Missing for steps: {bad}")

        # Validate fixed_* pairing and positivity when set
        if 'fixed_pre_expon' in df.columns or 'fixed_pe_ratio' in df.columns:
            def _has(x): return pd.notna(x)
            bad_pair = []
            bad_sign = []
            for idx, r in df.iterrows():
                fpe = r.get('fixed_pre_expon', pd.NA)
                fpr = r.get('fixed_pe_ratio', pd.NA)
                if _has(fpe) ^ _has(fpr):
                    bad_pair.append(idx)
                elif _has(fpe) and _has(fpr):
                    try:
                        if float(fpe) <= 0.0 or float(fpr) <= 0.0:
                            bad_sign.append(idx)
                    except Exception:
                        bad_sign.append(idx)
            if bad_pair:
                raise ReactionModelError(
                    f"For steps {bad_pair}, 'fixed_pre_expon' and 'fixed_pe_ratio' must be provided together.")
            if bad_sign:
                raise ReactionModelError(
                    f"For steps {bad_sign}, 'fixed_pre_expon' and 'fixed_pe_ratio' must be positive numbers.")

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
        """

        # Handle default arguments
        if manual_scaling is None:
            manual_scaling = {}
        if stiffness_scalable_steps is None:
            stiffness_scalable_steps = []
        if stiffness_scalable_symmetric_steps is None:
            stiffness_scalable_symmetric_steps = []

        # Determine which steps are fixed (have both columns set)
        def _is_fixed_row(r):
            return pd.notna(r.get('fixed_pre_expon', pd.NA)) and pd.notna(r.get('fixed_pe_ratio', pd.NA))

        fixed_steps = set([idx for idx, r in self.df.iterrows() if _is_fixed_row(r)])

        # Enforce incompatibilities with stiffness-scalable options
        if fixed_steps and stiffness_scalable_steps == 'all':
            raise ReactionModelError(
                "Using per-step fixed_pre_expon/fixed_pe_ratio is incompatible with stiffness_scalable_steps='all'."
            )

        if fixed_steps and isinstance(stiffness_scalable_steps, (list, tuple, set)):
            overlap = fixed_steps.intersection(set(stiffness_scalable_steps))
            if overlap:
                raise ReactionModelError(
                    f"Steps {sorted(overlap)} are fixed and cannot be in stiffness_scalable_steps."
                )

        if fixed_steps and isinstance(stiffness_scalable_symmetric_steps, (list, tuple, set)):
            overlap = fixed_steps.intersection(set(stiffness_scalable_symmetric_steps))
            if overlap:
                raise ReactionModelError(
                    f"Steps {sorted(overlap)} are fixed and cannot be in stiffness_scalable_symmetric_steps."
                )

        # Check for inconsistent stiffness scaling configuration
        if isinstance(stiffness_scalable_steps, (list, tuple, set)) and \
                isinstance(stiffness_scalable_symmetric_steps, (list, tuple, set)):
            overlapping_steps = set(stiffness_scalable_steps).intersection(set(stiffness_scalable_symmetric_steps))
            if overlapping_steps:
                raise ReactionModelError(
                    f"Steps {sorted(overlapping_steps)} cannot be in both 'stiffness_scalable_steps' and "
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
                    row = self.df.loc[step]
                    initial_state = row['initial']
                    final_state = row['final']

                    if len(initial_state) != len(final_state):
                        raise ReactionModelError(
                            f"Error in '{step}': Number of sites in initial state ({len(initial_state)}) "
                            f"does not match final state ({len(final_state)})."
                        )

                    infile.write(f"reversible_step {step}\n\n")

                    # gas_reacs_prods assembly
                    mol_is = row.get('molecule_is', pd.NA)
                    mol_fs = row.get('molecule_fs', pd.NA)
                    # Also consider deprecated 'molecule' for legacy CSVs where normalize ensured molecule_is
                    if pd.notna(row.get('molecule', pd.NA)) and pd.isna(mol_is):
                        mol_is = row.get('molecule')

                    if pd.notna(mol_is) or pd.notna(mol_fs):
                        line = "  gas_reacs_prods"
                        if pd.notna(mol_is):
                            line += f" {str(mol_is).strip()} -1"
                        if pd.notna(mol_fs):
                            line += f" {str(mol_fs).strip()} 1"
                        infile.write(line + "\n")

                    infile.write(f"  sites {len(initial_state)}\n")

                    neighboring = row.get('neighboring', None)
                    if pd.notna(neighboring):
                        infile.write(f"  neighboring {neighboring}\n")

                    infile.write("  initial\n")
                    for element in initial_state:
                        infile.write(f"    {' '.join(element.split())}\n")

                    infile.write("  final\n")
                    for element in final_state:
                        infile.write(f"    {' '.join(element.split())}\n")

                    site_types = row.get('site_types', None)
                    if pd.notna(site_types):
                        infile.write(f"  site_types {site_types}\n")

                    # Use fixed values if defined; otherwise compute
                    if step in fixed_steps:
                        pe_fwd = float(row['fixed_pre_expon'])
                        pe_ratio = float(row['fixed_pe_ratio'])
                        # NOTE: For fixed values we do NOT apply manual scaling nor graph multiplicity;
                        # they are treated as final values to be written as-is.
                        infile.write(f"  pre_expon {pe_fwd:.{sig_figs_pe}e}   # fixed\n")
                    else:
                        pe_fwd, pe_ratio = self.get_pre_expon(
                            step=step,
                            temperature=temperature,
                            gas_model=gas_model,
                            manual_scaling=manual_scaling
                        )
                        if step in manual_scaling:
                            infile.write(
                                f"  pre_expon {pe_fwd:.{sig_figs_pe}e}   # scaled {manual_scaling[step]:.8e}\n")
                        else:
                            infile.write(f"  pre_expon {pe_fwd:.{sig_figs_pe}e}\n")

                    activ_eng = float(row['activ_eng'])
                    infile.write(f"  pe_ratio {pe_ratio:.{sig_figs_pe}e}\n")
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


    def get_pre_expon(self, step: str, temperature: float, gas_model: GasModel, manual_scaling: dict) -> tuple:
        """
        Calculate the forward pre-exponential and the pre-exponential ratio (pe_fwd / pe_rev).
        Forward RS is IS; reverse RS is FS. Each direction may be surface or adsorption
        (activated/non-activated) and is treated independently.
        """
        # Compute raw (unscaled) pe_fwd and pe_rev
        pe_fwd = self._pe_for_direction(step=step, direction="fwd", T=temperature, gas_model=gas_model)
        pe_rev = self._pe_for_direction(step=step, direction="rev", T=temperature, gas_model=gas_model)

        # ---- Convert adsorption pre-exponentials from Pa^-1·s^-1 to bar^-1·s^-1 (Zacros uses bar) ----
        # Identify process type per direction
        proc_fwd = self._get_process_type(step, "fwd")
        proc_rev = self._get_process_type(step, "rev")

        PA_TO_BAR_FACTOR = 1.0e5  # multiply Pa^-1·s^-1 by 1e5 to get bar^-1·s^-1

        if proc_fwd in ("activated_adsorption", "non_activated_adsorption"):
            pe_fwd *= PA_TO_BAR_FACTOR
        if proc_rev in ("activated_adsorption", "non_activated_adsorption"):
            pe_rev *= PA_TO_BAR_FACTOR
        # -----------------------------------------------------------------------------------------------

        # Apply manual scaling if applicable (both directions)
        if step in manual_scaling:
            scale = float(manual_scaling[step])
            pe_fwd *= scale
            pe_rev *= scale

        # Apply graph multiplicity if applicable (divide both)
        graph_multiplicity = self.df.loc[step].get('graph_multiplicity', 1)
        if graph_multiplicity is not None and not pd.isna(graph_multiplicity):
            gm = float(graph_multiplicity)
            if gm != 0.0:
                pe_fwd /= gm
                pe_rev /= gm

        if pe_rev == 0.0:
            raise ReactionModelError(f"Computed pe_rev == 0 for step '{step}', cannot compute pe_ratio.")
        pe_ratio = pe_fwd / pe_rev

        return pe_fwd, pe_ratio


    def _pe_for_direction(self, step: str, direction: str, T: float, gas_model: GasModel) -> float:
        """
        Compute pe for one direction ('fwd' or 'rev') using step-level activation logic.
        """
        row = self.df.loc[step]
        proc_type = self._get_process_type(step, direction)

        # Pick RS (reactant-side) vibrational list according to direction
        vib_RS_meV = row['vib_energies_is'] if direction == "fwd" else row['vib_energies_fs']
        vib_TS_meV = row.get('vib_energies_ts', [])

        if proc_type == "surface_process":
            # Activated step with no gas in RS -> surface process requires TS vibes
            if not isinstance(vib_TS_meV, list) or len(vib_TS_meV) == 0:
                raise ReactionModelError(
                    f"vib_energies_ts must be provided for surface processes (step {step}, dir={direction})."
                )
            return pe_surface(vib_TS_meV=vib_TS_meV, vib_RS_meV=vib_RS_meV or [], T=T)

        if proc_type == "activated_adsorption":
            # Activated adsorption: need area + RS gas molecule + TS vibes
            if 'area_site' not in self.df.columns or pd.isna(row.get('area_site', pd.NA)):
                raise ReactionModelError(
                    f"'area_site' is required for activated adsorption (step='{step}', direction='{direction}')."
                )
            rs_molecule = self._get_rs_molecule(step, direction)
            if rs_molecule is None:
                raise ReactionModelError(
                    f"Activated adsorption detected but RS molecule not found (step='{step}', dir='{direction}')."
                )
            try:
                molec_data = gas_model.df.loc[rs_molecule]
            except KeyError:
                raise ReactionModelError(f"Gas species '{rs_molecule}' (step='{step}') not found in GasModel.")
            if not isinstance(vib_TS_meV, list) or len(vib_TS_meV) == 0:
                raise ReactionModelError("vib_energies_ts must be provided for activated adsorption.")
            return pe_activated_ads(
                A_ang2=row['area_site'],
                molec_data=molec_data,
                vib_TS_meV=vib_TS_meV,
                vib_RS_meV=vib_RS_meV or [],
                T=T
            )

        if proc_type == "non_activated_adsorption":
            # Non-activated adsorption: need area + RS gas molecule
            if 'area_site' not in self.df.columns or pd.isna(row.get('area_site', pd.NA)):
                raise ReactionModelError(
                    f"'area_site' is required for non-activated adsorption (step='{step}', direction='{direction}')."
                )
            rs_molecule = self._get_rs_molecule(step, direction)
            if rs_molecule is None:
                raise ReactionModelError(
                    f"Non-activated adsorption detected but RS molecule not found (step='{step}', dir='{direction}')."
                )
            try:
                molec_data = gas_model.df.loc[rs_molecule]
            except KeyError:
                raise ReactionModelError(f"Gas species '{rs_molecule}' (step='{step}') not found in GasModel.")
            return pe_nonactivated_ads(
                A_ang2=row['area_site'],
                mass_amu=molec_data['gas_molec_weight'],
                T=T
            )

        # non_activated_desorption:
        # RS has no gas, PS has a gas molecule; need area + PS gas molecule and PS partition
        if 'area_site' not in self.df.columns or pd.isna(row.get('area_site', pd.NA)):
            raise ReactionModelError(
                f"'area_site' is required for non-activated desorption (step='{step}', direction='{direction}')."
            )
        ps_molecule = self._get_ps_molecule(step, direction)
        if ps_molecule is None:
            raise ReactionModelError(
                f"Non-activated desorption detected but PS molecule not found (step='{step}', dir='{direction}')."
            )
        try:
            molec_data_ps = gas_model.df.loc[ps_molecule]
        except KeyError:
            raise ReactionModelError(f"Gas species '{ps_molecule}' (step='{step}') not found in GasModel.")

        # vib_PS_meV: use the vib list of the product state for this direction
        vib_PS_meV = row['vib_energies_fs'] if direction == "fwd" else row['vib_energies_is']

        return pe_nonactivated_desorption(
            A_ang2=row['area_site'],
            molec_data=molec_data_ps,
            vib_PS_meV=vib_PS_meV or [],
            vib_RS_meV_surface=vib_RS_meV or [],
            T=T
        )

    def _get_rs_molecule(self, step: str, direction: str):
        """
        Return the gas molecule name for the Reactant State (RS) of the given direction,
        or None if there is no gas-phase molecule in the RS.
        Forward RS uses 'molecule_is', reverse RS uses 'molecule_fs'.
        """
        row = self.df.loc[step]
        if direction == "fwd":
            mol = row.get("molecule_is", pd.NA)
            if pd.isna(mol) and pd.notna(row.get("molecule", pd.NA)):  # legacy fallback
                mol = row.get("molecule")
        else:
            mol = row.get("molecule_fs", pd.NA)
        return None if (pd.isna(mol) or mol in ("", None)) else str(mol).strip()


    def _get_ps_molecule(self, step: str, direction: str):
        """
        Return the gas molecule name for the Product State (PS) of the given direction,
        or None if there is no gas-phase molecule in the PS.
        Forward PS uses 'molecule_fs'; reverse PS uses 'molecule_is' (legacy fallback 'molecule').
        """
        row = self.df.loc[step]
        if direction == "fwd":
            mol = row.get("molecule_fs", pd.NA)
        else:
            mol = row.get("molecule_is", pd.NA)
            if pd.isna(mol) and pd.notna(row.get("molecule", pd.NA)):  # legacy fallback
                mol = row.get("molecule")
        return None if (pd.isna(mol) or mol in ("", None)) else str(mol).strip()


    def _get_process_type(self, step: str, direction: str) -> str:
        """
        Step-level activation first:
          - If step is 'activated' (vib_energies_ts non-empty):
              if RS has gas  -> 'activated_adsorption'
              else           -> 'surface_process'
          - If step is 'non-activated' (vib_energies_ts empty):
              if RS has gas  -> 'non_activated_adsorption'
              else           -> 'non_activated_desorption'
        """
        row = self.df.loc[step]
        vib_ts = row.get("vib_energies_ts", [])
        step_is_activated = isinstance(vib_ts, list) and len(vib_ts) > 0

        rs_mol = self._get_rs_molecule(step, direction)

        if step_is_activated:
            return "activated_adsorption" if rs_mol is not None else "surface_process"
        else:
            return "non_activated_adsorption" if rs_mol is not None else "non_activated_desorption"
