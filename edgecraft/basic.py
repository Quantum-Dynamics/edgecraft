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


def find_gate_potential_for_scale_factor(
    target_scale_factors: np.ndarray,
    reference_scale_factors: np.ndarray,
    reference_potentials: np.ndarray,
) -> np.ndarray:
    """
    Find gate potentials that produce desired scale factors using a lookup
    table approach.
    
    This implements Miller903's algorithm: for each target scale factor,
    find the reference potential that produces the closest scale factor.
    
    Args:
        target_scale_factors (np.ndarray): Array of desired scale factors a(t).
        reference_scale_factors (np.ndarray): Array of scale factors from 
            reference simulation.
        reference_potentials (np.ndarray): Array of gate potentials from 
            reference simulation corresponding to reference_scale_factors.
            
    Returns:
        np.ndarray: Array of gate potentials that should produce the target
            scale factors.
    """
    if len(reference_scale_factors) != len(reference_potentials):
        raise ValueError("Reference arrays must have the same length.")
    
    target_potentials = np.zeros_like(target_scale_factors)
    
    for i, target_a in enumerate(target_scale_factors):
        # Find the index that minimizes |a_0(tau) - a(tau_0)|
        diff = np.abs(reference_scale_factors - target_a)
        closest_idx = np.argmin(diff)
        target_potentials[i] = reference_potentials[closest_idx]
    
    return target_potentials


def optimize_gate_potential_for_scale_factor(
    target_scale_factor: float,
    energy: np.ndarray,
    E_F: float,
    U_fluc: float,
    bulk: np.ndarray,
    gate_indices: np.ndarray,
    initial_edge_length: float,
    potential_range: tuple[float, float] = (-1.0, 1.0),
    tolerance: float = 1e-3,
    max_iterations: int = 100,
) -> float:
    """
    Find the gate potential that produces a specific target scale factor
    using iterative optimization.
    
    This implements a more sophisticated version of the naive algorithm
    mentioned in the issue.
    
    Args:
        target_scale_factor (float): Desired scale factor a = l/l_0.
        energy (np.ndarray): Base energy array before gate potential is applied.
        E_F (float): Fermi energy.
        U_fluc (float): Energy fluctuation parameter.
        bulk (np.ndarray): Bulk region mask.
        gate_indices (np.ndarray): Indices where gate potential is applied.
        initial_edge_length (float): Initial edge length l_0.
        potential_range (tuple): Min and max gate potential to search.
        tolerance (float): Convergence tolerance for scale factor.
        max_iterations (int): Maximum number of optimization iterations.
        
    Returns:
        float: Gate potential that produces the target scale factor.
        
    Raises:
        ValueError: If optimization fails to converge.
    """
    min_potential, max_potential = potential_range
    
    for iteration in range(max_iterations):
        # Try the midpoint of current range
        test_potential = (min_potential + max_potential) / 2
        
        # Apply gate potential to energy
        test_energy = np.copy(energy)
        test_energy = apply_local_constant_potential(
            test_energy, test_potential, gate_indices
        )
        
        # Calculate resulting scale factor
        edge = find_edge(test_energy, E_F, U_fluc, bulk)
        edge_length = calc_edge_length(edge)
        current_scale_factor = edge_length / initial_edge_length
        
        # Check convergence
        if abs(current_scale_factor - target_scale_factor) < tolerance:
            return test_potential
        
        # Update search range based on result
        if current_scale_factor < target_scale_factor:
            # Need more positive potential to increase scale factor
            min_potential = test_potential
        else:
            # Need more negative potential to decrease scale factor
            max_potential = test_potential
    
    raise ValueError(
        f"Failed to converge after {max_iterations} iterations. "
        f"Target: {target_scale_factor}, Current: {current_scale_factor}"
    )
