import numpy as np


def true_circle_in(
    Y: np.ndarray,
    X: np.ndarray,
    y0: float,
    x0: float,
    radius: float,
) -> np.ndarray:
    """
    Return a boolean mask indicating which points (X, Y) are inside a circle.

    Args:
        Y (np.ndarray): 2D array of y-coordinates.
        X (np.ndarray): 2D array of x-coordinates.
        y0 (float): y-coordinate of the circle center.
        x0 (float): x-coordinate of the circle center.
        radius (float): Radius of the circle.

    Returns:
        np.ndarray: Boolean array where True indicates the point is inside the
            circle.
    """
    return (X - x0)**2 + (Y - y0)**2 <= radius**2


def calc_confinement_potential_at(
    bulk_index: np.ndarray,
    boundary_indices: np.ndarray,
    dl: float = 1,
) -> float:
    """
    Calculate the confinement potential at a given bulk index due to all
    boundary indices.

    Args:
        bulk_index (np.ndarray): 1D array with the coordinates of the bulk
            point.
        boundary_indices (np.ndarray): 2D array of boundary point coordinates.
        dl (float, optional): Differential length element. Defaults to 1.

    Returns:
        float: The calculated confinement potential at the bulk index.
    """
    potential_density = (
        (bulk_index[0] - boundary_indices[:, 0] + 1e-20)**2 +
        (bulk_index[1] - boundary_indices[:, 1] + 1e-20)**2
    )**(-3 / 2) * dl
    return np.sum(potential_density)


def apply_confinement_potential(
    energy: np.ndarray,
    bulk_indices: np.ndarray,
    boundary_indices: np.ndarray,
    alpha: float,
    dl: float = 1,
) -> np.ndarray:
    """
    Add a constant potential value to specified indices in the energy array.

    Args:
        energy (np.ndarray): 2D array of energy values to modify.
        val (float): Value to add.
        space_indices (np.ndarray): 2D array of indices where the value should
            be added.

    Returns:
        np.ndarray: The modified energy array.
    """
    for bulk_index in bulk_indices:
        energy[bulk_index[0], bulk_index[1]] += calc_confinement_potential_at(
            bulk_index,
            boundary_indices,
            dl=dl,
        ) * alpha / 2
    return energy


def apply_local_constant_potential(
    energy: np.ndarray,
    val: float,
    space_indices: np.ndarray,
) -> np.ndarray:
    """
    Add a quantum Hall energy value to specified bulk indices in the energy
    array.

    Args:
        energy (np.ndarray): 2D array of energy values to modify.
        QH_energy (np.ndarray): Value to add at each bulk index.
        bulk_indices (np.ndarray): 2D array of bulk point coordinates.

    Returns:
        np.ndarray: The modified energy array.
    """
    for x_gate, y_gate in space_indices:
        energy[x_gate, y_gate] += val
    return energy


def apply_QH_energy(
    energy: np.ndarray,
    QH_energy: np.ndarray,
    bulk_indices: np.ndarray,
) -> np.ndarray:
    """
    Add a quantum Hall energy value to specified bulk indices in the energy
    array.

    Args:
        energy (np.ndarray): 2D array of energy values to modify.
        QH_energy (np.ndarray): Value to add at each bulk index.
        bulk_indices (np.ndarray): 2D array of bulk point coordinates.

    Returns:
        np.ndarray: The modified energy array.
    """
    for x_bulk, y_bulk in bulk_indices:
        energy[x_bulk, y_bulk] += QH_energy
    return energy


def find_edge(
    energy: np.ndarray,
    E_F: float,
    U_fluc: float,
    bulk: np.ndarray,
) -> np.ndarray:
    """
    Identify the edge region in the energy array based on Fermi energy and
    fluctuations.

    Args:
        energy (np.ndarray): 2D array of energy values.
        E_F (float): Fermi energy.
        U_fluc (float): Energy fluctuation parameter.
        bulk (np.ndarray): 2D array indicating bulk regions.

    Returns:
        np.ndarray: Boolean array where 1 indicates edge points.
    """
    edge = np.zeros_like(energy)
    upper = E_F - U_fluc <= energy
    lower = energy <= E_F + U_fluc
    edge[np.where(upper & lower)] = 1

    # TODO
    for index_x in range(len(edge)):
        if np.sum(edge[index_x, :]) != 0:
            continue

        for index_y, is_lower in enumerate(lower[index_x, :]):
            if is_lower and (bulk[index_x, index_y] == 1):
                edge[index_x, index_y] = 1
                break

    return edge


def calc_edge_length(
    edge: np.ndarray,
    pixel_x: int = 1,
    pixel_y: int = 1,
) -> float:
    """
    Calculate the total length of the edge by connecting edge points row by
    row.

    Args:
        edge (np.ndarray): 2D array where edge points are marked as 1.
        pixel_x (int, optional): Size of a pixel in the x-direction.
            Defaults to 1.
        pixel_y (int, optional): Size of a pixel in the y-direction.
            Defaults to 1.

    Returns:
        float: The calculated edge length.
    """
    # At each row, find all the pixels that are in the edge
    centeredge = np.zeros(len(edge))
    for y in range(len(edge)):
        if np.sum(edge[y]) == 0:
            raise ValueError(
                f"Row {y} has no edge points. Please check the edge array."
            )

        # Take the average of the edge points in this row
        for x in range(len(edge[y])):
            centeredge[y] += x * edge[y, x]
        centeredge[y] /= np.sum(edge[y])

    dx = (centeredge[:-1] - centeredge[1:]) * pixel_x
    dy = pixel_y

    # since there's 1 less tangent line than pixels
    return np.sqrt(dx**2 + dy**2).sum() + pixel_y


def calc_scale_factor(
    edge_lengths: np.ndarray,
    init_length: float,
) -> np.ndarray:
    """
    Calculate the scale factor to adjust the edge length to a target length.

    Args:
        edge_lengths (np.ndarray): Current lengths of the edges.
        init_length (float): Desired initial length for the edges. The value
            must be positive and non-zero.

    Returns:
        np.ndarray: The scale factors to apply.
    """
    if np.any(edge_lengths == 0):
        raise ValueError("Edge lengths cannot be zero.")
    if init_length <= 0:
        raise ValueError("Initial length must be positive and non-zero.")
    return edge_lengths / init_length


def calc_effective_potential_from_scale_factor(
    target_scale_factors: np.ndarray,
    edge_length_vs_potential_data: tuple[np.ndarray, np.ndarray],
    init_length: float,
) -> np.ndarray:
    """
    Calculate the effective potential required to achieve target scale factors.
    
    This function performs the inverse calculation: given desired scale factors,
    find the effective potential values that would produce those scale factors.
    
    Args:
        target_scale_factors (np.ndarray): Desired scale factor values.
        edge_length_vs_potential_data (tuple): Tuple of (gate_potentials, edge_lengths)
            arrays that define the relationship between potential and edge length.
        init_length (float): Initial edge length for scale factor calculation.
    
    Returns:
        np.ndarray: Effective potential values that produce the target scale factors.
    """
    gate_potentials, edge_lengths = edge_length_vs_potential_data
    
    # Convert target scale factors to target edge lengths
    target_edge_lengths = target_scale_factors * init_length
    
    # Interpolate to find required potentials
    effective_potentials = np.interp(target_edge_lengths, edge_lengths, gate_potentials)
    
    return effective_potentials


def generate_time_array(
    total_time_ns: float,
    time_step_ns: float,
) -> np.ndarray:
    """
    Generate a time array for voltage waveform export.
    
    Args:
        total_time_ns (float): Total time duration in nanoseconds.
        time_step_ns (float): Time step size in nanoseconds.
    
    Returns:
        np.ndarray: Time array in nanoseconds.
    """
    return np.arange(0, total_time_ns + time_step_ns, time_step_ns)


def export_voltage_waveform(
    time_ns: np.ndarray,
    effective_potential: np.ndarray,
    convert_to_voltage_func,
    time_filename: str = "time_ns.txt",
    voltage_filename: str = "waveform_V.txt",
) -> None:
    """
    Export time and voltage arrays to text files for experimental use.
    
    Args:
        time_ns (np.ndarray): Time array in nanoseconds.
        effective_potential (np.ndarray): Effective potential array.
        convert_to_voltage_func: Function that converts effective potential to voltage.
            Should have signature: func(eff_potential: np.ndarray) -> np.ndarray
        time_filename (str): Filename for time data. Defaults to "time_ns.txt".
        voltage_filename (str): Filename for voltage data. Defaults to "waveform_V.txt".
    """
    if len(time_ns) != len(effective_potential):
        raise ValueError("Time and effective potential arrays must have the same length.")
    
    # Convert effective potential to voltage using the provided function
    voltage_V = convert_to_voltage_func(effective_potential)
    
    # Export to text files using numpy.savetxt
    np.savetxt(time_filename, time_ns, fmt='%.6f')
    np.savetxt(voltage_filename, voltage_V, fmt='%.6f')
