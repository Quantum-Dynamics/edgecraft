import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from edgecraft import (
    apply_confinement_potential,
    apply_local_constant_potential,
    apply_QH_energy,
    calc_Landau_level_gap,
    calc_edge_length,
    calc_magneticfield_for_nu,
    calc_thermal_energy,
    calc_unit_length_energy_time,
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
l_0, E_0, t_0 = calc_unit_length_energy_time(B_0, M)
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


fig, axes = plt.subplots(1, 2)
fig.set_size_inches(9, 4)
cbar = None
frames = 101
E_gate_min = 0
E_gate_max = E_F
E_gate_step = (E_gate_max - E_gate_min) / (frames - 1)
edge_lengths = []


def plot_anim(index: int) -> None:
    global cbar
    global energy

    if cbar is not None:
        cbar.remove()
    axes[0].cla()
    axes[1].cla()

    if index > 0:
        energy = apply_local_constant_potential(
            energy,
            E_gate_step,
            gate_indices,
        )

    edge = find_edge(energy, E_F, U_fluc, bulk)
    if len(edge_lengths) == index:
        edge_lengths.append(calc_edge_length(edge))

    # edge 2D plot
    cplot = axes[0].pcolor(
        y,
        x,
        edge,
        shading="nearest",
    )
    axes[0].set_aspect("equal")
    axes[0].set_xlabel("$Y$  ($" + f"{M:d}" + " l_B$)")
    axes[0].set_ylabel("$X$  ($" + f"{M:d}" + " l_B$)")
    axes[0].set_title(f"step: {index}")
    cbar = fig.colorbar(cplot, orientation="vertical")

    # energy 1D plot
    axes[1].plot(
        y,
        energy[len(x) // 2, :],
        label="single electron energy",
    )
    axes[1].axhline(
        E_F,
        color="black",
        linestyle="dashed",
        label="$E_\mathrm{F}$",
    )
    axes[1].axhspan(E_F - U_fluc, E_F + U_fluc, color="red", alpha=0.3)
    axes[1].hlines(1.5, 130, 130 + 10e-6 / l_0, color="black", linewidth=3)
    axes[1].text(120, 2.5, "10 $\mathrm{\mu m}$")
    axes[1].set_xlim(101)
    axes[1].set_ylim(0, E_F * 2.5)
    axes[1].set_xlabel("$Y$  ($" + f"{M:d}" + " l_B$)")
    axes[1].set_ylabel("Energy  ($e^2 / 4 \pi \epsilon l_0$)")
    axes[1].legend(fontsize=12)


if __name__ == "__main__":
    anim = animation.FuncAnimation(fig, plot_anim, interval=100, frames=frames)
    anim.save("simple_sample.gif")
