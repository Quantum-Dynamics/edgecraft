import numpy as np


h = 6.62607015e-34
"""Plank constant  (m^2 kg / s)."""

hbar = h / (2 * np.pi)
"""Reduced Plank constant (m^2 kg / s)."""

c = 2.99792458e8
"""Speed of light (m / s)."""

e = 1.60217663e-19
"""Elementary charge (C)."""

hc = h * c
"""Product of Plank constant and speed of light."""

magnetic_flux_quantum = h / e
"""Magnetic flux quantum."""

klitzing_constant = h / e**2
"""Klitzing constant."""

dielectric_vacuum = 8.8854e-12
"""Vacuum permittivity (F / m)."""

dielectric_GaAs = 12.9 * dielectric_vacuum
"""Permittivity of GaAs (F / m)."""

m_e = 9.109e-31
"""Electron mass (kg)."""

m_GaAs = 0.067 * m_e
"""Effective mass of electrons in GaAs (kg)."""

k_B = 1.380649e-23
"""Boltzmann constant (J / K)."""


def calc_magnetic_length(B: float) -> float:
    """
    Calculate magnetic length for a given magnetic field strength.

    Parameters
    ----------
    B : float
        Magnetic field strength (T).

    Returns
    -------
    float
        Magnetic length (m).
    """
    return np.sqrt(hbar / (e * B))
