import numpy as np
from zacrostools.read_functions import parse_general_output, get_data_specnum
from zacrostools.custom_exceptions import *


class KMCOutput:
    """A class that represents a KMC output

    Parameters
    ----------
    path: str
        Path of the directory containing the output files.
    ignore: float, optional
        Ignore first % of simulated time, i.e., equilibration (in %).
        Default value: 0.0
    coverage_per_site: bool, optional
        If True, calculate the coverage per site type.
        Default value: False
    ads_sites: dict, optional
        A dictionary where the surface species are stored as keys and their values are the site types where they adsorb,
        e.g. {'CO': 'top', 'O': 'hollow'}
        Default value: None


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
    def __init__(self, path: str, ignore: float = 0.0, coverage_per_site: bool = False, ads_sites: dict = None):
        self.path = path

        # Get data from general_output.txt file
        data_general = parse_general_output(path)
        self.n_gas_species = data_general['n_gas_species']
        self.gas_species_names = data_general['gas_species_names']
        self.n_surf_species = data_general['n_surf_species']
        self.surf_species_names = data_general['surf_species_names']
        self.n_sites = data_general['n_sites']
        self.area = data_general['area']
        self.site_types = data_general['site_types']

        # Get data from specnum_output.txt
        data_specnum, header = get_data_specnum(path, ignore)
        self.time = data_specnum[:, 2]
        self.final_time = data_specnum[-1, 2]
        self.energy = data_specnum[:, 4] / self.area
        self.av_energy = np.average(data_specnum[:, 4]) / self.area
        self.final_energy = data_specnum[-1, 4] / self.area

        # Production (molec) and TOF (molec·s^-1·Å^-2)
        self.production = {}
        self.total_production = {}  # useful when calculating selectivity (i.e., set min_total_production)
        self.tof = {}
        for i in range(5 + self.n_surf_species, len(header)):
            ads = header[i]
            self.production[ads] = data_specnum[:, i]
            self.total_production[ads] = data_specnum[-1, i] - data_specnum[0, i]
            if data_specnum[-1, i] != 0:
                self.tof[header[i]] = np.polyfit(data_specnum[:, 2], data_specnum[:, i], 1)[0] / self.area
            else:
                self.tof[header[i]] = 0.00

        # Coverage (%)
        self.coverage = {}
        self.av_coverage = {}
        for i in range(5, 5 + self.n_surf_species):
            ads = header[i].replace('*', '')
            self.coverage[ads] = data_specnum[:, i] / self.n_sites * 100
            self.av_coverage[ads] = np.average(data_specnum[:, i]) / self.n_sites * 100
        self.total_coverage = sum(self.coverage.values())
        self.av_total_coverage = sum(self.av_coverage.values())
        self.dominant_ads = max(self.av_coverage, key=self.av_coverage.get)

        # Coverage per site type (%)
        if len(self.site_types) == 1:
            raise KMCOutputError(f"'coverage_per_site' not available when there is only one site type. Path: "
                                 f"{self.path}")
        if coverage_per_site:
            self.coverage_per_site_type = {}
            self.av_coverage_per_site_type = {}
            for site_type in self.site_types:
                self.coverage_per_site_type[site_type] = {}
                self.av_coverage_per_site_type[site_type] = {}
            for i in range(5, 5 + self.n_surf_species):
                ads = header[i].replace('*', '')
                site_type = ads_sites[ads]
                self.coverage_per_site_type[site_type][ads] = data_specnum[:, i] / self.site_types[ads_sites[ads]] * 100
                self.av_coverage_per_site_type[site_type][ads] = np.average(data_specnum[:, i]) / self.site_types[
                    ads_sites[ads]] * 100
            self.total_coverage_per_site_type = {}
            self.av_total_coverage_per_site_type = {}
            self.dominant_ads_per_site_type = {}
            for site_type in self.site_types:
                self.total_coverage_per_site_type[site_type] = sum(self.coverage_per_site_type[site_type].values())
                self.av_total_coverage_per_site_type[site_type] = sum(
                    self.av_coverage_per_site_type[site_type].values())
                self.dominant_ads_per_site_type[site_type] = max(self.av_coverage_per_site_type[site_type],
                                                                 key=self.av_coverage_per_site_type[site_type].get)

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
