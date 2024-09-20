import numpy as np
from zacrostools.read_functions import parse_general_output, get_data_specnum, get_surf_specs_data
from zacrostools.custom_exceptions import *


def detect_issues(path, window_percent):

    energy_slope_threshold = 5.0e-10  # eV/Å²/step
    time_linear_fit_threshold = 0.95

    def reduce_size(time, energy, nevents, size=100):
        if len(nevents) <= size:
            return time, energy, nevents
        else:
            indices = np.round(np.linspace(0, len(nevents) - 1, size)).astype(int)
            return time[indices], energy[indices], nevents[indices]

    kmc_output = KMCOutput(path=path, window_percent=window_percent,
                           window_type='nevents', weights='nevents')

    # Reduce arrays to 100 elements if necessary
    time_reduced, energy_reduced, nevents_reduced = reduce_size(time=kmc_output.time,
                                                                energy=kmc_output.energy,
                                                                nevents=kmc_output.nevents)

    # Check for a positive or negative trend in energy using linear regression
    coeffs_energy = np.polyfit(nevents_reduced, energy_reduced, 1)
    slope_energy = coeffs_energy[0]
    energy_trend = abs(slope_energy) > energy_slope_threshold

    # Perform linear regression on time vs. nevents
    coeffs_time = np.polyfit(nevents_reduced, time_reduced, 1)
    slope_time = coeffs_time[0]
    intercept_time = coeffs_time[1]
    time_predicted = slope_time * nevents_reduced + intercept_time
    r_squared_time = np.corrcoef(time_reduced, time_predicted)[0, 1] ** 2
    time_not_linear = r_squared_time < time_linear_fit_threshold

    # Detect issues
    has_issues = energy_trend or time_not_linear

    return has_issues


class KMCOutput:
    """A class that represents a KMC output

    Attributes
    ----------
    n_gas_species: int
        Number of gas species.
    gas_species_names: list of str
        Gas species names.
    n_surf_species: int
        Number of surface species.
    surf_species_names: list of str
        Surface species names.
    n_sites: int
        Total number of lattice sites.
    area: float
        Lattice surface area (in Å^2)
    site_types: dict
        Site type names and total number of sites of that type
    nevents: np.Array
        Number of events occurred.
    time: np.Array
        Simulated time (in s).
    final_time: float
        Final simulated time (in s).
    energy: np.Array
        Lattice energy (in eV·Å^-2).
    av_energy: float
        Average lattice energies (in eV·Å^-2).
    final_energy: float
        Final lattice energy (in eV·Å^-2).
    production: dict
        Gas species produced. Example: KMCOutput.production['CO']
    total_production: dict
        Total number of gas species produced. Example: KMCOutput.total_production['CO']
    tof: dict
        TOF of gas species (in molec·s^-1·Å^-2). Example: KMCOutput.tof['CO2']
    coverage: dict
        Coverage of surface species (in %). Example: KMCOutput.coverage['CO']
    av_coverage: dict
        Average coverage of surface species (in %). Example: KMCOutput.av_coverage['CO']
    total_coverage: np.Array
        Total coverage of surface species (in %).
    av_total_coverage: float
        Average total coverage of surface species (in %).
    dominant_ads: str
        Most dominant surface species, to plot the kinetic phase diagrams.
    coverage_per_site_type: dict
        Coverage of surface species per site type (in %).
    av_coverage_per_site_type: dict
        Average coverage of surface species per site type (in %).
    total_coverage_per_site_type: dict
        Total coverage of surface species per site type (in %). Example: KMCOutput.total_coverage_per_site_type['top']
    av_total_coverage_per_site_type: dict
        Average total coverage of surface species per site type (in %).
    dominant_ads_per_site_type: dict
        Most dominant surface species per site type, to plot the kinetic phase diagrams.
    """

    @enforce_types
    def __init__(self, path: str, window_percent: Union[list, None] = None, window_type: str = 'time',
                 weights: Union[str, None] = None):

        """
        Parameters
        ----------
        path: str
            The path where the output files are located.
        window_percent: list
            A list of two elements [initial_percent, final_percent] specifying the window of the total simulation. The
            values should be between 0 and 100, representing the percentage of the total simulated time or the total
            number of events to be considered. Default: [0, 100]
        window_type: str
            The type of window to apply when calculating averages (e.g. av_coverage) or TOF. Can be 'time' or 'nevents'.
            - 'time': Apply a window over the simulated time.
            - 'nevents': Apply a window over the number of simulated events.
        weights: str (optional)
            Weights for calculating the weighted average. Possible values: 'time', 'nevents', None. If None, all weights
            are set to 1. Default value: None.
        """

        self.path = path
        if window_percent is None:
            window_percent = [0.0, 100.0]

        # Get data from general_output.txt file
        data_general = parse_general_output(path)
        self.n_gas_species = data_general['n_gas_species']
        self.gas_species_names = data_general['gas_species_names']
        self.n_surf_species = data_general['n_surf_species']
        self.surf_species_names = data_general['surf_species_names']
        self.n_sites = data_general['n_sites']
        self.area = data_general['area']
        self.site_types = data_general['site_types']

        # Get data from specnum_output.txt file
        data_specnum, header = get_data_specnum(path=path, window_percent=window_percent, window_type=window_type)
        self.nevents = data_specnum[:, 1]
        self.time = data_specnum[:, 2]
        self.final_time = data_specnum[-1, 2]
        self.energy = data_specnum[:, 4] / self.area  # in eV/Å2
        self.energy_slope = abs(np.polyfit(self.nevents, self.energy, 1)[0])  # in eV/Å2/step
        self.final_energy = data_specnum[-1, 4] / self.area
        self.av_energy = self.get_average(array=self.energy, weights=weights)

        # Compute production and TOF
        self.production = {}  # in molec
        self.total_production = {}  # useful when calculating selectivity (i.e., set min_total_production)
        self.tof = {}  # in molec·s^-1·Å^-2
        for i in range(5 + self.n_surf_species, len(header)):
            gas_spec = header[i]
            self.production[gas_spec] = data_specnum[:, i]
            self.total_production[gas_spec] = data_specnum[-1, i] - data_specnum[0, i]
            if len(data_specnum) > 1 and data_specnum[-1, i] != 0:
                """ If the catalyst is poisoned, it could be that the last ∆t is very high and the time window only
                contains one row. In that case (len(data_specnum) = 1), set tof = 0"""
                self.tof[header[i]] = np.polyfit(data_specnum[:, 2], data_specnum[:, i], 1)[0] / self.area
            else:
                self.tof[header[i]] = 0.00

        # Compute coverages (per total number of sites)
        surf_specs_data = get_surf_specs_data(self.path)
        self.coverage = {}
        self.av_coverage = {}
        for i in range(5, 5 + self.n_surf_species):
            surf_spec = header[i].replace('*', '')
            num_dentates = surf_specs_data[surf_spec]['surf_specs_dent']
            self.coverage[surf_spec] = data_specnum[:, i] * num_dentates / self.n_sites * 100
            self.av_coverage[surf_spec] = self.get_average(array=self.coverage[surf_spec], weights=weights)
        self.total_coverage = sum(self.coverage.values())
        self.av_total_coverage = min(sum(self.av_coverage.values()), 100)  # to prevent 100.00000000001 (num. error)
        self.dominant_ads = max(self.av_coverage, key=self.av_coverage.get)

        # Compute partial coverages (per total number of sites of a given type)
        self.coverage_per_site_type = {}
        self.av_coverage_per_site_type = {}
        for site_type in self.site_types:
            self.coverage_per_site_type[site_type] = {}
            self.av_coverage_per_site_type[site_type] = {}
        for i in range(5, 5 + self.n_surf_species):
            surf_spec = header[i].replace('*', '')
            site_type = surf_specs_data[surf_spec]['site_type']
            num_dentates = surf_specs_data[surf_spec]['surf_specs_dent']
            self.coverage_per_site_type[site_type][surf_spec] = data_specnum[:, i] * num_dentates / self.site_types[
                surf_specs_data[surf_spec]['site_type']] * 100
            self.av_coverage_per_site_type[site_type][surf_spec] = self.get_average(
                array=self.coverage_per_site_type[site_type][surf_spec], weights=weights)
        self.total_coverage_per_site_type = {}
        self.av_total_coverage_per_site_type = {}
        self.dominant_ads_per_site_type = {}
        for site_type in self.site_types:
            self.total_coverage_per_site_type[site_type] = sum(self.coverage_per_site_type[site_type].values())
            self.av_total_coverage_per_site_type[site_type] = min(sum(
                self.av_coverage_per_site_type[site_type].values()), 100)  # to prevent 100.00000000001 (num. error)
            self.dominant_ads_per_site_type[site_type] = max(self.av_coverage_per_site_type[site_type],
                                                             key=self.av_coverage_per_site_type[site_type].get)

    def get_average(self, array, weights):

        if weights not in [None, 'time', 'nevents']:
            raise KMCOutputError(f"'weights' must be one of the following: 'none' (default), 'time', or 'nevents'.")

        if len(array) == 1:
            """ If the catalyst is poisoned, it could be that the last ∆t is very high and the time window only
            contains one row. In that case (len(array) = 1), do not compute the average"""
            return array
        else:
            if weights is None:
                return np.average(array)
            elif weights == 'time':
                return np.average(array[1:], weights=np.diff(self.time))
            elif weights == 'nevents':
                return np.average(array[1:], weights=np.diff(self.nevents))

    @enforce_types
    def get_selectivity(self, main_product: str, side_products: list):
        """
        Get the selectivity.

        Parameters
        ----------
        main_product: str
            Name of the main product
        side_products: list of str
            Names of the side products

        """
        selectivity = float('NaN')
        tof_side_products = 0.0
        for side_product in side_products:
            tof_side_products += self.tof[side_product]
        if self.tof[main_product] + tof_side_products != 0:
            selectivity = self.tof[main_product] / (self.tof[main_product] + tof_side_products) * 100
        return selectivity


