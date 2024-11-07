import numpy as np
import pytest
from zacrostools import calc_functions
from zacrostools.custom_exceptions import CalcFunctionsError


def test_find_nearest():
    array = np.array([1, 3, 5, 7, 9])
    value = 6
    expected = 5
    result = calc_functions.find_nearest(array, value)
    assert result == expected, f"Expected {expected}, got {result}"

    value = 8
    expected = 7
    result = calc_functions.find_nearest(array, value)
    assert result == expected, f"Expected {expected}, got {result}"


def test_get_q_vib():
    temperature = 300  # Kelvin
    vib_energies = [100, 200, 300]  # meV
    result = calc_functions.get_q_vib(temperature, vib_energies)
    expected = 9.32366938280356e-06
    assert np.isclose(result, expected), f"Expected {expected}, got {result}"


def test_get_q_rot_linear():
    temperature = 300  # Kelvin
    inertia_moments = [10.0]  # amu·Å^2 for a linear molecule
    sym_number = 2
    result = calc_functions.get_q_rot(temperature, inertia_moments, sym_number)
    expected = 61.84453275589907
    assert np.isclose(result, expected), f"Expected {expected}, got {result}"


def test_get_q_rot_non_linear():
    temperature = 300  # Kelvin
    inertia_moments = [10.0, 15.0, 20.0]  # amu·Å^2 for a non-linear molecule
    sym_number = 1
    result = calc_functions.get_q_rot(temperature, inertia_moments, sym_number)
    expected = 4223.11128907918
    assert np.isclose(result, expected), f"Expected {expected}, got {result}"


def test_get_q_rot_invalid():
    temperature = 300
    inertia_moments = [10.0, 15.0]  # Invalid number of moments
    sym_number = 1
    with pytest.raises(CalcFunctionsError):
        calc_functions.get_q_rot(temperature, inertia_moments, sym_number)


def test_calc_ads_non_activated():
    area_site = 5.0  # Å^2
    molec_mass = 28.0  # g/mol (e.g., N2)
    temperature = 300  # K
    vib_energies_is = [100, 200, 300]  # meV
    vib_energies_ts = []  # Non-activated process
    vib_energies_fs = [150, 250, 350]  # meV
    inertia_moments = [10.0]  # amu·Å^2 (linear molecule)
    sym_number = 2
    degeneracy = 1

    pe_fwd, pe_rev = calc_functions.calc_ads(
        area_site, molec_mass, temperature,
        vib_energies_is, vib_energies_ts, vib_energies_fs,
        inertia_moments, sym_number, degeneracy
    )

    expected_pe_fwd = 143738873.52217174
    expected_pe_rev = 9.873407036538351e+17

    assert np.isclose(pe_fwd, expected_pe_fwd, rtol=1e-5), f"Expected pe_fwd {expected_pe_fwd}, got {pe_fwd}"
    assert np.isclose(pe_rev, expected_pe_rev, rtol=1e-5), f"Expected pe_rev {expected_pe_rev}, got {pe_rev}"


def test_calc_ads_activated():
    area_site = 5.0  # Å^2
    molec_mass = 28.0  # g/mol (e.g., N2)
    temperature = 300  # K
    vib_energies_is = [100, 200, 300]  # meV
    vib_energies_ts = [120, 220, 320]  # meV
    vib_energies_fs = [150, 250, 350]  # meV
    inertia_moments = [10.0]  # amu·Å^2
    sym_number = 2
    degeneracy = 1

    pe_fwd, pe_rev = calc_functions.calc_ads(
        area_site, molec_mass, temperature,
        vib_energies_is, vib_energies_ts, vib_energies_fs,
        inertia_moments, sym_number, degeneracy
    )

    expected_pe_fwd = 5223.684306081529
    expected_pe_rev = 35881428677235.87

    assert np.isclose(pe_fwd, expected_pe_fwd, rtol=1e-5), f"Expected pe_fwd {expected_pe_fwd}, got {pe_fwd}"
    assert np.isclose(pe_rev, expected_pe_rev, rtol=1e-5), f"Expected pe_rev {expected_pe_rev}, got {pe_rev}"


def test_calc_surf_proc():
    temperature = 300  # K
    vib_energies_is = [100, 200, 300]  # meV
    vib_energies_ts = [150, 250, 350]  # meV
    vib_energies_fs = [200, 300, 400]  # meV

    pe_fwd, pe_rev = calc_functions.calc_surf_proc(
        temperature, vib_energies_is, vib_energies_ts, vib_energies_fs
    )

    expected_pe_fwd = 337272372339.18915
    expected_pe_rev = 114035791835184.86

    assert np.isclose(pe_fwd, expected_pe_fwd, rtol=1e-5), f"Expected pe_fwd {expected_pe_fwd}, got {pe_fwd}"
    assert np.isclose(pe_rev, expected_pe_rev, rtol=1e-5), f"Expected pe_rev {expected_pe_rev}, got {pe_rev}"
