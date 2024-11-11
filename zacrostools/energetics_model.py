import ast
from typing import Union
from pathlib import Path
import pandas as pd
from zacrostools.write_functions import write_header
from zacrostools.custom_exceptions import EnergeticsModelError, enforce_types


class EnergeticsModel:
    """A class that represents a KMC energetics model.

    Parameters:

    energetics_data: pd.DataFrame
        Information on the energetics model.
        The cluster name is taken as the index of each row.

        The following columns are required:
            - cluster_eng (float): Cluster formation energy (in eV)
            - site_types (str): The types of each site in the pattern
            - lattice_state (list): Cluster configuration in Zacros format, e.g., ['1 CO* 1','2 CO* 1']
        The following columns are optional:
            - neighboring (str): Connectivity between sites involved, e.g., 1-2. Default value: None
            - angles (str): Angle between sites in Zacros format, e.g., '1-2-3:180'. Default value: None
            - graph_multiplicity (int): Symmetry number of the cluster, e.g., 2. Default value: None
    """

    REQUIRED_COLUMNS = {'cluster_eng', 'site_types', 'lattice_state'}
    OPTIONAL_COLUMNS = {'neighboring', 'angles', 'graph_multiplicity'}
    LIST_COLUMNS = ['lattice_state']

    @enforce_types
    def __init__(self, energetics_data: pd.DataFrame = None):
        if energetics_data is None:
            raise EnergeticsModelError("energetics_data must be provided as a Pandas DataFrame.")
        self.df = energetics_data.copy()
        self._validate_dataframe()

    @classmethod
    def from_dict(cls, clusters_dict: dict):
        """
        Create an EnergeticsModel instance from a dictionary.

        Parameters:
            clusters_dict (dict): Dictionary where keys are cluster names and values are dictionaries
                                  of cluster properties.

        Returns:
            EnergeticsModel: An instance of EnergeticsModel.
        """
        try:
            df = pd.DataFrame.from_dict(clusters_dict, orient='index')
            return cls.from_df(df)
        except Exception as e:
            raise EnergeticsModelError(f"Failed to create EnergeticsModel from dictionary: {e}")

    @classmethod
    def from_csv(cls, csv_path: Union[str, Path]):
        """
        Create an EnergeticsModel instance by reading a CSV file.

        Parameters:
            csv_path (Union[str, Path]): Path to the CSV file.

        Returns:
            EnergeticsModel: An instance of EnergeticsModel.
        """
        try:
            csv_path = Path(csv_path)
            if not csv_path.is_file():
                raise EnergeticsModelError(f"The CSV file '{csv_path}' does not exist.")

            df = pd.read_csv(csv_path, index_col=0, dtype=str)

            # Parse list-like columns
            for col in cls.LIST_COLUMNS:
                if col in df.columns:
                    df[col] = df[col].apply(cls._parse_list_cell)
                else:
                    # Validation will catch missing required list columns
                    pass

            # Convert numerical columns to appropriate types
            numeric_columns = ['cluster_eng', 'graph_multiplicity']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            return cls.from_df(df)
        except EnergeticsModelError:
            # Re-raise known EnergeticsModelError without modification
            raise
        except Exception as e:
            raise EnergeticsModelError(f"Failed to create EnergeticsModel from CSV file: {e}")

    @classmethod
    def from_df(cls, df: pd.DataFrame):
        """
        Create an EnergeticsModel instance from a Pandas DataFrame.

        Parameters:
            df (pd.DataFrame): DataFrame containing energetics data.

        Returns:
            EnergeticsModel: An instance of EnergeticsModel.
        """
        return cls(energetics_data=df)

    @staticmethod
    def _parse_list_cell(cell: str) -> list:
        """
        Parses a cell expected to contain a list. If the cell is NaN or empty, returns an empty list.
        Otherwise, evaluates the string to a Python list.

        Parameters:
            cell (str): The cell content as a string.

        Returns:
            list: The parsed list, or empty list if the cell is NaN or empty.

        Raises:
            EnergeticsModelError: If the cell cannot be parsed into a list.
        """
        if pd.isna(cell) or cell.strip() == '':
            return []
        try:
            return ast.literal_eval(cell)
        except (ValueError, SyntaxError) as e:
            raise EnergeticsModelError(f"Failed to parse list from cell: {cell}. Error: {e}")

    def _validate_dataframe(self, df: pd.DataFrame = None):
        """
        Validate that the DataFrame contains the required columns and correct data types.

        Parameters:
            df (pd.DataFrame, optional): The DataFrame to validate.
                                         If None, uses self.df.

        Raises:
            EnergeticsModelError: If validation fails.
        """
        if df is None:
            df = self.df

        missing_columns = self.REQUIRED_COLUMNS - set(df.columns)
        if missing_columns:
            raise EnergeticsModelError(f"Missing required columns: {missing_columns}")

        # Validate data types for list columns
        for col in self.LIST_COLUMNS:
            if not df[col].apply(lambda x: isinstance(x, list)).all():
                invalid_clusters = df[~df[col].apply(lambda x: isinstance(x, list))].index.tolist()
                raise EnergeticsModelError(f"Column '{col}' must contain lists. Invalid clusters: {invalid_clusters}")

        # Validate data types for numeric columns
        for col in ['cluster_eng', 'graph_multiplicity']:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    invalid_clusters = df[~df[col].apply(lambda x: isinstance(x, (int, float)))].index.tolist()
                    raise EnergeticsModelError(f"Column '{col}' must contain numeric values. Invalid clusters: {invalid_clusters}")

        # Validate 'site_types' column
        if not df['site_types'].apply(lambda x: isinstance(x, str)).all():
            invalid_clusters = df[~df['site_types'].apply(lambda x: isinstance(x, str))].index.tolist()
            raise EnergeticsModelError(f"Column 'site_types' must contain string values. Invalid clusters: {invalid_clusters}")

        # Validate 'neighboring' column if present
        if 'neighboring' in df.columns:
            if not df['neighboring'].apply(lambda x: isinstance(x, str) or pd.isna(x)).all():
                invalid_clusters = df[~df['neighboring'].apply(lambda x: isinstance(x, str) or pd.isna(x))].index.tolist()
                raise EnergeticsModelError("Column 'neighboring' must contain string values or NaN.")

        # Validate 'angles' column if present
        if 'angles' in df.columns:
            if not df['angles'].apply(lambda x: isinstance(x, str) or pd.isna(x)).all():
                invalid_clusters = df[~df['angles'].apply(lambda x: isinstance(x, str) or pd.isna(x))].index.tolist()
                raise EnergeticsModelError("Column 'angles' must contain string values or NaN.")

        # Validate 'lattice_state' list contents
        for cluster, lattice_state in df['lattice_state'].items():
            if not isinstance(lattice_state, list):
                raise EnergeticsModelError(f"'lattice_state' for cluster '{cluster}' must be a list.")
            for state in lattice_state:
                if not isinstance(state, str):
                    raise EnergeticsModelError(f"Each entry in 'lattice_state' for cluster '{cluster}' must be a string.")

        # **Removed the default assignment for 'graph_multiplicity'**
        # Assign default values for optional columns if missing or NaN (excluding 'graph_multiplicity')
        if 'graph_multiplicity' not in df.columns:
            pass  # Do not assign a default value
        else:
            # Optionally, you could ensure that graph_multiplicity is positive, etc.
            pass

    def write_energetics_input(self,
                               output_dir: Union[str, Path],
                               sig_figs_energies: int = 8):
        """Writes the energetics_input.dat file.

        Parameters:

        output_dir: Union[str, Path]
            Directory path where the file will be written.
        sig_figs_energies: int, optional
            Number of significant figures for cluster energies. Default is `8`.

        Raises:
            EnergeticsModelError: If file writing fails.
        """
        # Convert output_dir to Path object if it's a string
        output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir

        # Ensure the output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "energetics_input.dat"
        write_header(output_file)
        try:
            with output_file.open('a') as infile:
                infile.write('energetics\n\n')
                infile.write('############################################################################\n\n')
                for cluster in self.df.index:
                    infile.write(f"cluster {cluster}\n\n")
                    lattice_state = self.df.loc[cluster, 'lattice_state']
                    infile.write(f"  sites {len(lattice_state)}\n")

                    neighboring = self.df.loc[cluster].get('neighboring', None)
                    if pd.notnull(neighboring):
                        infile.write(f"  neighboring {neighboring}\n")

                    infile.write("  lattice_state\n")
                    for element in lattice_state:
                        infile.write(f"    {' '.join(element.split())}\n")

                    site_types = self.df.loc[cluster].get('site_types', None)
                    if pd.notnull(site_types):
                        infile.write(f"  site_types {site_types}\n")

                    # **Modify graph_multiplicity handling**
                    graph_multiplicity = self.df.loc[cluster].get('graph_multiplicity', None)
                    if pd.notnull(graph_multiplicity):
                        infile.write(f"  graph_multiplicity {int(graph_multiplicity)}\n")

                    angles = self.df.loc[cluster].get('angles', None)
                    if pd.notnull(angles):
                        infile.write(f"  angles {angles}\n")

                    cluster_eng = self.df.loc[cluster, 'cluster_eng']
                    infile.write(f"  cluster_eng {cluster_eng:.{sig_figs_energies}f}\n\n")
                    infile.write("end_cluster\n\n")
                    infile.write('############################################################################\n\n')
                infile.write("end_energetics\n")
        except IOError as e:
            raise EnergeticsModelError(f"Failed to write to '{output_file}': {e}")

    def add_cluster(self, cluster_info: dict = None, cluster_series: pd.Series = None):
        """
        Add a new cluster to the energetics model.

        Parameters:
            cluster_info (dict, optional): Dictionary containing cluster properties.
                                           Must include a key 'cluster_name' to specify the cluster's name.
            cluster_series (pd.Series, optional): Pandas Series containing cluster properties.
                                                  Must include 'cluster_name' as part of the Series data.

        Raises:
            EnergeticsModelError: If neither cluster_info nor cluster_series is provided,
                                   or if required fields are missing, or if the cluster already exists.
        """
        if cluster_info is not None and cluster_series is not None:
            raise EnergeticsModelError("Provide either 'cluster_info' or 'cluster_series', not both.")

        if cluster_info is None and cluster_series is None:
            raise EnergeticsModelError("Either 'cluster_info' or 'cluster_series' must be provided.")

        if cluster_info is not None:
            if 'cluster_name' not in cluster_info:
                raise EnergeticsModelError("Missing 'cluster_name' in cluster_info dictionary.")
            cluster_name = cluster_info.pop('cluster_name')
            new_data = cluster_info
        else:
            if 'cluster_name' not in cluster_series:
                raise EnergeticsModelError("Missing 'cluster_name' in cluster_series.")
            cluster_name = cluster_series.pop('cluster_name')
            new_data = cluster_series.to_dict()

        # Parse 'lattice_state' using _parse_list_cell
        if 'lattice_state' in new_data:
            new_data['lattice_state'] = self._parse_list_cell(new_data['lattice_state'])
        else:
            raise EnergeticsModelError("Missing 'lattice_state' in new cluster data.")

        # **Modify 'graph_multiplicity' handling**
        if 'graph_multiplicity' in new_data:
            try:
                if pd.isna(new_data['graph_multiplicity']) or new_data['graph_multiplicity'] == '':
                    new_data['graph_multiplicity'] = None
                else:
                    new_data['graph_multiplicity'] = float(new_data['graph_multiplicity'])
            except ValueError:
                raise EnergeticsModelError(f"'graph_multiplicity' for cluster '{cluster_name}' must be numeric.")
        else:
            new_data['graph_multiplicity'] = None  # Set to None instead of 1

        # Assign 'neighboring' and 'angles' if not present
        for optional_col in self.OPTIONAL_COLUMNS - {'graph_multiplicity'}:
            if optional_col not in new_data or pd.isna(new_data[optional_col]):
                new_data[optional_col] = None

        # Ensure 'graph_multiplicity' is handled correctly
        if 'graph_multiplicity' not in new_data or pd.isna(new_data['graph_multiplicity']):
            new_data['graph_multiplicity'] = None

        new_row = pd.Series(new_data, name=cluster_name)

        # Validate required columns
        missing_columns = self.REQUIRED_COLUMNS - set(new_row.index)
        if missing_columns:
            raise EnergeticsModelError(f"Missing required columns in the new cluster: {missing_columns}")

        temp_df = pd.concat([self.df, new_row.to_frame().T], ignore_index=False)

        # Validate the temporary DataFrame
        try:
            self._validate_dataframe(temp_df)
        except EnergeticsModelError as e:
            raise EnergeticsModelError(f"Invalid data for new cluster '{cluster_name}': {e}")

        # Check for duplicate cluster name
        if cluster_name in self.df.index:
            raise EnergeticsModelError(f"Cluster '{cluster_name}' already exists in the model.")

        self.df = temp_df

    def remove_clusters(self, cluster_names: list):
        """
        Remove existing clusters from the energetics model.

        Parameters:
            cluster_names (list): List of cluster names to be removed.

        Raises:
            EnergeticsModelError: If any of the cluster names do not exist in the model.
        """
        missing_clusters = [name for name in cluster_names if name not in self.df.index]
        if missing_clusters:
            raise EnergeticsModelError(f"The following clusters do not exist and cannot be removed: {missing_clusters}")

        self.df = self.df.drop(cluster_names)
