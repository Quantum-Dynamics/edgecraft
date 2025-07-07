#!/usr/bin/env python3
"""
Example script that creates a voltage waveform matching the pattern shown in the issue.

This example demonstrates creating a periodic voltage waveform that oscillates
between approximately -0.1V to +0.1V, similar to the reference image provided.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Add the parent directory to Python path to import edgecraft
sys.path.insert(0, str(Path(__file__).parent.parent))

from edgecraft import (
    calc_effective_potential_from_scale_factor,
    generate_time_array,
    export_voltage_waveform,
)


def convert_to_voltage_realistic(eff_potential: np.ndarray) -> np.ndarray:
    """
    Realistic voltage conversion function that maps effective potential to voltage.
    
    This function maps the effective potential range to approximately -0.1V to +0.1V
    to match the pattern shown in the issue image.
    
    Args:
        eff_potential (np.ndarray): Effective potential values (normalized 0-1)
        
    Returns:
        np.ndarray: Voltage values in Volts
    """
    # Map effective potential range [0, 1] to voltage range [-0.1, +0.1] V
    voltage_min = -0.1  # V
    voltage_max = 0.1   # V
    
    # Linear mapping: eff_potential=0 -> voltage_min, eff_potential=1 -> voltage_max
    return voltage_min + (voltage_max - voltage_min) * eff_potential


def create_realistic_scale_factor_profile(total_time_ns: float = 100.0, 
                                        period_ns: float = 12.5) -> tuple[np.ndarray, np.ndarray]:
    """
    Create a realistic scale factor profile that produces the voltage pattern 
    shown in the issue image.
    
    Args:
        total_time_ns (float): Total time duration in nanoseconds
        period_ns (float): Period of each voltage pulse in nanoseconds
        
    Returns:
        tuple: (time_array, scale_factor_array)
    """
    # Create time array with 0.1 ns resolution for smooth waveform
    time_step_ns = 0.1
    time_ns = generate_time_array(total_time_ns - time_step_ns, time_step_ns)
    
    # Create periodic scale factor profile
    # The scale factor oscillates between two values to create voltage pattern
    scale_factors = np.zeros_like(time_ns)
    
    for i, t in enumerate(time_ns):
        # Determine which period we're in
        t_in_period = t % period_ns
        
        if t_in_period < period_ns * 0.8:  # 80% of period at high value
            scale_factors[i] = 1.2  # High scale factor -> high voltage
        else:  # 20% of period at low value  
            scale_factors[i] = 0.8  # Low scale factor -> low voltage
    
    return time_ns, scale_factors


def main():
    """Main function to create realistic voltage export example."""
    print("Realistic Voltage Export Example")
    print("=" * 50)
    
    # Step 1: Create synthetic edge length vs gate potential relationship
    print("1. Creating synthetic calibration data...")
    gate_potentials = np.linspace(0, 1, 101)  # Normalized effective potential
    # Simulate edge lengths with realistic saturation behavior
    edge_lengths = 150 + 50 * np.tanh(3 * gate_potentials)  # 150-200 range
    init_length = edge_lengths[0]
    
    print(f"   - Effective potential range: {gate_potentials[0]:.1f} to {gate_potentials[-1]:.1f}")
    print(f"   - Edge length range: {edge_lengths[0]:.1f} to {edge_lengths[-1]:.1f}")
    
    # Step 2: Create realistic scale factor profile
    print("\n2. Creating realistic scale factor profile...")
    time_ns, target_scale_factors = create_realistic_scale_factor_profile()
    
    print(f"   - Total time: {time_ns[-1]:.1f} ns")
    print(f"   - Time resolution: {time_ns[1] - time_ns[0]:.1f} ns")
    print(f"   - Scale factor range: {target_scale_factors.min():.3f} to {target_scale_factors.max():.3f}")
    
    # Step 3: Calculate required effective potential
    print("\n3. Converting scale factors to effective potentials...")
    required_potential = calc_effective_potential_from_scale_factor(
        target_scale_factors,
        (gate_potentials, edge_lengths),
        init_length
    )
    
    print(f"   - Effective potential range: {required_potential.min():.3f} to {required_potential.max():.3f}")
    
    # Step 4: Export voltage waveform
    print("\n4. Exporting realistic voltage waveform...")
    export_voltage_waveform(
        time_ns,
        required_potential,
        convert_to_voltage_realistic,
        time_filename="realistic_time_ns.txt",
        voltage_filename="realistic_waveform_V.txt"
    )
    
    print("   ✓ Exported realistic_time_ns.txt")
    print("   ✓ Exported realistic_waveform_V.txt")
    
    # Step 5: Create visualization
    print("\n5. Creating visualization...")
    
    voltage_V = convert_to_voltage_realistic(required_potential)
    
    # Create a plot similar to the issue image
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot voltage vs time
    ax.plot(time_ns, voltage_V, linewidth=2, color='blue')
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Voltage (V)')
    ax.set_title('Realistic Voltage Waveform for Scale Factor Control')
    ax.grid(True, alpha=0.3)
    
    # Set y-axis limits to match the issue image
    ax.set_ylim(-0.12, 0.12)
    
    # Add horizontal lines at key voltage levels
    ax.axhline(y=0.1, color='red', linestyle='--', alpha=0.5, label='±0.1V')
    ax.axhline(y=-0.1, color='red', linestyle='--', alpha=0.5)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('realistic_voltage_waveform.png', dpi=150, bbox_inches='tight')
    print("   ✓ Saved realistic_voltage_waveform.png")
    
    # Step 6: Display statistics
    print("\n6. Waveform Statistics:")
    print(f"   - Voltage range: {voltage_V.min():.3f} V to {voltage_V.max():.3f} V")
    print(f"   - Peak-to-peak voltage: {voltage_V.max() - voltage_V.min():.3f} V")
    print(f"   - Number of data points: {len(voltage_V)}")
    print(f"   - High voltage level: {voltage_V.max():.3f} V")
    print(f"   - Low voltage level: {voltage_V.min():.3f} V")
    
    # Show a few sample data points
    print("\n7. Sample data points:")
    print("   Time (ns)    Voltage (V)")
    print("   ---------    -----------")
    for i in range(0, len(time_ns), len(time_ns)//10):
        print(f"   {time_ns[i]:8.1f}    {voltage_V[i]:10.6f}")


if __name__ == "__main__":
    main()