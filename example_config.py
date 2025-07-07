"""Example configuration file for EdgeCraft simulation.

This file demonstrates how to configure an EdgeCraft simulation using Gileum.
You can copy this file and modify the parameters as needed for your simulation.
"""

from edgecraft.config import EdgeCraftConfig

# Create configuration with custom parameters
config = EdgeCraftConfig(
    # Physical constants
    n=1e15,                     # electron density in m^-2
    T=40e-3,                    # temperature in K
    M=20,                       # magnetic length units
    
    # Disorder and fluctuation parameters
    U_disorder_eV=60e-6,        # disorder potential in eV
    
    # Simulation grid parameters
    x_size_um=200e-6,           # x dimension in micrometers
    y_size_um=150e-6,           # y dimension in micrometers
    radius_gate_um=50e-6,       # gate radius in micrometers
    gate_width_um=25e-6,        # gate width in micrometers
    
    # Simulation parameters
    frames=101,                 # number of simulation frames
    E_gate_min_factor=0.0,      # min gate energy as factor of E_F
    E_gate_max_factor=1.0,      # max gate energy as factor of E_F
    
    # Confinement potential parameter
    alpha=1e3,                  # confinement strength
    
    # Output parameters
    output_edge_lengths="edge_lengths.npy",
    output_gate_potential="gate_potential.npy",
)