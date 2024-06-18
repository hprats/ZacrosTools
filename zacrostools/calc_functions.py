import sys
import numpy as np
from math import sqrt, exp
from scipy.constants import pi, N_A, k, h, physical_constants

k_eV = physical_constants["Boltzmann constant in eV/K"][0]
atomic_mass = physical_constants["atomic mass constant"][0]


def find_nearest(array, value):
    """Finds the element of an array whose value is closest to a given value, and returns its index.

    Parameters
    ----------
    array: np.Array
    value: float

    Returns
    -------
    array[idx]: int

    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def get_q_vib(temperature, vib_energies):
    """Calculates the vibrational partition function.

    Parameters
    ----------
    temperature: float
        Temperature (in K)
    vib_energies: list of float
        Vibrational energies of the molecule or adsorbate (in meV)

    Returns
    -------
    q_vib: float
        Vibrational partition function

    """
    q_vib = 1.0
    for v in vib_energies:
        q_vib = q_vib * exp(- v / (1000 * 2 * k_eV * temperature)) / (1 - exp(- v / (1000 * k_eV * temperature)))
    return q_vib


def get_q_rot(temperature, inertia_moments: list, sym_number):
    """Calculates the rotational partition function.

    Parameters
    ----------
    temperature: float
        Temperature (in K)
    inertia_moments: list
        Moments of inertia in amu·Å^2. 1 element for linear molecules, 3 elements for non-linear molecules. Can be
        obtained from ase.Atoms.get_moments_of_inertia()
    sym_number: int
        Molecule symmetry number

    Returns
    -------
    q_rot_gas: float
        Rotational partition function

    """

    if len(inertia_moments) == 1:  # linear
        i = inertia_moments[0] * atomic_mass / 1.0e20  # from amu*Å2 to kg*m2
        q_rot_gas = 8 * pi ** 2 * i * k * temperature / (sym_number * h ** 2)
    elif len(inertia_moments) == 3:  # non-linear
        i_a = inertia_moments[0] * atomic_mass / 1.0e20
        i_b = inertia_moments[1] * atomic_mass / 1.0e20
        i_c = inertia_moments[2] * atomic_mass / 1.0e20
        q_rot_gas = (sqrt(pi * i_a * i_b * i_c) / sym_number) * (8 * pi ** 2 * k * temperature / h ** 2) ** (3 / 2)
    else:
        sys.exit(f"Invalid inertia_moments")
    return q_rot_gas


def calc_ads(area_site, molec_mass, temperature, vib_energies_is, vib_energies_ts, vib_energies_fs,
             inertia_moments: list, sym_number, degeneracy=1):
    """Calculates the forward and reverse pre-exponential factors for a reversible activated adsorption.

    Parameters
    ----------
    area_site: float
        Area of an adsorption site (in Å^2)
    molec_mass: float
        Molecular mass (in g/mol) of the gas species
    temperature: float
        Temperature (in K)
    vib_energies_is: list
        Vibrational energies for the initial state (in meV)
    vib_energies_ts: list
        Vibrational energies for the transition state (in meV)
    vib_energies_fs: list
        Vibrational energies for the final state (in meV)
    inertia_moments: list
        Moments of inertia for the gas-phase molecule (in amu·Å^2). 1 element for linear molecules, 3 elements for
        non-linear molecules. Can be obtained from ase.Atoms.get_moments_of_inertia()
    sym_number: int
        Symmetry number of the molecule
    degeneracy: int
        Degeneracy of the ground state, for the calculation of the electronic partition function. Default value: 1

    Returns
    -------
    pe_fwd: float
        Pre-exponential factor in the forward direction (in s^-1·bar^-1)
    pe_rev: float
        Pre-exponential factor in the reverse direction (in s^-1)

    """
    area_site = area_site * 1.0e-20  # Å^2 to m^2
    m = molec_mass * 1.0e-3 / N_A  # g/mol to kg/molec
    q_vib_gas = get_q_vib(temperature=temperature, vib_energies=vib_energies_is)
    q_rot_gas = get_q_rot(temperature=temperature, inertia_moments=inertia_moments, sym_number=sym_number)
    q_trans_2d_gas = area_site * 2 * pi * m * k * temperature / h ** 2
    q_el_gas = degeneracy
    q_vib_ads = get_q_vib(temperature=temperature, vib_energies=vib_energies_fs)
    if not vib_energies_ts:  # non-activated
        pe_fwd = area_site / sqrt(2 * pi * m * k * temperature) * 1e5  # Pa-1 to bar-1
        pe_rev = (q_el_gas * q_vib_gas * q_rot_gas * q_trans_2d_gas / q_vib_ads) * (k * temperature / h)
    else:  # activated
        q_vib_ts = get_q_vib(temperature=temperature, vib_energies=vib_energies_ts)
        pe_fwd = (q_vib_ts / (q_el_gas * q_vib_gas * q_rot_gas * q_trans_2d_gas)) * (area_site / sqrt(2 * pi * m * k * temperature))
        pe_fwd = pe_fwd * 1e5  # Pa-1 to bar-1
        pe_rev = (q_vib_ts / q_vib_ads) * (k * temperature / h)
    return pe_fwd, pe_rev


def calc_surf_proc(temperature, vib_energies_is, vib_energies_ts, vib_energies_fs):
    """Calculates the forward and reverse pre-exponential factors for a reversible surface process.

    Parameters
    ----------
    temperature: float
        Temperature (in K)
    vib_energies_is: list
        Vibrational energies for the initial state (in meV)
    vib_energies_ts: list
        Vibrational energies for the transition state (in meV)
    vib_energies_fs: list
        Vibrational energies for the final state (in meV)

    Returns
    -------
    pe_fwd: float
        Pre-exponential factor in the forward direction (in s^-1)
    pe_rev: float
        Pre-exponential factor in the reverse direction (in s^-1)

    """
    q_vib_initial = get_q_vib(temperature=temperature, vib_energies=vib_energies_is)
    q_vib_ts = get_q_vib(temperature=temperature, vib_energies=vib_energies_ts)
    q_vib_final = get_q_vib(temperature=temperature, vib_energies=vib_energies_fs)
    pe_fwd = (q_vib_ts / q_vib_initial) * (k * temperature / h)
    pe_rev = (q_vib_ts / q_vib_final) * (k * temperature / h)
    return pe_fwd, pe_rev
