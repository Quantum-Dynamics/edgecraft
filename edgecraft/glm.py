import typing as t

import gileum


class EdgecraftGileum(gileum.BaseGileum):
    """Configuration gileum for edgecraft simulation."""

    glm_name: t.Literal["main"] = "main"
    """Type of simulation."""

    electron_density: float
    """Electron density (m^-2)."""

    magnetic_field: float
    """Magnetic Field (T)."""

    temperature: float
    """Temperature (K)."""
