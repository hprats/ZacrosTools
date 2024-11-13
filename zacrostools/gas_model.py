import ast
from pathlib import Path
from typing import Union
import pandas as pd
from zacrostools.custom_exceptions import GasModelError, enforce_types


class GasModel:
    """
    Represents gas-phase molecular data for KMC reaction modeling.

    Parameters
    ----------
    gas_data : pandas.DataFrame
        Information on gas-phase molecules. The molecule name is taken as the index of each row.

        **Required columns**:

        - **type** (str): 'non_linear' or 'linear'.
        - **gas_molec_weight** (float): Molecular weight (in amu) of the gas species.
        - **sym_number** (int): Symmetry number of the molecule.
        - **inertia_moments** (list): Moments of inertia for the gas-phase molecule (in amu·Å²).
            - 1 element for linear molecules, 3 elements for non-linear molecules.
            - Can be obtained from `ase.Atoms.get_moments_of_inertia()`.
        - **gas_energy** (float): Formation energy (in eV). Do not include the ZPE.

        Optional columns:

        - **degeneracy** (int): Degeneracy of the ground state, for the calculation of the electronic partition function.
            - Default value: 1.

    Raises
    ------
    GasModelError
        If `gas_data` is not provided, contains duplicates, or is invalid.

    Examples
    --------
    Example DataFrame:

    | index | type       | gas_molec_weight | sym_number | degeneracy | inertia_moments        | gas_energy |
    |-------|------------|------------------|------------|------------|------------------------|------------|
    | CO    | linear     | 28.01            | 1          | 1          | [8.973619026272551]    | 1.96       |
    | O2    | linear     | 32.0             | 2          | 3          | [12.178379354326061]   | 2.6        |
    | CO2   | non_linear | 44.01            | 2          | 1          | [44.317229117708344]   | 0.0        |

    """

    REQUIRED_COLUMNS = {
        'type',
        'gas_molec_weight',
        'sym_number',
        'inertia_moments',
        'gas_energy'
    }

    OPTIONAL_COLUMNS = {'degeneracy'}
    LIST_COLUMNS = ['inertia_moments']

    @enforce_types
    def __init__(self, gas_data: pd.DataFrame = None):
        """
        Initialize the GasModel.

        Parameters
        ----------
        gas_data : pandas.DataFrame
            DataFrame containing gas-phase molecular data.

        Raises
        ------
        GasModelError
            If `gas_data` is not provided, contains duplicates, or is invalid.
        """
        if gas_data is None:
            raise GasModelError("gas_data must be provided as a Pandas DataFrame.")
        self.df = gas_data.copy()
        self._validate_dataframe()

    @classmethod
    def from_dict(cls, species_dict: dict):
        """
        Create a GasModel instance from a dictionary.

        Parameters
        ----------
        species_dict : dict
            Dictionary where keys are species names and values are dictionaries of species properties.

        Returns
        -------
        GasModel
            An instance of GasModel.

        Raises
        ------
        GasModelError
            If the instance cannot be created from the provided dictionary due to duplicates or invalid data.
        """
        try:
            df = pd.DataFrame.from_dict(species_dict, orient='index')

            # Check for duplicate molecule names
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
        """
        Create a GasModel instance by reading a CSV file.

        Parameters
        ----------
        csv_path : Union[str, Path]
            Path to the CSV file.

        Returns
        -------
        GasModel
            An instance of GasModel.

        Raises
        ------
        GasModelError
            If the CSV file cannot be read, contains duplicates, or the data is invalid.
        """
        try:
            csv_path = Path(csv_path)
            if not csv_path.is_file():
                raise GasModelError(f"The CSV file '{csv_path}' does not exist.")

            df = pd.read_csv(csv_path, index_col=0, dtype=str)

            # Check for duplicate molecule names
            if df.index.duplicated().any():
                duplicates = df.index[df.index.duplicated()].unique().tolist()
                raise GasModelError(f"Duplicate molecule names found in CSV: {duplicates}")

            # Parse list-like columns
            for col in cls.LIST_COLUMNS:
                if col in df.columns:
                    df[col] = df[col].apply(cls._parse_list_cell)

            # Convert numeric columns to appropriate types
            numeric_columns = ['gas_molec_weight', 'sym_number', 'gas_energy', 'degeneracy']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            return cls.from_df(df)
        except GasModelError:
            raise
        except Exception as e:
            raise GasModelError(f"Failed to create GasModel from CSV file: {e}")

    @classmethod
    def from_df(cls, df: pd.DataFrame):
        """
        Create a GasModel instance from a Pandas DataFrame.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame containing gas data.

        Returns
        -------
        GasModel
            An instance of GasModel.

        Raises
        ------
        GasModelError
            If the DataFrame contains duplicates or is invalid.
        """
        # Check for duplicate molecule names
        if df.index.duplicated().any():
            duplicates = df.index[df.index.duplicated()].unique().tolist()
            raise GasModelError(f"Duplicate molecule names found in DataFrame: {duplicates}")

        return cls(gas_data=df)

    @staticmethod
    def _parse_list_cell(cell):
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
        GasModelError
            If the cell cannot be parsed into a list.

        """
        if pd.isna(cell) or cell.strip() == '':
            return []
        try:
            return ast.literal_eval(cell)
        except (ValueError, SyntaxError) as e:
            raise GasModelError(f"Failed to parse list from cell: {cell}. Error: {e}")

    def _validate_dataframe(self, df=None):
        """
        Validate that the DataFrame contains the required columns and correct data types.

        Parameters
        ----------
        df : pandas.DataFrame, optional
            The DataFrame to validate. If None, uses self.df.

        Raises
        ------
        GasModelError
            If validation fails.
        """
        if df is None:
            df = self.df

        # Check for duplicate molecule names
        if df.index.duplicated().any():
            duplicates = df.index[df.index.duplicated()].unique().tolist()
            raise GasModelError(f"Duplicate molecule names found: {duplicates}")

        missing_columns = self.REQUIRED_COLUMNS - set(df.columns)
        if missing_columns:
            raise GasModelError(f"Missing required columns: {missing_columns}")

        # Validate data types for list columns
        for col in self.LIST_COLUMNS:
            if not df[col].apply(lambda x: isinstance(x, list)).all():
                invalid_species = df[~df[col].apply(lambda x: isinstance(x, list))].index.tolist()
                raise GasModelError(f"Column '{col}' must contain lists. Invalid species: {invalid_species}")

        # Validate 'degeneracy' column
        if 'degeneracy' not in df.columns:
            df['degeneracy'] = 1  # Default value
        else:
            # Fill missing or NaN values with default
            df['degeneracy'] = df['degeneracy'].fillna(1)
            # Convert to numeric (integer)
            df['degeneracy'] = pd.to_numeric(df['degeneracy'], errors='coerce')
            # Replace NaN after conversion with default
            df['degeneracy'] = df['degeneracy'].fillna(1)
            # Ensure all values are integers
            if not df['degeneracy'].apply(lambda x: isinstance(x, (int, float)) and float(x).is_integer()).all():
                invalid_species = df[~df['degeneracy'].apply(lambda x: isinstance(x, (int, float)) and float(x).is_integer())].index.tolist()
                raise GasModelError(f"Column 'degeneracy' must contain integer values. Invalid species: {invalid_species}")
            # Convert to integer type
            df['degeneracy'] = df['degeneracy'].astype(int)

        # Validate data types for numeric columns
        numeric_columns = ['gas_molec_weight', 'sym_number', 'gas_energy']
        for col in numeric_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                invalid_species = df[~df[col].apply(lambda x: isinstance(x, (int, float)))].index.tolist()
                raise GasModelError(f"Column '{col}' must contain numeric values. Invalid species: {invalid_species}")

        # Validate 'type' column
        if not df['type'].apply(lambda x: isinstance(x, str) and x in ['linear', 'non_linear']).all():
            invalid_species = df[~df['type'].apply(lambda x: isinstance(x, str) and x in ['linear', 'non_linear'])].index.tolist()
            raise GasModelError(f"Column 'type' must contain 'linear' or 'non_linear'. Invalid species: {invalid_species}")

        # Validate 'inertia_moments' based on 'type'
        for idx, row in df.iterrows():
            if row['type'] == 'linear' and len(row['inertia_moments']) != 1:
                raise GasModelError(f"Species '{idx}' is linear and must have exactly 1 inertia moment. Found: {len(row['inertia_moments'])}")
            elif row['type'] == 'non_linear' and len(row['inertia_moments']) != 3:
                raise GasModelError(f"Species '{idx}' is non-linear and must have exactly 3 inertia moments. Found: {len(row['inertia_moments'])}")

        # Assign the validated DataFrame back to self.df
        self.df = df

    def add_species(self, species_info: dict = None, species_series: pd.Series = None):
        """
        Add a new gas-phase species to the model.

        Parameters
        ----------
        species_info : dict, optional
            Dictionary containing species properties. Must include a key 'species_name' to specify the species' name.
        species_series : pandas.Series, optional
            Pandas Series containing species properties. Must include 'species_name' as part of the Series data.

        Raises
        ------
        GasModelError
            If neither `species_info` nor `species_series` is provided, or if required fields are missing,
            or if the species already exists.
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

        # Check if species already exists
        if species_name in self.df.index:
            raise GasModelError(f"Species '{species_name}' already exists in the model.")

        # Parse list-like columns if necessary
        for col in self.LIST_COLUMNS:
            if col in new_data and pd.notna(new_data[col]):
                if not isinstance(new_data[col], list):
                    new_data[col] = self._parse_list_cell(new_data[col])
            else:
                new_data[col] = []

        # Handle 'degeneracy'
        if 'degeneracy' not in new_data or pd.isna(new_data['degeneracy']) or new_data['degeneracy'] == '':
            new_data['degeneracy'] = 1  # Default value
        else:
            try:
                new_data['degeneracy'] = int(new_data['degeneracy'])
            except (ValueError, TypeError):
                raise GasModelError(f"'degeneracy' for species '{species_name}' must be an integer.")

        new_row = pd.Series(new_data, name=species_name)

        # Create a temporary DataFrame with the new row appended for validation
        temp_df = pd.concat([self.df, new_row.to_frame().T], ignore_index=False)

        # Validate the temporary DataFrame
        try:
            self._validate_dataframe(temp_df)
        except GasModelError as e:
            raise GasModelError(f"Invalid data for new species '{species_name}': {e}")

        self.df = temp_df

    def remove_species(self, species_names: list):
        """
        Remove existing gas-phase species from the model.

        Parameters
        ----------
        species_names : list
            List of species names to be removed.

        Raises
        ------
        GasModelError
            If any of the species names do not exist in the model.
        """
        missing_species = [name for name in species_names if name not in self.df.index]
        if missing_species:
            raise GasModelError(f"The following species do not exist and cannot be removed: {missing_species}")

        self.df = self.df.drop(species_names)
