#!/usr/bin/env python3
"""
Test script for the voltage export functionality.
"""

import numpy as np
import sys
from pathlib import Path

# Add the parent directory to Python path to import edgecraft
sys.path.insert(0, str(Path(__file__).parent.parent))

from edgecraft import (
    calc_scale_factor,
    calc_effective_potential_from_scale_factor,
    generate_time_array,
    export_voltage_waveform,
)


def test_calc_scale_factor():
    """Test the calc_scale_factor function."""
    edge_lengths = np.array([100, 120, 140, 160])
    init_length = 100.0
    
    expected = np.array([1.0, 1.2, 1.4, 1.6])
    result = calc_scale_factor(edge_lengths, init_length)
    
    np.testing.assert_array_almost_equal(result, expected)
    print("✓ calc_scale_factor test passed")


def test_calc_effective_potential_from_scale_factor():
    """Test the calc_effective_potential_from_scale_factor function."""
    # Create test data
    gate_potentials = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    edge_lengths = np.array([100, 110, 120, 130, 140])
    init_length = 100.0
    
    # Target scale factors
    target_scale_factors = np.array([1.1, 1.3])  # Corresponding to edge lengths 110, 130
    
    result = calc_effective_potential_from_scale_factor(
        target_scale_factors,
        (gate_potentials, edge_lengths),
        init_length
    )
    
    expected = np.array([0.25, 0.75])  # Should interpolate to these potentials
    np.testing.assert_array_almost_equal(result, expected)
    print("✓ calc_effective_potential_from_scale_factor test passed")


def test_generate_time_array():
    """Test the generate_time_array function."""
    total_time_ns = 10.0
    time_step_ns = 1.0
    
    result = generate_time_array(total_time_ns, time_step_ns)
    expected = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    
    np.testing.assert_array_almost_equal(result, expected)
    print("✓ generate_time_array test passed")


def test_export_voltage_waveform():
    """Test the export_voltage_waveform function."""
    time_ns = np.array([0.0, 1.0, 2.0])
    effective_potential = np.array([0.0, 0.5, 1.0])
    
    def convert_to_voltage(eff_potential):
        return eff_potential * 0.1  # Simple linear conversion
    
    # Export to temporary files
    export_voltage_waveform(
        time_ns,
        effective_potential,
        convert_to_voltage,
        time_filename="/tmp/test_time.txt",
        voltage_filename="/tmp/test_voltage.txt"
    )
    
    # Load and verify
    time_loaded = np.loadtxt("/tmp/test_time.txt")
    voltage_loaded = np.loadtxt("/tmp/test_voltage.txt")
    
    np.testing.assert_array_almost_equal(time_loaded, time_ns)
    np.testing.assert_array_almost_equal(voltage_loaded, np.array([0.0, 0.05, 0.1]))
    print("✓ export_voltage_waveform test passed")


def test_edge_cases():
    """Test edge cases and error conditions."""
    # Test calc_scale_factor with zero edge lengths
    try:
        calc_scale_factor(np.array([0, 1, 2]), 1.0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Edge lengths cannot be zero" in str(e)
        print("✓ calc_scale_factor zero edge length error test passed")
    
    # Test calc_scale_factor with negative initial length
    try:
        calc_scale_factor(np.array([1, 2, 3]), -1.0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Initial length must be positive" in str(e)
        print("✓ calc_scale_factor negative initial length error test passed")
    
    # Test export_voltage_waveform with mismatched array lengths
    try:
        time_ns = np.array([0.0, 1.0])
        effective_potential = np.array([0.0, 0.5, 1.0])  # Different length
        
        def convert_to_voltage(eff_potential):
            return eff_potential * 0.1
        
        export_voltage_waveform(
            time_ns,
            effective_potential,
            convert_to_voltage,
            time_filename="/tmp/test_time_err.txt",
            voltage_filename="/tmp/test_voltage_err.txt"
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "must have the same length" in str(e)
        print("✓ export_voltage_waveform mismatched length error test passed")


def run_all_tests():
    """Run all tests."""
    print("Running voltage export functionality tests...")
    print("=" * 50)
    
    test_calc_scale_factor()
    test_calc_effective_potential_from_scale_factor()
    test_generate_time_array()
    test_export_voltage_waveform()
    test_edge_cases()
    
    print("=" * 50)
    print("All tests passed! ✅")


if __name__ == "__main__":
    run_all_tests()