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
    QH_energy: float,
    bulk_indices: np.ndarray,
) -> np.ndarray:
    """
    Add a quantum Hall energy value to specified bulk indices in the energy
    array.

    Args:
        energy (np.ndarray): 2D array of energy values to modify.
        QH_energy (float): Value to add at each bulk index.
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


def find_local_potential_magnitude(
    desired_scale_factor: np.ndarray,
    simulated_scale_factor:np.ndarray,
    gate_potential:np.ndarray
)->np.ndarray:
    """
    Calculate the required local potential magnitude for a scale factor closest to the desired scale factor

    Args:
        desired_scale_factor (np.ndarray): 1D array of scale factor at various time steps. Each element should satisfy .93<=scale_factor[t]<=1.
        E_F (float): Fermi energy of the material

    Returns:
        np.ndarray: an array with the required local potential at each step.
    """
    ret=np.full_like(desired_scale_factor,0.0)
    sf_new=desired_scale_factor/np.max(desired_scale_factor)
    for time_step in range(0,len(desired_scale_factor)):
        num=np.where(np.square( simulated_scale_factor -sf_new[time_step])==np.full_like( simulated_scale_factor, min(np.square( simulated_scale_factor - sf_new[time_step]))))[0][0]
        ret[time_step]=gate_potential[num]
    return ret


def test_local_potential_magnitude(
    energy:np.ndarray, 
    gate_indices:np.ndarray,
    gate_potential:np.ndarray,
    bulk:np.ndarray,
    E_F:float,
    U_fluc:float,
) ->np.ndarray:
    """
    Calculates the scale factor for the given local potential.

    Args:
        energy (np.ndarray): 2D array of the energy values before applying the local potential
        gate_indices (np.ndarray): 2D array with a 1 at each point point if a local potential is being applied there and a 0 if it isn't. Should be identical in shape to energy.
        gate_potential (np.ndarray): 1D array of the magnitude of the local potential at each time step. Magnitude of local potential is assumed to be uniform across space.
        bulk (np.ndarray): 2D array of the same shape as energy. Has a 1 where the point is in the bulk region and a 0 elsewhere.
        E_F (float): Fermi energy.
        U_fluc (float): Energy fluctuation parameter.

    Returns:
        np.ndarray: the scale factor at each time step with plot.
    """
    dt=[]
    for time_step in range(0,len(gate_potential)):
        e_new=energy.copy()
        e_new=apply_local_constant_potential(e_new,gate_potential[time_step],gate_indices)
        dt.append(calc_edge_length(find_edge(e_new,E_F,U_fluc,bulk)))
    scale_factor=calc_scale_factor(dt,dt[0])
    return scale_factor

def calc_velocity(
    energy:np.ndarray,
    e:float,B:float
)->np.ndarray:
    """
    Calculates the velocity at every point.

    Args:
        energy (np.ndarray): 2D array of the energy values before applying the local potential
        e (float): elementary charge
        B (float): Magnitude of perpendicular magnetic field

    Returns:
        np.ndarray: an array of the same shape as energy with the velocities at each coordinate.
    """
    grad=np.array(np.gradient(energy))/(e*B)
    return np.sqrt(np.square(grad[0])+np.square(grad[1]))

def calc_velocity_along_edge(
    energy:np.ndarray,
    e:float,
    B:float,
    edge
)->np.ndarray:
    """
    Calculates the velocity at each edge point.

    Args:
        energy (np.ndarray): 2D array of the energy values before applying the local potential
        e (float): elementary charge
        B (float): Magnitude of perpendicular magnetic field
        edge (np.ndarray): 2D array with a 1 at each point if it is in the edge and a 0 if it isn't. Same shape as energy

    Returns:
        np.ndarray: velocity at the edge at each y-coordinate.
    """
    centeredge = np.zeros(len(edge))
    for index_1 in range(len(edge)):
        if np.sum(edge[index_1]) == 0:
            raise ValueError(
                f"Row {index_1} has no edge points. Please check the edge array."
            )
         # Take the average of the edge points in this row
        for index_2 in range(len(edge[index_1])):
            centeredge[index_1] += index_2 * edge[index_1, index_2]
        centeredge[index_1] /= np.sum(edge[index_1])
    velocity_array=calc_velocity(energy,e,B)
    velocity_along_edge=[]
    for index in range(0,len(energy)):
        velocity_along_edge.append(velocity_array[index][int(centeredge[index])])
    return velocity_along_edge