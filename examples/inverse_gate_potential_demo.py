"""
Example demonstrating the inverse gate potential optimization algorithm.

This example shows how to use the new functions to find gate potentials
that produce desired scale factors, implementing the algorithm described
in the GitHub issue.
"""

import numpy as np
import matplotlib.pyplot as plt

from edgecraft import (
    apply_confinement_potential,
    apply_local_constant_potential,
    apply_QH_energy,
    calc_Landau_level_gap,
    calc_edge_length,
    calc_magneticfield_for_nu,
    calc_scale_factor,
    calc_thermal_energy,
    calc_time_unit,
    calc_unit_length_energy,
    find_edge,
    find_gate_potential_for_scale_factor,
    optimize_gate_potential_for_scale_factor,
    true_circle_in,
    e,
)


def setup_simulation():
    """Setup the basic simulation parameters and geometry."""
    # Physical constants
    n = 1e15  # m^-2
    B_0 = calc_magneticfield_for_nu(n, 1)  # T
    T = 40e-3  # K

    # Calculate unit length and energy
    M = 20
    l_0, E_0 = calc_unit_length_energy(B_0, M)
    E_LL_gap = calc_Landau_level_gap(B_0, E_0)
    E_F = E_LL_gap / 2
    E_QH = E_F / 2
    U_thermal = calc_thermal_energy(T, E_0)
    U_disorder = (60e-6 * e) / E_0
    U_fluc = U_disorder + U_thermal

    # Space matrices
    radius_gate = int(50e-6 / l_0)
    x = np.arange(0, int(200e-6 / l_0), 1)
    y = np.arange(0, int(150e-6 / l_0), 1)
    Y, X = np.meshgrid(y, x)

    space_matrix = (
        true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate) |
        (Y >= y[len(y) // 2])
    ).astype(int)
    
    diff_y = np.gradient(space_matrix, 1, axis=0)
    diff_x = np.gradient(space_matrix, 1, axis=1)

    # Sample edge
    boundary = ((diff_x != 0) | (diff_y != 0)).astype(int)
    boundary_indices = np.array(np.where(boundary == 1)).T

    # Bulk (space \ sample edge)
    bulk = np.copy(space_matrix)
    bulk[boundary == 1] = 0
    bulk_indices = np.array(np.where(bulk == 1)).T

    # Expansion gate
    gate = np.logical_xor(
        true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate),
        true_circle_in(
            Y,
            X,
            y[len(y) // 2],
            x[len(x) // 2],
            radius_gate - int(25e-6 / l_0),
        ),
    ).astype(int)
    gate[Y >= y[len(y) // 2]] = 0
    gate[boundary == 1] = 0
    gate_indices = np.array(np.where(gate == 1)).T

    # Initial energy calculations
    alpha = 1e3
    energy = np.zeros_like(space_matrix, dtype=float)
    energy = apply_QH_energy(energy, E_QH, bulk_indices)
    energy = apply_confinement_potential(
        energy,
        bulk_indices,
        boundary_indices,
        alpha,
    )

    return {
        "energy": energy,
        "E_F": E_F,
        "U_fluc": U_fluc,
        "bulk": bulk,
        "gate_indices": gate_indices,
        "E_0": E_0,
        "l_0": l_0,
    }


def generate_reference_data(setup, num_points=51):
    """Generate reference scale factor vs potential data."""
    print("Generating reference data...")
    
    # Calculate initial edge length
    initial_edge = find_edge(setup["energy"], setup["E_F"], setup["U_fluc"], setup["bulk"])
    initial_edge_length = calc_edge_length(initial_edge)
    
    # Generate range of gate potentials
    potentials = np.linspace(0, setup["E_F"], num_points)
    scale_factors = []
    
    for i, potential in enumerate(potentials):
        if i % 10 == 0:
            print(f"  Processing potential {i+1}/{num_points}")
            
        test_energy = np.copy(setup["energy"])
        test_energy = apply_local_constant_potential(
            test_energy, potential, setup["gate_indices"]
        )
        edge = find_edge(test_energy, setup["E_F"], setup["U_fluc"], setup["bulk"])
        edge_length = calc_edge_length(edge)
        scale_factor = edge_length / initial_edge_length
        scale_factors.append(scale_factor)
    
    return potentials, np.array(scale_factors), initial_edge_length


def demonstrate_lookup_table_approach(potentials, scale_factors, setup):
    """Demonstrate Miller903's lookup table approach."""
    print("\n=== Lookup Table Approach ===")
    
    # Define target scale factors
    target_scale_factors = np.array([0.95, 0.98, 1.01, 1.02])
    
    # Find corresponding potentials using lookup table
    found_potentials = find_gate_potential_for_scale_factor(
        target_scale_factors, scale_factors, potentials
    )
    
    print("Target scale factors:", target_scale_factors)
    print("Found potentials:    ", found_potentials)
    
    # Verify the results
    initial_edge = find_edge(setup["energy"], setup["E_F"], setup["U_fluc"], setup["bulk"])
    initial_edge_length = calc_edge_length(initial_edge)
    
    actual_scale_factors = []
    for potential in found_potentials:
        test_energy = np.copy(setup["energy"])
        test_energy = apply_local_constant_potential(
            test_energy, potential, setup["gate_indices"]
        )
        edge = find_edge(test_energy, setup["E_F"], setup["U_fluc"], setup["bulk"])
        edge_length = calc_edge_length(edge)
        scale_factor = edge_length / initial_edge_length
        actual_scale_factors.append(scale_factor)
    
    actual_scale_factors = np.array(actual_scale_factors)
    print("Actual scale factors:", actual_scale_factors)
    print("Errors:              ", np.abs(target_scale_factors - actual_scale_factors))


def demonstrate_optimization_approach(setup):
    """Demonstrate the iterative optimization approach."""
    print("\n=== Iterative Optimization Approach ===")
    
    # Calculate initial edge length
    initial_edge = find_edge(setup["energy"], setup["E_F"], setup["U_fluc"], setup["bulk"])
    initial_edge_length = calc_edge_length(initial_edge)
    
    # Define a time-dependent scale factor a(t) = cosh²(st) as mentioned in the issue
    t_0 = calc_time_unit(setup["E_0"])
    print(f"Time unit t_0 = {t_0:.2e} s")
    
    s = 0.1  # Parameter for the scale factor function
    time_points = np.linspace(0, 1, 5) * t_0  # 5 time points
    target_scale_factors = np.cosh(s * time_points / t_0)**2
    
    print(f"Target scale factors: {target_scale_factors}")
    
    # Find gate potentials for each target scale factor
    optimized_potentials = []
    actual_scale_factors = []
    
    for i, target in enumerate(target_scale_factors):
        print(f"  Optimizing for scale factor {target:.4f}...")
        
        try:
            potential = optimize_gate_potential_for_scale_factor(
                target,
                setup["energy"],
                setup["E_F"],
                setup["U_fluc"],
                setup["bulk"],
                setup["gate_indices"],
                initial_edge_length,
                potential_range=(-setup["E_F"]/2, setup["E_F"]/2),
                tolerance=1e-2,
                max_iterations=50,
            )
            
            # Verify the result
            test_energy = np.copy(setup["energy"])
            test_energy = apply_local_constant_potential(
                test_energy, potential, setup["gate_indices"]
            )
            edge = find_edge(test_energy, setup["E_F"], setup["U_fluc"], setup["bulk"])
            edge_length = calc_edge_length(edge)
            actual_scale_factor = edge_length / initial_edge_length
            
            optimized_potentials.append(potential)
            actual_scale_factors.append(actual_scale_factor)
            
            print(f"    Found potential: {potential:.4f}")
            print(f"    Actual scale factor: {actual_scale_factor:.4f}")
            
        except ValueError as e:
            print(f"    Optimization failed: {e}")
            optimized_potentials.append(np.nan)
            actual_scale_factors.append(np.nan)
    
    return time_points, target_scale_factors, optimized_potentials, actual_scale_factors


def plot_results(potentials, scale_factors, time_points, target_scale_factors, 
                optimized_potentials, actual_scale_factors):
    """Plot the results."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot reference data
    ax1.plot(potentials, scale_factors, 'b-', linewidth=2, label='Reference data')
    ax1.set_xlabel('Gate Potential')
    ax1.set_ylabel('Scale Factor')
    ax1.set_title('Scale Factor vs Gate Potential\n(Reference Data)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot optimization results
    valid_indices = ~np.isnan(optimized_potentials)
    if np.any(valid_indices):
        ax2.plot(time_points[valid_indices], target_scale_factors[valid_indices], 
                'ro-', linewidth=2, markersize=8, label='Target')
        ax2.plot(time_points[valid_indices], np.array(actual_scale_factors)[valid_indices], 
                'go-', linewidth=2, markersize=8, label='Achieved')
    
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Scale Factor')
    ax2.set_title('Target vs Achieved Scale Factors\n(Optimization Results)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('inverse_gate_potential_results.png', dpi=150, bbox_inches='tight')
    print("\n=== Results saved to 'inverse_gate_potential_results.png' ===")


def main():
    """Main demonstration function."""
    print("=== Inverse Gate Potential Algorithm Demonstration ===")
    print("This demonstrates the algorithm to find gate potentials")
    print("that produce desired scale factors.\n")
    
    # Setup simulation
    setup = setup_simulation()
    
    # Generate reference data
    potentials, scale_factors, initial_edge_length = generate_reference_data(setup)
    
    # Demonstrate lookup table approach
    demonstrate_lookup_table_approach(potentials, scale_factors, setup)
    
    # Demonstrate optimization approach
    time_points, target_scale_factors, optimized_potentials, actual_scale_factors = \
        demonstrate_optimization_approach(setup)
    
    # Plot results
    plot_results(potentials, scale_factors, time_points, target_scale_factors, 
                optimized_potentials, actual_scale_factors)
    
    print("\n=== Summary ===")
    print("1. Generated reference data relating gate potential to scale factor")
    print("2. Demonstrated lookup table approach for finding gate potentials")
    print("3. Demonstrated iterative optimization for arbitrary scale factors")
    print("4. Successfully implemented F: U_gate(t) = F[a(t)] function")


if __name__ == "__main__":
    main()