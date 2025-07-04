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

# Etching potentials
U_etching9 = 0.3
U_etching8 = U_etching9 + 0.3
U_etching7 = U_etching8 + 0.3
U_etching6 = U_etching7 + 0.3
U_etching5 = U_etching6 + 0.3
U_etching4 = U_etching5 + 0.3
U_etching3 = U_etching4 + 0.3
U_etching2 = U_etching3 + 0.3
U_etching1 = U_etching2 + 0.3

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

# shallow etching region 1
etched1 = np.logical_xor(
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate),
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(5e-6 / l_0),
    ),
).astype(int)
etched1[Y >= y[len(y) // 2]] = 0
etched1[boundary == 1] = 0
etched1_indices = np.array(np.where(etched1 == 1)).T

# shallow etching region 2
etched2 = np.logical_xor(
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(5e-6 / l_0),
    ),
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(9e-6 / l_0),
    ),
).astype(int)
etched2[Y >= y[len(y) // 2]] = 0
etched2[boundary == 1] = 0
etched2[etched1 == 1] = 0
etched2_indices = np.array(np.where(etched2 == 1)).T

# shallow etching region 3
etched3 = np.logical_xor(
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(9e-6 / l_0),
    ),
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(11e-6 / l_0),
    ),
).astype(int)
etched3[Y >= y[len(y) // 2]] = 0
etched3[boundary == 1] = 0
etched3[etched1 == 1] = 0
etched3[etched2 == 1] = 0
etched3_indices = np.array(np.where(etched3 == 1)).T

# shallow etching region 4
etched4 = np.logical_xor(
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(11e-6 / l_0),
    ),
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(13e-6 / l_0),
    ),
).astype(int)
etched4[Y >= y[len(y) // 2]] = 0
etched4[boundary == 1] = 0
etched4[etched1 == 1] = 0
etched4[etched2 == 1] = 0
etched4[etched3 == 1] = 0
etched4_indices = np.array(np.where(etched4 == 1)).T

# shallow etching region 5
etched5 = np.logical_xor(
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(13e-6 / l_0),
    ),
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(15e-6 / l_0),
    ),
).astype(int)
etched5[Y >= y[len(y) // 2]] = 0
etched5[boundary == 1] = 0
etched5[etched1 == 1] = 0
etched5[etched2 == 1] = 0
etched5[etched3 == 1] = 0
etched5[etched4 == 1] = 0
etched5_indices = np.array(np.where(etched5 == 1)).T

# shallow etching region 6
etched6 = np.logical_xor(
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(15e-6 / l_0),
    ),
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(17e-6 / l_0),
    ),
).astype(int)
etched6[Y >= y[len(y) // 2]] = 0
etched6[boundary == 1] = 0
etched6[etched1 == 1] = 0
etched6[etched2 == 1] = 0
etched6[etched3 == 1] = 0
etched6[etched4 == 1] = 0
etched6[etched5 == 1] = 0
etched6_indices = np.array(np.where(etched6 == 1)).T

# shallow etching region 7
etched7 = np.logical_xor(
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(17e-6 / l_0),
    ),
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(19e-6 / l_0),
    ),
).astype(int)
etched7[Y >= y[len(y) // 2]] = 0
etched7[boundary == 1] = 0
etched7[etched1 == 1] = 0
etched7[etched2 == 1] = 0
etched7[etched3 == 1] = 0
etched7[etched4 == 1] = 0
etched7[etched5 == 1] = 0
etched7[etched6 == 1] = 0
etched7_indices = np.array(np.where(etched7 == 1)).T

# shallow etching region 8
etched8 = np.logical_xor(
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(19e-6 / l_0),
    ),
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(21e-6 / l_0),
    ),
).astype(int)
etched8[Y >= y[len(y) // 2]] = 0
etched8[boundary == 1] = 0
etched8[etched1 == 1] = 0
etched8[etched2 == 1] = 0
etched8[etched3 == 1] = 0
etched8[etched4 == 1] = 0
etched8[etched5 == 1] = 0
etched8[etched6 == 1] = 0
etched8[etched7 == 1] = 0
etched8_indices = np.array(np.where(etched8 == 1)).T

# shallow etching region 9
etched9 = np.logical_xor(
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(21e-6 / l_0),
    ),
    true_circle_in(
        Y, X, y[len(y) // 2], x[len(x) // 2],
        radius_gate - int(23e-6 / l_0),
    ),
).astype(int)
etched9[Y >= y[len(y) // 2]] = 0
etched9[boundary == 1] = 0
etched9[etched1 == 1] = 0
etched9[etched2 == 1] = 0
etched9[etched3 == 1] = 0
etched9[etched4 == 1] = 0
etched9[etched5 == 1] = 0
etched9[etched6 == 1] = 0
etched9[etched7 == 1] = 0
etched9[etched8 == 1] = 0
etched9_indices = np.array(np.where(etched9 == 1)).T

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
energy = apply_local_constant_potential(energy, U_etching1, etched1_indices)
energy = apply_local_constant_potential(energy, U_etching2, etched2_indices)
energy = apply_local_constant_potential(energy, U_etching3, etched3_indices)
energy = apply_local_constant_potential(energy, U_etching4, etched4_indices)
energy = apply_local_constant_potential(energy, U_etching5, etched5_indices)
energy = apply_local_constant_potential(energy, U_etching6, etched6_indices)
energy = apply_local_constant_potential(energy, U_etching7, etched7_indices)
energy = apply_local_constant_potential(energy, U_etching8, etched8_indices)
energy = apply_local_constant_potential(energy, U_etching9, etched9_indices)


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
