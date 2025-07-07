#!/usr/bin/env python3
"""
Example script demonstrating how to export voltage files that reproduce given scale factors.

This example shows how to:
1. Load edge length vs. gate potential data from simulation
2. Define a desired scale factor profile
3. Calculate the required effective potential
4. Convert to voltage using a user-defined conversion function  
5. Export time and voltage files for experimental use
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add the parent directory to Python path to import edgecraft
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from edgecraft import (
    calc_scale_factor,
    calc_effective_potential_from_scale_factor,
    generate_time_array,
    export_voltage_waveform,
)


def create_sample_data():
    """Create sample edge length vs gate potential data for demonstration."""
    # Simulate some realistic data: gate potential vs edge length relationship
    gate_potentials = np.linspace(0, 1.0, 101)  # Effective potential range
    # Simulate edge lengths that increase with gate potential
    edge_lengths = 150 + 50 * np.tanh(2 * gate_potentials)  # Saturating growth
    return gate_potentials, edge_lengths


def convert_to_voltage(eff_potential: np.ndarray) -> np.ndarray:
    """
    User-defined function to convert effective potential to sample surface voltage.
    
    This function depends on the specific sample and experimental setup.
    Here we provide a simple linear conversion as an example.
    
    Args:
        eff_potential (np.ndarray): Effective potential values
        
    Returns:
        np.ndarray: Voltage values in Volts
    """
    # Example conversion: linear scaling with offset
    # In practice, this would be determined by sample characterization
    voltage_scale = 0.2  # V per unit effective potential
    voltage_offset = 0.0  # V
    
    return eff_potential * voltage_scale + voltage_offset


def create_periodic_scale_factor_profile(n_periods: int = 8, samples_per_period: int = 11) -> np.ndarray:
    """
    Create a periodic scale factor profile similar to the one shown in the issue.
    
    Args:
        n_periods (int): Number of periods in the waveform
        samples_per_period (int): Number of samples per period
        
    Returns:
        np.ndarray: Scale factor values
    """
    total_samples = n_periods * samples_per_period
    
    # Create a step-like periodic waveform
    scale_factors = np.zeros(total_samples)
    
    for i in range(n_periods):
        start_idx = i * samples_per_period
        end_idx = start_idx + samples_per_period
        
        # Alternate between high and low scale factors
        if i % 2 == 0:
            scale_factors[start_idx:end_idx] = 1.5  # High state
        else:
            scale_factors[start_idx:end_idx] = 0.5  # Low state
    
    return scale_factors


def main():
    """Main function demonstrating voltage export workflow."""
    print("Voltage Export Example")
    print("=" * 50)
    
    # Step 1: Create or load edge length vs gate potential data
    print("1. Creating sample edge length vs gate potential data...")
    gate_potentials, edge_lengths = create_sample_data()
    
    # Calculate scale factors from the simulation data
    init_length = edge_lengths[0]  # Use first edge length as reference
    scale_factors_sim = calc_scale_factor(edge_lengths, init_length)
    
    print(f"   - Gate potential range: {gate_potentials[0]:.3f} to {gate_potentials[-1]:.3f}")
    print(f"   - Edge length range: {edge_lengths[0]:.1f} to {edge_lengths[-1]:.1f}")
    print(f"   - Scale factor range: {scale_factors_sim[0]:.3f} to {scale_factors_sim[-1]:.3f}")
    
    # Step 2: Define desired scale factor profile
    print("\n2. Creating desired scale factor profile...")
    target_scale_factors = create_periodic_scale_factor_profile()
    
    print(f"   - Target scale factors: {len(target_scale_factors)} points")
    print(f"   - Scale factor range: {target_scale_factors.min():.3f} to {target_scale_factors.max():.3f}")
    
    # Step 3: Calculate required effective potential
    print("\n3. Calculating required effective potential...")
    required_potential = calc_effective_potential_from_scale_factor(
        target_scale_factors,
        (gate_potentials, edge_lengths),
        init_length
    )
    
    print(f"   - Required potential range: {required_potential.min():.3f} to {required_potential.max():.3f}")
    
    # Step 4: Generate time array
    print("\n4. Generating time array...")
    time_per_sample_ns = 1.0  # 1 ns per sample
    total_time_ns = len(target_scale_factors) * time_per_sample_ns
    time_ns = generate_time_array(total_time_ns - time_per_sample_ns, time_per_sample_ns)
    
    print(f"   - Total time: {total_time_ns:.1f} ns")
    print(f"   - Time step: {time_per_sample_ns:.1f} ns")
    print(f"   - Number of time points: {len(time_ns)}")
    
    # Step 5: Export voltage waveform
    print("\n5. Exporting voltage waveform...")
    export_voltage_waveform(
        time_ns,
        required_potential,
        convert_to_voltage,
        time_filename="example_time_ns.txt",
        voltage_filename="example_waveform_V.txt"
    )
    
    print("   ✓ Exported example_time_ns.txt")
    print("   ✓ Exported example_waveform_V.txt")
    
    # Step 6: Create visualization
    print("\n6. Creating visualization...")
    
    # Convert to voltage for plotting
    voltage_V = convert_to_voltage(required_potential)
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
    
    # Plot 1: Target scale factors
    ax1.step(time_ns, target_scale_factors, where='post', linewidth=2)
    ax1.set_ylabel('Scale Factor')
    ax1.set_title('Target Scale Factor Profile')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Required effective potential
    ax2.step(time_ns, required_potential, where='post', linewidth=2, color='orange')
    ax2.set_ylabel('Effective Potential')
    ax2.set_title('Required Effective Potential')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Output voltage waveform
    ax3.step(time_ns, voltage_V, where='post', linewidth=2, color='red')
    ax3.set_xlabel('Time (ns)')
    ax3.set_ylabel('Voltage (V)')
    ax3.set_title('Output Voltage Waveform')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('voltage_export_example.png', dpi=150, bbox_inches='tight')
    print("   ✓ Saved voltage_export_example.png")
    
    # Display some statistics
    print("\n7. Summary:")
    print(f"   - Voltage range: {voltage_V.min():.3f} V to {voltage_V.max():.3f} V")
    print(f"   - Average voltage: {voltage_V.mean():.3f} V")
    print(f"   - Voltage peak-to-peak: {voltage_V.max() - voltage_V.min():.3f} V")


if __name__ == "__main__":
    main()