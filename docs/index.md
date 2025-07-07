# edgecraft

![simple_sample](res/simple_sample.gif)

## Overview

**edgecraft** is a Quantum Hall edge deformation simulator designed for analog universe experiments. It provides a comprehensive framework for modeling edge states, confinement potentials, and disorder effects in quantum Hall systems.

## Features

- **Quantum Hall Physics**: Complete implementation of Landau levels and edge states
- **Realistic Material Parameters**: Optimized for GaAs heterostructures
- **Edge Deformation Modeling**: Track edge evolution under gate voltage changes
- **Disorder and Thermal Effects**: Include realistic broadening mechanisms
- **Analog Universe Applications**: Model curved spacetime effects through edge deformation

## Quick Start

### Installation

- Python: ^3.10

1. Download the repository as a zipped file and decompress the file.
2. Move to the root directory and run the installation code.
   ```sh
   $ python -m pip install .
   ```

### Development Setup

1. Install Python 3.10.x.
2. Install [poetry](https://python-poetry.org/docs/).
3. Install the dependencies:
    ```sh
    $ poetry install
    ```

## Documentation Structure

- **[Theoretical Principles](principles.md)**: Comprehensive mathematical framework and physics background
- **[API Reference](api.md)**: Detailed function documentation
- **Examples**: See the `examples/` directory for simulation examples

## Key Concepts

The simulator is built around several core physics concepts:

- **Landau Levels**: Quantized energy levels in magnetic fields
- **Edge States**: Chiral conducting states at sample boundaries  
- **Confinement Potential**: Electrostatic edge confinement modeling
- **Unit Systems**: Rescaled coordinates using magnetic length
- **Edge Finding**: Algorithm to identify and track edge positions

For detailed mathematical formulations, see the [Theoretical Principles](principles.md) section.
