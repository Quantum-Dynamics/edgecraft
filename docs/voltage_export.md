# Voltage File Export for Scale Factor Control

This module provides functionality to export voltage files that reproduce given scale factors in real experiments. The workflow involves calculating the required effective potential from desired scale factors and converting it to actual voltages using a user-defined conversion function.

## Overview

The voltage export functionality enables you to:

1. **Define desired scale factor profiles** over time
2. **Calculate required effective potentials** using simulation data
3. **Convert to actual voltages** using sample-specific conversion functions  
4. **Export time and voltage files** in text format for experimental use

## Key Functions

### `calc_effective_potential_from_scale_factor(target_scale_factors, edge_length_vs_potential_data, init_length)`

Calculates the effective potential required to achieve target scale factors.

**Parameters:**
- `target_scale_factors` (np.ndarray): Desired scale factor values
- `edge_length_vs_potential_data` (tuple): Tuple of (gate_potentials, edge_lengths) arrays from simulation
- `init_length` (float): Initial edge length for scale factor calculation

**Returns:**
- `np.ndarray`: Effective potential values that produce the target scale factors

### `generate_time_array(total_time_ns, time_step_ns)`

Generates a time array for voltage waveform export.

**Parameters:**
- `total_time_ns` (float): Total time duration in nanoseconds
- `time_step_ns` (float): Time step size in nanoseconds

**Returns:**
- `np.ndarray`: Time array in nanoseconds

### `export_voltage_waveform(time_ns, effective_potential, convert_to_voltage_func, time_filename, voltage_filename)`

Exports time and voltage arrays to text files for experimental use.

**Parameters:**
- `time_ns` (np.ndarray): Time array in nanoseconds
- `effective_potential` (np.ndarray): Effective potential array
- `convert_to_voltage_func`: Function that converts effective potential to voltage
- `time_filename` (str): Filename for time data (default: "time_ns.txt")
- `voltage_filename` (str): Filename for voltage data (default: "waveform_V.txt")

## Usage Example

```python
import numpy as np
from edgecraft import (
    calc_effective_potential_from_scale_factor,
    generate_time_array,
    export_voltage_waveform,
)

# 1. Load simulation data (gate potential vs edge length relationship)
gate_potentials = np.load("gate_potential.npy")  # From simulation
edge_lengths = np.load("edge_lengths.npy")      # From simulation
init_length = edge_lengths[0]

# 2. Define desired scale factor profile
target_scale_factors = np.array([1.0, 1.2, 1.4, 1.2, 1.0])  # Example profile

# 3. Calculate required effective potential
required_potential = calc_effective_potential_from_scale_factor(
    target_scale_factors,
    (gate_potentials, edge_lengths),
    init_length
)

# 4. Generate time array
time_ns = generate_time_array(total_time_ns=50.0, time_step_ns=1.0)

# 5. Define voltage conversion function (sample-specific)
def convert_to_voltage(eff_potential: np.ndarray) -> np.ndarray:
    """Convert effective potential to sample surface voltage."""
    # This function depends on your specific sample and setup
    voltage_scale = 0.2  # V per unit effective potential
    voltage_offset = 0.0  # V
    return eff_potential * voltage_scale + voltage_offset

# 6. Export voltage waveform
export_voltage_waveform(
    time_ns,
    required_potential,
    convert_to_voltage,
    time_filename="experiment_time_ns.txt",
    voltage_filename="experiment_waveform_V.txt"
)
```

## Voltage Conversion Function

The voltage conversion function is **sample-specific** and must be provided by the user. This function converts the effective potential calculated from the simulation to the actual voltage that should be applied to the sample surface.

### Example Conversion Functions

**Linear conversion:**
```python
def convert_to_voltage_linear(eff_potential: np.ndarray) -> np.ndarray:
    voltage_scale = 0.1  # V per unit effective potential
    voltage_offset = 0.0  # V
    return eff_potential * voltage_scale + voltage_offset
```

**Nonlinear conversion:**
```python
def convert_to_voltage_nonlinear(eff_potential: np.ndarray) -> np.ndarray:
    # Example: square root relationship
    return 0.2 * np.sqrt(np.abs(eff_potential)) * np.sign(eff_potential)
```

**Lookup table conversion:**
```python
def convert_to_voltage_lookup(eff_potential: np.ndarray) -> np.ndarray:
    # Use measured calibration data
    calibration_potential = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    calibration_voltage = np.array([0.0, 0.05, 0.12, 0.18, 0.25])
    return np.interp(eff_potential, calibration_potential, calibration_voltage)
```

## Output File Format

The exported files use the format specified in the issue:

- **Time file** (`*_time_ns.txt`): One time value per line in nanoseconds
- **Voltage file** (`*_waveform_V.txt`): One voltage value per line in Volts

Both files use `numpy.savetxt` with 6 decimal places precision.

## Examples

See the following example scripts:

- `examples/voltage_export_example.py`: Comprehensive demonstration with visualization
- `examples/realistic_voltage_example.py`: Example matching the voltage pattern from the issue image
- `tests/test_voltage_export.py`: Complete test suite

## Error Handling

The functions include error checking for common issues:

- Scale factor arrays with zero values
- Negative initial lengths
- Mismatched array lengths between time and potential arrays
- Invalid parameter ranges

## Integration with Existing Code

The new functions integrate seamlessly with the existing `edgecraft` workflow:

1. Use existing simulation functions to generate edge length vs gate potential data
2. Use `calc_scale_factor()` to analyze the relationship
3. Use the new functions to reverse the process and export voltage files
4. Apply the exported voltages in experiments to reproduce desired scale factors