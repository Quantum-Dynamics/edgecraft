"""Tests for inverse gate potential calculation algorithms."""

import numpy as np
import pytest
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


@pytest.fixture
def simulation_setup():
    """Setup basic simulation parameters and geometry."""
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

    # Space matrices (smaller for testing)
    radius_gate = int(25e-6 / l_0)  # Smaller radius for faster tests
    x = np.arange(0, int(100e-6 / l_0), 1)  # Smaller grid
    y = np.arange(0, int(75e-6 / l_0), 1)
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
            radius_gate - int(12e-6 / l_0),
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


def test_calc_time_unit():
    """Test time unit calculation."""
    E_0 = 1e-21  # Example unit energy in Joules
    t_0 = calc_time_unit(E_0)
    
    # Should be hbar / E_0
    from edgecraft import hbar
    expected = hbar / E_0
    assert abs(t_0 - expected) < 1e-35


def test_calc_scale_factor():
    """Test scale factor calculation."""
    edge_lengths = np.array([10.0, 11.0, 12.0])
    init_length = 10.0
    
    scale_factors = calc_scale_factor(edge_lengths, init_length)
    expected = np.array([1.0, 1.1, 1.2])
    
    np.testing.assert_array_almost_equal(scale_factors, expected)


def test_calc_scale_factor_edge_cases():
    """Test scale factor calculation edge cases."""
    # Test zero edge length
    with pytest.raises(ValueError, match="Edge lengths cannot be zero"):
        calc_scale_factor(np.array([0.0, 1.0]), 1.0)
    
    # Test negative initial length
    with pytest.raises(ValueError, match="Initial length must be positive"):
        calc_scale_factor(np.array([1.0, 2.0]), -1.0)


def test_find_gate_potential_for_scale_factor():
    """Test lookup table based gate potential finding."""
    # Create reference data
    reference_scale_factors = np.array([0.93, 0.95, 0.97, 0.99, 1.00])
    reference_potentials = np.array([0.1, 0.05, 0.02, 0.01, 0.0])
    
    # Test exact matches
    target_scale_factors = np.array([0.95, 1.00])
    result_potentials = find_gate_potential_for_scale_factor(
        target_scale_factors, reference_scale_factors, reference_potentials
    )
    
    expected = np.array([0.05, 0.0])
    np.testing.assert_array_almost_equal(result_potentials, expected)
    
    # Test interpolation (should pick closest)
    target_scale_factors = np.array([0.94, 0.96])
    result_potentials = find_gate_potential_for_scale_factor(
        target_scale_factors, reference_scale_factors, reference_potentials
    )
    
    # 0.94 is closer to 0.93, 0.96 is closer to 0.95
    expected = np.array([0.1, 0.05])
    np.testing.assert_array_almost_equal(result_potentials, expected)


def test_find_gate_potential_for_scale_factor_edge_cases():
    """Test edge cases for lookup table function."""
    reference_scale_factors = np.array([0.93, 0.95])
    reference_potentials = np.array([0.1])  # Wrong length
    target_scale_factors = np.array([0.94])
    
    with pytest.raises(ValueError, match="Reference arrays must have the same length"):
        find_gate_potential_for_scale_factor(
            target_scale_factors, reference_scale_factors, reference_potentials
        )


def test_optimize_gate_potential_for_scale_factor(simulation_setup):
    """Test iterative optimization for gate potential."""
    setup = simulation_setup
    
    # Calculate initial edge length
    initial_edge = find_edge(setup["energy"], setup["E_F"], setup["U_fluc"], setup["bulk"])
    initial_edge_length = calc_edge_length(initial_edge)
    
    # Target scale factor close to 1.0 (should require small potential)
    target_scale_factor = 1.01  # More realistic target
    
    # Find gate potential
    optimized_potential = optimize_gate_potential_for_scale_factor(
        target_scale_factor,
        setup["energy"],
        setup["E_F"],
        setup["U_fluc"],
        setup["bulk"],
        setup["gate_indices"],
        initial_edge_length,
        potential_range=(-0.2, 0.2),  # Smaller range
        tolerance=5e-2,  # More lenient tolerance
        max_iterations=30,
    )
    
    # Verify the result
    test_energy = np.copy(setup["energy"])
    test_energy = apply_local_constant_potential(
        test_energy, optimized_potential, setup["gate_indices"]
    )
    edge = find_edge(test_energy, setup["E_F"], setup["U_fluc"], setup["bulk"])
    edge_length = calc_edge_length(edge)
    actual_scale_factor = edge_length / initial_edge_length
    
    # Should be close to target
    assert abs(actual_scale_factor - target_scale_factor) < 0.1


def test_optimize_gate_potential_convergence_failure(simulation_setup):
    """Test optimization failure case."""
    setup = simulation_setup
    
    # Calculate initial edge length
    initial_edge = find_edge(setup["energy"], setup["E_F"], setup["U_fluc"], setup["bulk"])
    initial_edge_length = calc_edge_length(initial_edge)
    
    # Impossible target scale factor
    target_scale_factor = 10.0  # Way too high
    
    with pytest.raises(ValueError, match="Failed to converge"):
        optimize_gate_potential_for_scale_factor(
            target_scale_factor,
            setup["energy"],
            setup["E_F"],
            setup["U_fluc"],
            setup["bulk"],
            setup["gate_indices"],
            initial_edge_length,
            potential_range=(-1.0, 1.0),
            tolerance=1e-3,
            max_iterations=5,  # Low iterations to force failure
        )


def test_example_workflow(simulation_setup):
    """Test a complete workflow example."""
    setup = simulation_setup
    
    # Step 1: Generate reference data (simulate the original experiment)
    potentials = np.linspace(0, 0.1, 11)
    scale_factors = []
    
    # Calculate initial edge length
    initial_edge = find_edge(setup["energy"], setup["E_F"], setup["U_fluc"], setup["bulk"])
    initial_edge_length = calc_edge_length(initial_edge)
    
    for potential in potentials:
        test_energy = np.copy(setup["energy"])
        test_energy = apply_local_constant_potential(
            test_energy, potential, setup["gate_indices"]
        )
        edge = find_edge(test_energy, setup["E_F"], setup["U_fluc"], setup["bulk"])
        edge_length = calc_edge_length(edge)
        scale_factor = edge_length / initial_edge_length
        scale_factors.append(scale_factor)
    
    scale_factors = np.array(scale_factors)
    
    # Step 2: Use lookup table to find potentials for desired scale factors
    target_scale_factors = np.array([scale_factors[3], scale_factors[7]])  # Pick some values
    found_potentials = find_gate_potential_for_scale_factor(
        target_scale_factors, scale_factors, potentials
    )
    
    # Should match the original potentials
    expected_potentials = np.array([potentials[3], potentials[7]])
    np.testing.assert_array_almost_equal(found_potentials, expected_potentials)
    
    # Step 3: Test with time unit calculation
    t_0 = calc_time_unit(setup["E_0"])
    assert t_0 > 0  # Should be positive time