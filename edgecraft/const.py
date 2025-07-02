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


def calc_unit_length_energy(
    B: float,
    multiplier: float,
) -> tuple[float, float]:
    """
    Calculate unit energy for a given magnetic field strength and length scale.

    Parameters
    ----------
    B : float
        Magnetic field strength (T).
    multiplier : float
        Multiplier for the unit length of the system.

    Returns
    -------
    tuple[float, float]
        Unit length (m) and unit energy (J).
    """
    unit_length = calc_magnetic_length(B) * multiplier
    return unit_length, e**2 / (4 * np.pi * dielectric_GaAs * unit_length)


def calc_Landau_level_gap(B: float, unit_energy: float | None = None) -> float:
    """
    Calculate Landau level gap for a given magnetic field strength and length
    scale.

    Parameters
    ----------
    B : float
        Magnetic field strength (T).
    unit_energy : float, optional
        Unit energy (J), by default None.
        If provided, the energy gap will be returned in units of this value.

    Returns
    -------
    float
        Landau level gap (J) or in units of the provided unit energy.
    """
    energy_gap = hbar * e * B / m_GaAs
    if unit_energy is not None:
        return energy_gap / unit_energy
    return energy_gap


def calc_thermal_energy(
    temperature: float,
    unit_energy: float | None = None,
) -> float:
    """
    Calculate thermal energy at a given temperature.

    Parameters
    ----------
    temperature : float
        Temperature (K).
    unit_energy : float, optional
        Unit energy (J), by default None.
        If provided, the thermal energy will be returned in units of this
        value.

    Returns
    -------
    float
        Thermal energy (J) or in units of the provided unit energy.
    """
    thermal_energy = k_B * temperature
    if unit_energy is not None:
        return thermal_energy / unit_energy
    return thermal_energy


def calc_magneticfield_for_nu(
    electron_density: float,
    filling_factor: float,
) -> float:
    """
    Calculate magnetic field strength for a given electron density and
    filling factor.

    Parameters
    ----------
    electron_density : float
        Electron density (m^-2).
    filling_factor : float
        Filling factor (dimensionless).

    Returns
    -------
    float
        Magnetic field strength (T).
    """
    return electron_density * magnetic_flux_quantum / filling_factor
