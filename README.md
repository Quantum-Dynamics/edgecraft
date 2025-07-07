# edgecraft

![simple_sample](./docs/res/simple_sample.gif)

EdgeCraft is a Quantum Hall edge deformation simulator for analog universe experiments.

## Installing

- Python: ^3.10

### Installation from source

1. Download the repository as a zipped file and decompress the file.
2. Move to the root directory and run the installation code.
   ```sh
   $ python -m pip install .
   ```

### Installation from GitHub

```sh
$ python -m pip install git+https://github.com/Quantum-Dynamics/edgecraft@main
```

## Usage

EdgeCraft provides a command-line interface for running simulations:

```sh
$ python -m edgecraft run [config_file]
```

### Example usage

1. Create a configuration file (see `example_config.py` for reference):

```python
from edgecraft.config import EdgeCraftConfig

config = EdgeCraftConfig(
    # Physical constants
    n=1e15,                     # electron density in m^-2
    T=40e-3,                    # temperature in K
    M=20,                       # magnetic length units
    
    # Simulation parameters
    frames=101,                 # number of simulation frames
    E_gate_min_factor=0.0,      # min gate energy as factor of E_F
    E_gate_max_factor=1.0,      # max gate energy as factor of E_F
    
    # Output parameters
    output_edge_lengths="edge_lengths.npy",
    output_gate_potential="gate_potential.npy",
)
```

2. Run the simulation:

```sh
$ python -m edgecraft run my_config.py
```

3. Optionally specify an output directory:

```sh
$ python -m edgecraft run my_config.py --output-dir ./results
```

The simulation will generate two NumPy files:
- `edge_lengths.npy`: Edge lengths for each simulation frame
- `gate_potential.npy`: Gate potential values for each frame

### Command-line options

- `--output-dir, -o`: Specify output directory for results (default: current directory)
- `--help`: Show help message

## Setup for development

1. Install Python 3.10.x.
2. Install [poetry](https://python-poetry.org/docs/).
3. Install the dependencies:
    ```sh
    $ poetry install
    ```
