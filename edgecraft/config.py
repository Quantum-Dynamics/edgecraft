"""Configuration class for EdgeCraft simulation using Gileum."""

import numpy as np
from gileum import BaseGileum
from typing import Optional, Any
from pydantic import Field, computed_field, ConfigDict


class EdgeCraftConfig(BaseGileum):
    """Configuration class for EdgeCraft quantum hall edge simulation.
    
    This class defines all the parameters needed to run an EdgeCraft simulation,
    including physical constants, space matrix parameters, and simulation settings.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Physical constants
    n: float = Field(default=1e15, description="electron density in m^-2")
    T: float = Field(default=40e-3, description="temperature in K")
    M: int = Field(default=20, description="magnetic length units")
    
    # Disorder and fluctuation parameters
    U_disorder_eV: float = Field(default=60e-6, description="disorder potential in eV")
    
    # Simulation grid parameters
    x_size_um: float = Field(default=200e-6, description="x dimension in micrometers")
    y_size_um: float = Field(default=150e-6, description="y dimension in micrometers")
    radius_gate_um: float = Field(default=50e-6, description="gate radius in micrometers")
    gate_width_um: float = Field(default=25e-6, description="gate width in micrometers")
    
    # Simulation parameters
    frames: int = Field(default=101, description="number of simulation frames")
    E_gate_min_factor: float = Field(default=0.0, description="min gate energy as factor of E_F")
    E_gate_max_factor: float = Field(default=1.0, description="max gate energy as factor of E_F")
    
    # Confinement potential parameter
    alpha: float = Field(default=1e3, description="confinement strength")
    
    # Output parameters
    output_edge_lengths: str = Field(default="edge_lengths.npy", description="output file for edge lengths")
    output_gate_potential: str = Field(default="gate_potential.npy", description="output file for gate potential")
    
    @computed_field
    @property
    def B_0(self) -> float:
        """Magnetic field in Tesla"""
        from edgecraft import calc_magneticfield_for_nu
        return calc_magneticfield_for_nu(self.n, 1)
    
    @computed_field
    @property
    def l_0(self) -> float:
        """Unit length"""
        from edgecraft import calc_unit_length_energy
        l_0, _ = calc_unit_length_energy(self.B_0, self.M)
        return l_0
    
    @computed_field
    @property
    def E_0(self) -> float:
        """Unit energy"""
        from edgecraft import calc_unit_length_energy
        _, E_0 = calc_unit_length_energy(self.B_0, self.M)
        return E_0
    
    @computed_field
    @property
    def E_LL_gap(self) -> float:
        """Landau level gap"""
        from edgecraft import calc_Landau_level_gap
        return calc_Landau_level_gap(self.B_0, self.E_0)
    
    @computed_field
    @property
    def E_F(self) -> float:
        """Fermi energy"""
        return self.E_LL_gap / 2
    
    @computed_field
    @property
    def E_QH(self) -> float:
        """Quantum Hall energy"""
        return self.E_F / 2
    
    @computed_field
    @property
    def U_thermal(self) -> float:
        """Thermal energy"""
        from edgecraft import calc_thermal_energy
        return calc_thermal_energy(self.T, self.E_0)
    
    @computed_field
    @property
    def U_disorder(self) -> float:
        """Disorder energy in simulation units"""
        from edgecraft import e
        return (self.U_disorder_eV * e) / self.E_0
    
    @computed_field
    @property
    def U_fluc(self) -> float:
        """Total fluctuation energy"""
        return self.U_disorder + self.U_thermal
    
    @computed_field
    @property
    def radius_gate(self) -> int:
        """Gate radius in simulation units"""
        return int(self.radius_gate_um / self.l_0)
    
    @computed_field
    @property
    def x(self) -> Any:
        """X coordinate array"""
        return np.arange(0, int(self.x_size_um / self.l_0), 1)
    
    @computed_field
    @property
    def y(self) -> Any:
        """Y coordinate array"""
        return np.arange(0, int(self.y_size_um / self.l_0), 1)
    
    @computed_field
    @property
    def E_gate_min(self) -> float:
        """Minimum gate energy"""
        return self.E_gate_min_factor * self.E_F
    
    @computed_field
    @property
    def E_gate_max(self) -> float:
        """Maximum gate energy"""
        return self.E_gate_max_factor * self.E_F
    
    @computed_field
    @property
    def E_gate_step(self) -> float:
        """Gate energy step size"""
        return (self.E_gate_max - self.E_gate_min) / (self.frames - 1)