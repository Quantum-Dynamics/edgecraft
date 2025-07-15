import numpy as np
from scipy.integrate import solve_ivp

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
        val (float): Value to add at each bulk index.
        bulk_indices (np.ndarray): 2D array of bulk point coordinates.

    Returns:
        np.ndarray: The modified energy array.
    """
    for x_gate, y_gate in space_indices:
        energy[x_gate, y_gate] += val
    return energy

def apply_local_varying_potential(
    energy: np.ndarray,
    val: np.ndarray,
) -> np.ndarray:
    """
    Add a quantum Hall energy value to specified bulk indices in the energy
    array.

    Args:
        energy (np.ndarray): 2D array of energy values to modify.
        val (np.ndarray): Value to add at each bulk index.

    Returns:
        np.ndarray: The modified energy array.
    """
    energy=energy+val
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

def find_center_edge(edge:np.ndarray)->np.ndarray:
    """
    Finds the center of the edge points at each y coordinate.

    Args:
        edge (np.ndarray): 2D array with a 1 where a point is in the edge and a 0 elsewhere

    Returns:
        np.ndarray: the x coordinate (float) of the center of the edge for each y coordinate
    """

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
    return centeredge

def calc_edge_length(
    edge: np.ndarray,
    pixel_x: float = 1.0,
    pixel_y: float = 1.0,
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
    centeredge = find_center_edge(edge)

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
    Calculates and plots the scale factor for the given local potential.

    Args:
        energy (np.ndarray): 2D array of the energy values before applying the local potential
        gate (np.ndarray): 2D array of the relative gate magnitude. Should be identical in shape to energy.
        local_potential_magnitude (np.ndarray): 1D array of the magnitude of the local potential at each time step
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
    e:float,
    B:float,
    E_scale:float =1.0,
    pixel_x_width:float =1.0,
    pixel_y_width:float =1,
)->np.ndarray:
    """
    Calculates the velocity of electrons at each point if they were to be moving along a QH edge.

    Args:
        energy (np.ndarray): 2D array of energy values.
        e (float): elementary charge
        B (float): magnitude of perpendicular magnetic field
        E_scale (float): energy scale. energy*E_scale should be in Joules
        pixel_x_width (float): width of pixels in the x direction
        pixel_y_width (float): width of pixels in the y direction

    Returns:
        np.ndarray: 2D array with the velocity at each point.
    """

    #Calculates SI velocity if SI units are inputted
    grad=np.array(np.gradient(energy))/(e*B)
    grad=grad*E_scale
    return np.sqrt(np.square(grad[0]/pixel_y_width)+np.square(grad[1]/pixel_x_width))

def calc_velocity_along_edge(
    energy:np.ndarray,
    e:float,
    B:float,
    edge,
    E_scale:float =1.0,
    pixel_x_width:float =1,
    pixel_y_width:float =1
)->np.ndarray:
    """
    Calculates the velocity of electrons at the center of the edge

    Args:
        energy (np.ndarray): 2D array of energy values.
        e (float): elementary charge
        B (float): magnitude of perpendicular magnetic field
        edge (np.ndarray): 2D array with a 1 where a point is in the edge and a 0 elsewhere 
        E_scale (float): energy scale. energy*E_scale should be in Joules
        pixel_x_width (float): width of pixels in the x direction
        pixel_y_width (float): width of pixels in the y direction

    Returns:
        np.ndarray: 1D array of the velocity at the edge point at each y coordinate.
    """

    centeredge = find_center_edge(edge)
    velocity_array=calc_velocity(energy,e,B,E_scale,pixel_x_width,pixel_y_width)
    velocity_along_edge=[]
    for index in range(0,len(energy)):
        velocity_along_edge.append(velocity_array[index][int(centeredge[index]+.5)])
    return velocity_along_edge

def calc_ds(
    centeredge:np.ndarray,
    pixel_x_width:float =1.0,
    pixel_y_width:float=1.0,
)->np.ndarray:
    """
    Calculates the marginal length of the edge at each point compared to the unit length of 1m in the y direction

    Args:
        centeredge (np.ndarray): the x coordinate (float) of the center of the edge for each y coordinate
        pixel_x_width (float): width of pixels in the x direction
        pixel_y_width (float): width of pixels in the y direction

    Returns:
        np.ndarray: 1D array of the length to the next edge point at each y-coordinate.
    """
    dx = (centeredge[:-1] - centeredge[1:]) * pixel_x_width
    dy = np.full_like(dx,1.0)*pixel_y_width

    # since there's 1 less tangent line than pixels
    dx=np.append(dx,0.0)
    dy=np.append(dy,1.0)

    return np.sqrt(np.square(dx) + np.square(dy))

def calc_time(
    ds:np.ndarray,
    tangent_velocity:np.ndarray,
    time_scale:float=1, 
    start_index:int=0,
    end_index:int =None,
)->float:
    """
    Calculates the time it takes for an electron to travel from start_index to end_index while the gate voltage is being applied

    Args:
        ds (np.ndarray): length from 1 y-coordinate to the next in the edge
        tangent_velocity (np.ndarray): velocity along the edge
        time_scale (float=1): time between elements of gate_potential 
        start_index (int=0): index the electron starts at
        end_index (int =None): index the electron ends at

    Returns:
        float: the time it takes for the particle to get to end_index
    """
    if(end_index==None):
        end_index=len(ds[0])
    #ds and velocity need to have the same length scale.
    # Computes velocity. x is measured in pixels
    def dxdt(t,x):
        if (0<=x[0]<len(ds[0]) and 0<=t/time_scale<len(ds)):
            return tangent_velocity[int(t/time_scale)][int(x[0])]/ds[int(t/time_scale)][int(x[0])]
        elif(0<=x[0]<len(ds[0])):
            return tangent_velocity[len(ds)-1][int(x[0])]/ds[len(ds)-1][int(x[0])]
        else:
            return 1
    #Has a zero when x reaches the end pixel
    def reached_end(t,x): 
        return x[0]-end_index
    reached_end.terminal=True
    reached_end.direction=1
    solution= solve_ivp(dxdt, [0,10*len(ds)*time_scale],[start_index],events=reached_end)
    return solution.t_events[0][0]