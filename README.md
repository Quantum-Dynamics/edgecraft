# edgecraft

![simple_sample](./docs/res/simple_sample.gif)

## Installing

- Python: ^3.10

1. Download the repository as a zipped file and decompress the file.
2. Move to the root directory and run the installation code.
   ```sh
   $ python -m pip install .
   ```

## Setup for development

1. Install Python 3.10.x.
2. Install [poetry](https://python-poetry.org/docs/).
3. Install the dependencies:
    ```sh
    $ poetry install
    ```
## Running
   You run the program as follows
   ```sh
    $ python click_application.py your_config_file.py
   ```
   This will run the simulation.

## The simulation
   It will output first several graphs of the potential and edge velocities.
   Then it will generate an animation PoC.gif of the edge position, potential profile and edge velocity.
   Then it will compute the scale factor calculated from your gate potential.
   Then it will calculate what potential is reuqired to get the desired scale factor.
   It outputs the potential to the voltage.txt file
   Several other results are outputted to the results.txt file

## Config file
   Your config file dictates many of the parameters of the simulation. It must be a python file locally accesibly to click_application.py (so in the same folder). See sample_config.py for an example.

   It needs to contain these variables for the simulation to use:
   - space_matrix (np.ndarray): 2D array of points. Represents the space your chip occupies.
   - etchings (np.ndarray): a 3D array. Elements of which are matricies of the same shape as space_matrix with a 1 if it is included in the etching and a 0 if it isn't
   - etching_potentials (np.ndarray): a 1D array. Each entry here corresponds to the strength of the potential induced by the corresponding etching. Should have the same first dimension as etchings
   - boundary_indices (np.ndarray): a 2d array. Contains coorinates of the edge of the chip
   - bulk_indices (np.ndarray): a 2D array. Contains coorinates of the bulk of the chip (that's not vaccum or boundary)
   - bulk (np.ndarray): a 2D array of the same shape as space_matrix. Contains a 1 where the coordinate is in the bulk and a 0 elsewhere.
   - desired_scale_factor(np.ndarray): 1D array of the desired scale factor at various points in time. The simulation will output the voltage required for the desired scale factor at each corresponding point in time.
   - gate (np.ndarray): a 2D array of the relative gate potential at each point in space. 0 everywhere the gate isn't applied
   - gate_potential (np.ndarray): a 1D array of the gate potential for each time step to multiply gate by.
   - time_scale (float): time between entries in gate_potential.
   - start_index (float): index to start an electron from for calculating its path.
   - gate_start (int): y coordinate of the start of the gate. gate should span indices from gate_start to gate_end.
   - gate_end (int): y coordinate of the end of the gate. gate should span indices from gate_start to gate_end.
   - convert_to_voltage (func): a function to convert gate potential to voltage applied.
