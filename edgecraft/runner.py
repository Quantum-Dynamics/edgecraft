"""Simulation runner module for EdgeCraft."""

import numpy as np
from typing import Any, Dict
from pathlib import Path

from edgecraft import (
    apply_confinement_potential,
    apply_local_constant_potential,
    apply_QH_energy,
    calc_edge_length,
    find_edge,
    true_circle_in,
)


def run_simulation(config: Any, output_dir: Path, progress_callback=None) -> tuple:
    """Run EdgeCraft simulation with the given configuration.
    
    Args:
        config: Configuration object with simulation parameters
        output_dir: Directory to save output files
        progress_callback: Optional callback function for progress updates
        
    Returns:
        Tuple of (edge_lengths_path, gate_potential_path)
    """
    # Create coordinate meshes
    Y, X = np.meshgrid(config.y, config.x)
    
    # Create space matrix
    space_matrix = (
        true_circle_in(Y, X, config.y[len(config.y) // 2], config.x[len(config.x) // 2], config.radius_gate) |
        (Y >= config.y[len(config.y) // 2])
    ).astype(int)
    
    # Calculate gradients for boundary detection
    diff_y = np.gradient(space_matrix, 1, axis=0)
    diff_x = np.gradient(space_matrix, 1, axis=1)
    
    # Find sample edge (boundary)
    boundary = ((diff_x != 0) | (diff_y != 0)).astype(int)
    boundary_indices = np.array(np.where(boundary == 1)).T
    
    # Define bulk region (space without sample edge)
    bulk = np.copy(space_matrix)
    bulk[boundary == 1] = 0
    bulk_indices = np.array(np.where(bulk == 1)).T
    
    # Create expansion gate
    gate = np.logical_xor(
        true_circle_in(Y, X, config.y[len(config.y) // 2], config.x[len(config.x) // 2], config.radius_gate),
        true_circle_in(
            Y,
            X,
            config.y[len(config.y) // 2],
            config.x[len(config.x) // 2],
            config.radius_gate - int(config.gate_width_um / config.l_0),
        ),
    ).astype(int)
    gate[Y >= config.y[len(config.y) // 2]] = 0
    gate[boundary == 1] = 0
    gate_indices = np.array(np.where(gate == 1)).T
    
    # Initialize energy array
    energy = np.zeros_like(space_matrix, dtype=float)
    energy = apply_QH_energy(energy, config.E_QH, bulk_indices)
    energy = apply_confinement_potential(
        energy,
        bulk_indices,
        boundary_indices,
        config.alpha,
    )
    
    # Run simulation
    edge = find_edge(energy, config.E_F, config.U_fluc, bulk)
    edge_lengths = [calc_edge_length(edge)]
    
    if progress_callback:
        progress_callback(0)
    
    for frame in range(config.frames - 1):
        energy = apply_local_constant_potential(
            energy,
            config.E_gate_step,
            gate_indices,
        )
        edge = find_edge(energy, config.E_F, config.U_fluc, bulk)
        edge_lengths.append(calc_edge_length(edge))
        
        if progress_callback:
            progress_callback(frame + 1)
    
    # Save results
    edge_lengths_path = output_dir / config.output_edge_lengths
    gate_potential_path = output_dir / config.output_gate_potential
    
    np.save(edge_lengths_path, np.array(edge_lengths))
    np.save(gate_potential_path, np.arange(0, config.frames) * config.E_gate_step)
    
    return edge_lengths_path, gate_potential_path