import math
from typing import Iterable, Sequence, Mapping, Any

# ------------------------------
# Constants (SI and eV flavors)
# ------------------------------
KB_J = 1.380649e-23            # Boltzmann constant [J/K]
KB_eV = 8.617333262145179e-05  # Boltzmann constant [eV/K]
H = 6.62607015e-34             # Planck constant [J*s]
N_A = 6.02214076e+23           # Avogadro number
AMU = 1.0e-3 / N_A             # 1 amu in kg
ANG2_to_m2 = 1.0e-20           # Å^2 -> m^2
amuA2_to_kgm2 = AMU * 1.0e-20  # (amu * Å^2) -> kg*m^2
PI = 3.141592653589793
TWO_PI = 2.0 * PI


# ---------- Basic helpers ----------
def as_eV_list(meV_list: Iterable[float]) -> list[float]:
    """Convert list of energies in meV to eV. Empty/None -> []."""
    if not meV_list:
        return []
    return [float(x) * 1.0e-3 for x in meV_list]


def q_vib(energies_meV: Sequence[float], T: float) -> float:
    """
    Vibrational partition function (product over modes) using harmonic oscillator.
    q_vib_x = exp(-v/(2 k T)) / (1 - exp(-v/(k T)))
    Energies given in meV.
    """
    energies_eV = as_eV_list(energies_meV)
    if not energies_eV:
        return 1.0
    beta = 1.0 / (KB_eV * T)  # 1/eV
    q = 1.0
    for v in energies_eV:
        if v <= 0.0:
            continue
        x = v * beta
        numerator = math.exp(-0.5 * x)
        denom = 1.0 - math.exp(-x)
        if denom <= 0.0:
            denom = 1.0
        q *= (numerator / denom)
    return q


def q_trans2D(A_ang2: float, mass_amu: float, T: float) -> float:
    """2D translational PF: q_trans2D = A * 2*pi*m*k*T / h^2 (dimensionless)."""
    A = float(A_ang2) * ANG2_to_m2
    m = float(mass_amu) * AMU
    return A * (TWO_PI * m * KB_J * T) / (H ** 2)


def q_rot(inertia_moments: Sequence[float] | None, sym_number: float | None, T: float) -> float:
    """
    Rotational PF (rigid rotor).
      - Monoatomic / no rotation (len=0 or None): 1.0
      - Linear (len=1): 8*pi^2*I*k*T / (sigma*h^2)
      - Non-linear (len=3): (sqrt(pi*Ia*Ib*Ic)/sigma) * (8*pi^2*k*T/h^2)^(3/2)
    inertia in amu*Å^2.
    """
    if not inertia_moments:
        # monoatomic or missing -> rotational PF = 1
        return 1.0

    if len(inertia_moments) == 1:
        I = float(inertia_moments[0]) * amuA2_to_kgm2
        sigma = float(sym_number) if sym_number else 1.0
        return (8.0 * (math.pi ** 2) * I * KB_J * T) / (sigma * (H ** 2))

    if len(inertia_moments) == 3:
        Ia = float(inertia_moments[0]) * amuA2_to_kgm2
        Ib = float(inertia_moments[1]) * amuA2_to_kgm2
        Ic = float(inertia_moments[2]) * amuA2_to_kgm2
        sigma = float(sym_number) if sym_number else 1.0
        factor = 8.0 * (math.pi ** 2) * KB_J * T / (H ** 2)
        return (math.sqrt(math.pi * Ia * Ib * Ic) / sigma) * (factor ** 1.5)

    raise ValueError("inertia_moments must have length 0 (monoatomic), 1 (linear), or 3 (non-linear).")


def q_elec(degeneracy: float | int | None) -> float:
    """Electronic PF ~ ground-state degeneracy."""
    try:
        g = float(degeneracy)
    except Exception:
        g = 1.0
    return max(g, 1.0)


def gas_RS_partition(A_ang2: float,
                     molec_data: Mapping[str, Any],
                     vib_RS_meV: Sequence[float],
                     T: float) -> float:
    """
    RS partition function for adsorption (gas in RS):
      q_RS = q_trans2D * q_rot * q_vib * q_elec
    """
    mass_amu = molec_data['gas_molec_weight']

    # inertia_moments may be missing/None/NaN for monoatomic
    imoms_raw = molec_data.get('inertia_moments', [])
    # avoid importing pandas; treat float('nan') as missing too
    if imoms_raw is None or (isinstance(imoms_raw, float) and math.isnan(imoms_raw)):
        imoms = []
    elif isinstance(imoms_raw, (list, tuple)):
        imoms = list(imoms_raw)
    else:
        # unknown type -> assume monoatomic/no rotation
        imoms = []

    sigma = molec_data.get('sym_number', 1)
    degen = molec_data.get('degeneracy', 1)

    return (q_trans2D(A_ang2, mass_amu, T)
            * q_rot(imoms, sigma, T)
            * q_vib(vib_RS_meV, T)
            * q_elec(degen))


# ---------- Pre-exponential calculators ----------
def pe_surface(vib_TS_meV: Sequence[float], vib_RS_meV: Sequence[float], T: float) -> float:
    """Surface process: pe = (kB*T/h) * (q_TS / q_RS). Vib-only PFs."""
    q_TS = q_vib(vib_TS_meV, T)
    q_RS = q_vib(vib_RS_meV, T)
    return (KB_J * T / H) * (q_TS / (q_RS if q_RS > 0.0 else 1.0))


def pe_activated_ads(A_ang2: float,
                     molec_data: Mapping[str, Any],
                     vib_TS_meV: Sequence[float],
                     vib_RS_meV: Sequence[float],
                     T: float) -> float:
    """Activated adsorption: pe = A / sqrt(2*pi*m*k*T) * (q_TS / q_RS)."""
    m = float(molec_data['gas_molec_weight']) * AMU
    pref = (float(A_ang2) * ANG2_to_m2) / math.sqrt(TWO_PI * m * KB_J * T)
    q_TS = q_vib(vib_TS_meV, T)
    q_RS = gas_RS_partition(A_ang2, molec_data, vib_RS_meV, T)
    return pref * (q_TS / (q_RS if q_RS > 0.0 else 1.0))


def pe_nonactivated_ads(A_ang2: float, mass_amu: float, T: float) -> float:
    """Non-activated adsorption (2D gas-like TS): pe = A / sqrt(2*pi*m*k*T)."""
    m = float(mass_amu) * AMU
    return (float(A_ang2) * ANG2_to_m2) / math.sqrt(TWO_PI * m * KB_J * T)


# add near the other pe_* functions
def pe_nonactivated_desorption(A_ang2: float,
                               molec_data: Mapping[str, Any],
                               vib_PS_meV: Sequence[float],
                               vib_RS_meV_surface: Sequence[float],
                               T: float) -> float:
    """
    Non-activated desorption:
        pe = (kB*T/h) * (q_PS / q_RS)
    with
        q_PS = q_trans2D * q_rot * q_vib * q_elec  (gas-like, 2D)
        q_RS = q_vib (surface vibrational only)
    """
    # q_PS (gas-like, depends on product-side molecule)
    q_ps = gas_RS_partition(A_ang2, molec_data, vib_RS_meV=vib_PS_meV, T=T)
    # q_RS (surface vibrational only)
    q_rs = q_vib(vib_RS_meV_surface, T)
    return (KB_J * T / H) * (q_ps / (q_rs if q_rs > 0.0 else 1.0))
