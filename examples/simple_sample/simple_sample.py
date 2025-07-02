import numpy as np

from edgecraft import (
    apply_confinement_potential,
    apply_local_constant_potential,
    apply_QH_energy,
    calc_Landau_level_gap,
    calc_edge_length,
    calc_magneticfield_for_nu,
    calc_thermal_energy,
    calc_unit_length_energy,
    find_edge,
    true_circle_in,
    e,
)


# Physical constants
n = 1e15                                # m^-2
B_0 = calc_magneticfield_for_nu(n, 1)   # T
T = 40e-3                               # K

# Calculate unit length and energy
M = 20
l_0, E_0 = calc_unit_length_energy(B_0, M)
E_LL_gap = calc_Landau_level_gap(B_0, E_0)
E_F = E_LL_gap / 2
E_QH = E_F / 2
U_thermal = calc_thermal_energy(T, E_0)
U_disorder = (60e-6 * e) / E_0
U_fluc = U_disorder + U_thermal

# Space matices
radius_gate = int(50e-6 / l_0)
x = np.arange(0, int(200e-6 / l_0), 1)
y = np.arange(0, int(150e-6 / l_0), 1)
Y, X = np.meshgrid(y, x)

space_matrix = (
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate) |
    (Y >= y[len(y) // 2])
).astype(int)
diff_y = np.gradient(space_matrix, 1, axis=0)
diff_x = np.gradient(space_matrix, 1, axis=1)

# sample edge
boundary = ((diff_x != 0) | (diff_y != 0)).astype(int)
boundary_y = y[np.where(boundary == 1)[1]]
boundary_x = x[np.where(boundary == 1)[0]]
boundary_indices = np.array(np.where(boundary == 1)).T

# bulk (space \ sample edge)
bulk = np.copy(space_matrix)
bulk[boundary == 1] = 0
bulk_indices = np.array(np.where(bulk == 1)).T

# vacuum
vacuum = np.copy((~space_matrix.astype(bool)).astype(int))

# expansion gate
gate = np.logical_xor(
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate),
    true_circle_in(
        Y,
        X,
        y[len(y) // 2],
        x[len(x) // 2],
        radius_gate - int(25e-6 / l_0),
    ),
).astype(int)
gate[Y >= y[len(y) // 2]] = 0
gate[boundary == 1] = 0
gate_indices = np.array(np.where(gate == 1)).T

# Initial energy calculations
alpha = 1e3
energy = np.zeros_like(space_matrix, dtype=float)
energy = apply_QH_energy(energy, E_QH, bulk_indices)
energy = apply_confinement_potential(
    energy,
    bulk_indices,
    boundary_indices,
    alpha,
)


if __name__ == "__main__":
    frames = 101
    E_gate_min = 0
    E_gate_max = E_F
    E_gate_step = (E_gate_max - E_gate_min) / (frames - 1)

    edge = find_edge(energy, E_F, U_fluc, bulk)
    edge_lengths = [calc_edge_length(edge)]
    for frame in range(frames - 1):
        energy = apply_local_constant_potential(
            energy,
            E_gate_step,
            gate_indices,
        )
        edge = find_edge(energy, E_F, U_fluc, bulk)
        edge_lengths.append(calc_edge_length(edge))

    np.save("edge_lengths.npy", np.array(edge_lengths))
    np.save("gate_potential.npy", np.arange(0, frames) * E_gate_step)
