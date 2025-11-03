# tests/test_calc_functions.py

import math
import numpy as np
import pytest

from zacrostools import calc_functions as cf


def test_as_eV_list():
    assert cf.as_eV_list([1000, 0, 250]) == [1.0, 0.0, 0.25]
    assert cf.as_eV_list([]) == []
    assert cf.as_eV_list(None) == []


def test_q_vib_numeric():
    # T = 300 K, vib energies in meV
    T = 300.0
    vib = [100, 200, 300]
    # Known value (from the HO formula used here)
    expected = 9.32366938463989e-06
    got = cf.q_vib(vib, T)
    assert np.isclose(got, expected, rtol=1e-12), f"q_vib mismatch: {got} vs {expected}"


def test_q_trans2D_numeric():
    # A = 5 Å^2, m = 28 amu, T = 300 K
    T = 300.0
    A = 5.0
    m_amu = 28.0
    expected = 137.80008332596037  # dimensionless
    got = cf.q_trans2D(A, m_amu, T)
    assert np.isclose(got, expected, rtol=1e-12), f"q_trans2D mismatch: {got} vs {expected}"


def test_q_rot_linear_numeric():
    # Linear rotor: 1 inertia moment
    T = 300.0
    inertia = [10.0]  # amu*Å^2
    sigma = 2
    expected = 61.84453277727122
    got = cf.q_rot(inertia, sigma, T)
    assert np.isclose(got, expected, rtol=1e-12), f"q_rot linear mismatch: {got} vs {expected}"


def test_q_rot_nonlinear_numeric():
    # Non-linear rotor: 3 inertia moments
    T = 300.0
    inertia = [10.0, 15.0, 20.0]  # amu*Å^2
    sigma = 1
    expected = 4223.111291268305
    got = cf.q_rot(inertia, sigma, T)
    assert np.isclose(got, expected, rtol=1e-12), f"q_rot nonlinear mismatch: {got} vs {expected}"


def test_q_rot_invalid_raises():
    T = 300.0
    bad_inertia = [10.0, 15.0]  # invalid length
    with pytest.raises(ValueError):
        cf.q_rot(bad_inertia, sym_number=1, T=T)


def test_q_elec_defaults_and_values():
    assert cf.q_elec(None) == 1.0
    assert cf.q_elec(0) == 1.0
    assert cf.q_elec(1) == 1.0
    assert cf.q_elec(3) == 3.0


def test_gas_RS_partition_composition():
    # Check that gas_RS_partition equals product of components
    T = 300.0
    A = 5.0
    molec = {
        "gas_molec_weight": 28.0,      # amu
        "inertia_moments": [10.0],     # linear
        "sym_number": 2,
        "degeneracy": 1,
    }
    vib_RS = [100, 200, 300]

    # Build product explicitly
    q_trans = cf.q_trans2D(A, molec["gas_molec_weight"], T)
    q_rot = cf.q_rot(molec["inertia_moments"], molec["sym_number"], T)
    q_vib = cf.q_vib(vib_RS, T)
    q_elec = cf.q_elec(molec["degeneracy"])
    expected = q_trans * q_rot * q_vib * q_elec

    got = cf.gas_RS_partition(A, molec, vib_RS, T)
    assert np.isclose(got, expected, rtol=1e-12), "gas_RS_partition does not match product of components"


def test_pe_surface_numeric():
    # Surface process: pe = (kB*T/h) * (q_TS/q_RS)
    T = 300.0
    vib_RS = [100, 200, 300]
    vib_TS = [150, 250, 350]
    expected = 337272372355.2879  # s^-1
    got = cf.pe_surface(vib_TS_meV=vib_TS, vib_RS_meV=vib_RS, T=T)
    assert np.isclose(got, expected, rtol=1e-10), f"pe_surface mismatch: {got} vs {expected}"


def test_pe_activated_ads_numeric():
    # pe = A / sqrt(2*pi*m*k*T) * (q_TS / q_RS)
    T = 300.0
    A = 5.0
    molec = {
        "gas_molec_weight": 28.0,  # amu
        "inertia_moments": [10.0],
        "sym_number": 2,
        "degeneracy": 1,
    }
    vib_RS = [100, 200, 300]
    vib_TS = [120, 220, 320]
    expected = 5.22368430437502e-02  # s^-1 Pa^-1
    got = cf.pe_activated_ads(A_ang2=A, molec_data=molec, vib_TS_meV=vib_TS, vib_RS_meV=vib_RS, T=T)
    assert np.isclose(got, expected, rtol=1e-12), f"pe_activated_ads mismatch: {got} vs {expected}"


def test_pe_nonactivated_ads_numeric():
    # pe = A / sqrt(2*pi*m*k*T)
    T = 300.0
    A = 5.0
    mass_amu = 28.0
    expected = 1437.3887352217173  # s^-1 Pa^-1
    got = cf.pe_nonactivated_ads(A_ang2=A, mass_amu=mass_amu, T=T)
    assert np.isclose(got, expected, rtol=1e-12), f"pe_nonactivated_ads mismatch: {got} vs {expected}"


def test_pe_nonactivated_desorption_numeric():
    # pe = (kB*T/h) * (q_PS / q_RS)
    # q_PS = q_trans2D * q_rot * q_vib * q_elec (gas-like, uses PS data)
    # q_RS = q_vib (surface)
    T = 300.0
    A = 5.0
    molec_ps = {
        "gas_molec_weight": 28.0,  # amu
        "inertia_moments": [10.0],  # linear
        "sym_number": 2,
        "degeneracy": 1,
    }
    vib_PS = [150, 250, 350]
    vib_RS_surface = [100, 200, 300]
    expected = 2.874296463198428e15  # s^-1
    got = cf.pe_nonactivated_desorption(
        A_ang2=A,
        molec_data=molec_ps,
        vib_PS_meV=vib_PS,
        vib_RS_meV_surface=vib_RS_surface,
        T=T
    )
    assert np.isclose(got, expected, rtol=1e-12), f"pe_nonactivated_desorption mismatch: {got} vs {expected}"
