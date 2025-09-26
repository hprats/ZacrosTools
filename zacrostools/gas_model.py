import ast
from pathlib import Path
from typing import Union
import pandas as pd
from zacrostools.custom_exceptions import GasModelError, enforce_types


def _to_list_or_empty(value):
    """Return a list, or [] when the incoming value is missing/empty."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        s = value.strip()
        if s == "":
            return []
        # try to parse a list written as a string (CSV case)
        try:
            parsed = ast.literal_eval(s)
            if isinstance(parsed, (list, tuple)):
                return list(parsed)
            # Anything else: treat as a single item list? For safety, empty:
            return []
        except Exception:
            return []
    # Anything else (number, bool, etc.): treat as empty
    return []


class GasModel:
    """
    Represents gas-phase molecular data for KMC reaction modeling.

    Parameters
    ----------
    gas_data : pandas.DataFrame
        Information on gas-phase molecules. The molecule name is taken as the index of each row.

        **Required columns (always):**
        - **type** (str): one of {'monoatomic', 'linear', 'non_linear'}.
        - **gas_energy** (float): Formation energy (eV). ZPE excluded.
        - **gas_molec_weight** (float): Molecular weight (amu).

        **Conditionally required (by type):**
        - **sym_number** (int):
            - Required for 'linear' and 'non_linear' (must be positive integer).
            - Must be undefined/None for 'monoatomic'.
        - **inertia_moments** (list of float, amu·Å²):
            - Required for 'linear' (exactly 1 value).
            - Required for 'non_linear' (exactly 3 values).
            - Must be undefined or empty for 'monoatomic'.

        **Optional columns:**
        - **degeneracy** (int): electronic ground-state degeneracy. Default: 1.

        Notes
        -----
        If the model contains only 'monoatomic' species, the columns 'sym_number' and
        'inertia_moments' can be absent in the CSV entirely.
    """

    # Always-required columns
    REQUIRED_COLUMNS = {'type', 'gas_energy', 'gas_molec_weight'}

    # Optional-at-schema-level (conditionally required per type)
    OPTIONAL_COLUMNS = {'degeneracy', 'sym_number', 'inertia_moments'}

    @enforce_types
    def __init__(self, gas_data: pd.DataFrame = None):
        if gas_data is None:
            raise GasModelError("gas_data must be provided as a Pandas DataFrame.")
        self.df = gas_data.copy()
        self._validate_dataframe()

    @classmethod
    def from_dict(cls, species_dict: dict):
        """Create a GasModel instance from a dictionary."""
        try:
            df = pd.DataFrame.from_dict(species_dict, orient='index')

            if df.index.duplicated().any():
                duplicates = df.index[df.index.duplicated()].unique().tolist()
                raise GasModelError(f"Duplicate molecule names found in dictionary: {duplicates}")

            return cls.from_df(df)
        except GasModelError:
            raise
        except Exception as e:
            raise GasModelError(f"Failed to create GasModel from dictionary: {e}")

    @classmethod
    def from_csv(cls, csv_path: Union[str, Path]):
        """Create a GasModel instance by reading a CSV file."""
        try:
            csv_path = Path(csv_path)
            if not csv_path.is_file():
                raise GasModelError(f"The CSV file '{csv_path}' does not exist.")

            df = pd.read_csv(csv_path, index_col=0, dtype=str)

            if df.index.duplicated().any():
                duplicates = df.index[df.index.duplicated()].unique().tolist()
                raise GasModelError(f"Duplicate molecule names found in CSV: {duplicates}")

            # Coerce/parse if columns exist; leave absent columns absent (monoatomic-only CSVs)
            if 'inertia_moments' in df.columns:
                df['inertia_moments'] = df['inertia_moments'].apply(_to_list_or_empty)

            # Convert numeric columns where present
            for col in ['gas_molec_weight', 'sym_number', 'gas_energy', 'degeneracy']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            return cls.from_df(df)
        except GasModelError:
            raise
        except Exception as e:
            raise GasModelError(f"Failed to create GasModel from CSV file: {e}")

    @classmethod
    def from_df(cls, df: pd.DataFrame):
        """Create a GasModel instance from a Pandas DataFrame."""
        if df.index.duplicated().any():
            duplicates = df.index[df.index.duplicated()].unique().tolist()
            raise GasModelError(f"Duplicate molecule names found in DataFrame: {duplicates}")
        return cls(gas_data=df)

    def _validate_dataframe(self, df: pd.DataFrame | None = None):
        """Validate required columns and enforce simple, type-based rules."""
        if df is None:
            df = self.df

        # Duplicates
        if df.index.duplicated().any():
            duplicates = df.index[df.index.duplicated()].unique().tolist()
            raise GasModelError(f"Duplicate molecule names found: {duplicates}")

        # Required columns present?
        missing = self.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise GasModelError(f"Missing required columns: {sorted(missing)}")

        # Ensure optional columns exist (with permissive defaults)
        if 'degeneracy' not in df.columns:
            df['degeneracy'] = 1
        if 'sym_number' not in df.columns:
            df['sym_number'] = pd.NA
        if 'inertia_moments' not in df.columns:
            df['inertia_moments'] = [[] for _ in range(len(df))]

        # Normalize types
        valid_types = {'monoatomic', 'linear', 'non_linear'}
        if not df['type'].apply(lambda x: isinstance(x, str) and x in valid_types).all():
            bad = df[~df['type'].apply(lambda x: isinstance(x, str) and x in valid_types)].index.tolist()
            raise GasModelError(f"Column 'type' must be one of {sorted(valid_types)}. Invalid species: {bad}")

        # Numeric required columns
        for col in ['gas_molec_weight', 'gas_energy']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].isna().any():
                bad = df[df[col].isna()].index.tolist()
                raise GasModelError(f"Column '{col}' must contain numeric values. Invalid species: {bad}")

        # Degeneracy: int, default 1
        df['degeneracy'] = pd.to_numeric(df['degeneracy'], errors='coerce').fillna(1)
        if not df['degeneracy'].apply(lambda x: float(x).is_integer() and x >= 1).all():
            bad = df[~df['degeneracy'].apply(lambda x: float(x).is_integer() and x >= 1)].index.tolist()
            raise GasModelError(f"Column 'degeneracy' must be a positive integer. Invalid species: {bad}")
        df['degeneracy'] = df['degeneracy'].astype(int)

        # Sym number may be NA for monoatomic; coerce to numeric where present
        df['sym_number'] = pd.to_numeric(df['sym_number'], errors='coerce')

        # Coerce inertia_moments cells to lists (or empty)
        df['inertia_moments'] = df['inertia_moments'].apply(_to_list_or_empty)

        # Per-type validation
        errs = []

        for name, row in df.iterrows():
            t = row['type']
            sym = row['sym_number']
            inertia = row['inertia_moments']

            if t == 'monoatomic':
                # Must NOT define sym_number; must have empty inertia list
                if pd.notna(sym):
                    errs.append(f"'{name}': monoatomic species must not define 'sym_number'.")
                if len(inertia) != 0:
                    errs.append(f"'{name}': monoatomic species must have empty 'inertia_moments'.")

            elif t == 'linear':
                # Must define positive integer sym_number; inertia length 1
                if pd.isna(sym) or not float(sym).is_integer() or int(sym) <= 0:
                    errs.append(f"'{name}': linear species must define a positive integer 'sym_number'.")
                if len(inertia) != 1:
                    errs.append(f"'{name}': linear species must define 'inertia_moments' with exactly 1 value.")

            elif t == 'non_linear':
                # Must define positive integer sym_number; inertia length 3
                if pd.isna(sym) or not float(sym).is_integer() or int(sym) <= 0:
                    errs.append(f"'{name}': non_linear species must define a positive integer 'sym_number'.")
                if len(inertia) != 3:
                    errs.append(f"'{name}': non_linear species must define 'inertia_moments' with exactly 3 values.")

        if errs:
            raise GasModelError(" ; ".join(errs))

        # Assign normalized/validated frame
        self.df = df

    def add_species(self, species_info: dict = None, species_series: pd.Series = None):
        """
        Add a new gas-phase species to the model.

        Parameters
        ----------
        species_info : dict, optional
            Must include key 'species_name'.
        species_series : pandas.Series, optional
            Must include 'species_name'.
        """
        if species_info is not None and species_series is not None:
            raise GasModelError("Provide either 'species_info' or 'species_series', not both.")
        if species_info is None and species_series is None:
            raise GasModelError("Either 'species_info' or 'species_series' must be provided.")

        if species_info is not None:
            if 'species_name' not in species_info:
                raise GasModelError("Missing 'species_name' in species_info dictionary.")
            species_name = species_info.pop('species_name')
            new_data = species_info
        else:
            if 'species_name' not in species_series:
                raise GasModelError("Missing 'species_name' in species_series.")
            species_name = species_series.pop('species_name')
            new_data = species_series.to_dict()

        if species_name in self.df.index:
            raise GasModelError(f"Species '{species_name}' already exists in the model.")

        # Normalize fields
        # inertia_moments -> list (or [])
        new_data['inertia_moments'] = _to_list_or_empty(new_data.get('inertia_moments', []))
        # degeneracy -> positive int
        deg = new_data.get('degeneracy', 1)
        try:
            deg = int(float(deg))
        except Exception:
            raise GasModelError(f"'degeneracy' for species '{species_name}' must be an integer.")
        if deg <= 0:
            raise GasModelError(f"'degeneracy' for species '{species_name}' must be >= 1.")
        new_data['degeneracy'] = deg
        # sym_number -> numeric or NA
        sym = new_data.get('sym_number', pd.NA)
        sym = pd.to_numeric(sym, errors='coerce')
        new_data['sym_number'] = sym

        new_row = pd.Series(new_data, name=species_name)
        temp_df = pd.concat([self.df, new_row.to_frame().T], ignore_index=False)

        try:
            self._validate_dataframe(temp_df)
        except GasModelError as e:
            raise GasModelError(f"Invalid data for new species '{species_name}': {e}")

        self.df = temp_df

    def remove_species(self, species_names: list):
        """Remove existing gas-phase species from the model."""
        missing = [name for name in species_names if name not in self.df.index]
        if missing:
            raise GasModelError(f"The following species do not exist and cannot be removed: {missing}")
        self.df = self.df.drop(species_names)
