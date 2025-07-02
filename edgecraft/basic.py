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
