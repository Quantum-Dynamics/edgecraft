import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import const
import basic
import user_configuration as config

x = np.arange(0, len(config.space_matrix), 1)
y = np.arange(0, len(config.space_matrix[0]), 1)
energy = np.zeros_like(config.space_matrix, dtype=float)
energy = basic.apply_QH_energy(energy, const.E_QH, config.bulk_indices)
energy = basic.apply_confinement_potential(
    energy, config.bulk_indices, config.boundary_indices, const.alpha)
for index in range(len(config.etchings)):
    energy = energy + config.etchings[index] * config.etching_potentials[index]


def run(
    energy_graphs: bool,
    anim: bool,
    scale_factor: bool,
    dynamics: bool,
) -> None:
    print("running...")
    if (energy_graphs):
        print("making energy graphs...")
        show_energy_graphs()
    if (anim):
        print("making animation...")
        make_animation()
    if (scale_factor):
        print("calculating scale factor...")
        show_scale_factor()
    if (dynamics):
        print("calculating dynamics...")
        show_dynamics()
    print("Finished!")


def show_energy_graphs():
    # Plotting the energy
    x = np.arange(0, len(config.space_matrix), 1)
    y = np.arange(0, len(config.space_matrix[0]), 1)
    energy = np.zeros_like(config.space_matrix, dtype=float)
    energy = basic.apply_QH_energy(energy, const.E_QH, config.bulk_indices)
    energy = basic.apply_confinement_potential(
        energy, config.bulk_indices, config.boundary_indices, const.alpha)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    cplot = axes[0].pcolor(
        y,
        x,
        energy,
        cmap="jet",
        shading="nearest",
    )
    cplot.set_clim(0, const.E_F * 3 / 2)
    axes[0].set_aspect("equal")
    axes[0].set_xlabel("$Y$  ($" + f"{const.M:d}" + " l_B$)")
    axes[0].set_ylabel("$X$  ($" + f"{const.M:d}" + " l_B$)")
    axes[0].set_title("Potential before etching")
    fig.colorbar(cplot)

    axes[1].plot(
        y,
        energy[len(x) // 2, :],
        label="single electron energy",
    )
    axes[1].axhline(
        const.E_F, color="black", linestyle="dashed", label="$E_\mathrm{F}$")
    axes[1].hlines(
        2, 130, 130 + 10e-6 / const.unit_length, color="black", linewidth=3)
    axes[1].text(120, 2.5, "10 $\mathrm{\mu m}$")
    axes[1].set_xlim(101)
    axes[1].set_ylim(0, const.E_F * 3 / 2)
    axes[1].set_xlabel(
        "distance from material edge  ($" + f"{const.M:d}" + " l_B$)")
    axes[1].set_ylabel("Energy  ($e^2 / 4 \pi \epsilon l_0$)")
    axes[1].legend()
    axes[1].set_title("Potential profile before etching")

    axes[2].plot(basic.calc_velocity_along_edge(
        energy, const.e, const.B_0, const.E_F,
        const.E_0, const.unit_length, const.unit_length))
    axes[2].set_title("Electron velocity along the edge before etching")
    axes[2].set_ylabel("velocity")
    axes[2].set_xlabel("y-position")
    plt.show()

    # Applying etchings
    for index in range(len(config.etchings)):
        energy += config.etchings[index] * config.etching_potentials[index]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    cplot = axes[0].pcolor(
        y,
        x,
        energy,
        cmap="jet",
        shading="nearest",
    )
    cplot.set_clim(0, const.E_F * 3 / 2)
    axes[0].set_aspect("equal")
    axes[0].set_xlabel("$Y$  ($" + f"{const.M:d}" + " l_B$)")
    axes[0].set_ylabel("$X$  ($" + f"{const.M:d}" + " l_B$)")
    axes[0].set_title("Potential after etching")
    fig.colorbar(cplot)

    axes[1].plot(
        y,
        energy[len(x) // 2, :],
        label="single electron energy",
    )
    axes[1].axhline(const.E_F, color="black", linestyle="dashed",
                    label="$E_\mathrm{F}$")
    axes[1].hlines(2, 130, 130 + 10e-6 / const.unit_length,
                   color="black", linewidth=3)
    axes[1].text(120, 2.5, "10 $\mathrm{\mu m}$")
    axes[1].set_xlim(101)
    axes[1].set_ylim(0, const.E_F * 3 / 2)
    axes[1].set_xlabel("distance from material edge  ($" +
                       f"{const.M:d}" + " l_B$)")
    axes[1].legend()
    axes[1].set_title("Potential profile after etching")

    axes[2].plot(
        basic.calc_velocity_along_edge(
            energy, const.e, const.B_0, const.E_F,
            const.E_0, const.unit_length, const.unit_length))
    axes[2].set_title("Electron velocity along the edge after etching")
    axes[2].set_ylabel("velocity")
    axes[2].set_xlabel("y-position")
    plt.show()

    energy = basic.apply_local_constant_potential(
        energy, config.gate_potential[len(config.gate_potential) // 2],
        config.gate_indices)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    cplot = axes[0].pcolor(
        y,
        x,
        energy,
        cmap="jet",
        shading="nearest",
    )
    cplot.set_clim(0, const.E_F * 3 / 2)
    axes[0].set_aspect("equal")
    axes[0].set_xlabel("$Y$  ($" + f"{const.M:d}" + " l_B$)")
    axes[0].set_ylabel("$X$  ($" + f"{const.M:d}" + " l_B$)")
    axes[0].set_title("Potential with some gate voltage")
    fig.colorbar(cplot)

    axes[1].plot(
        y,
        energy[len(x) // 2, :],
        label="single electron energy",
    )
    axes[1].axhline(const.E_F, color="black", linestyle="dashed",
                    label="$E_\mathrm{F}$")
    axes[1].hlines(2, 130, 130 + 10e-6 / const.unit_length,
                   color="black", linewidth=3)
    axes[1].text(120, 2.5, "10 $\mathrm{\mu m}$")
    axes[1].set_xlim(101)
    axes[1].set_ylim(0, const.E_F * 3 / 2)
    axes[1].set_xlabel("distance from material edge  ($" +
                       f"{const.M:d}" + " l_B$)")
    axes[1].legend()
    axes[1].set_title("Potential profile with some gate voltage")

    axes[2].plot(
        basic.calc_velocity_along_edge(
            energy, const.e, const.B_0, const.E_F,
            const.E_0, const.unit_length, const.unit_length))
    axes[2].set_title(
        "Electron velocity along the edge with some gate voltage")
    axes[2].set_ylabel("velocity")
    axes[2].set_xlabel("y-position")
    plt.show()


cbar = None


def make_animation() -> None:
    fig, axes = plt.subplots(1, 3)
    fig.set_size_inches(14, 4)
    ds = []
    velocity = []
    edge_width = []
    centeredge = []
    for index in range(len(config.gate_potential)):
        e_new = np.copy(energy)
        e_new = basic.apply_local_varying_potential(
            e_new, config.gate * config.gate_potential[index])

        centeredge.append(basic.find_center_edge(e_new, const.E_F))
        ds.append(basic.calc_ds(
            centeredge[index], const.unit_length, const.unit_length))

        # Calculates velocity in SI units
        velocity.append(basic.calc_velocity_along_edge(
            e_new, const.e, const.B_0, const.E_F, const.E_0,
            const.unit_length, const.unit_length))
    path = basic.calc_path(ds, velocity, config.time_scale, 350)

    def plot_anim(index: int) -> None:
        global cbar
        global energy

        if cbar is not None:
            cbar.remove()

        # clears plot
        axes[0].cla()
        axes[1].cla()
        axes[2].cla()

        e_new = energy.copy()
        e_new = basic.apply_local_varying_potential(
            e_new, config.gate_potential[index] * config.gate)

        edge = basic.find_edge(e_new, const.E_F, const.U_fluc, config.bulk)

        # Calculates velocity in SI units
        edge_width.append(len(np.where(
            edge[len(edge) // 2] == np.full_like(edge[len(edge) // 2], 1))[0]))

        # edge 2D plot
        cplot = axes[0].pcolor(
            y,
            x,
            edge,
            shading="nearest",
        )
        axes[0].set_aspect("equal")
        axes[0].set_xlabel("$Y$  ($" + f"{const.M:d}" + " l_B$)")
        axes[0].set_ylabel("$X$  ($" + f"{const.M:d}" + " l_B$)")
        axes[0].set_title(
            f"time: {np.round(index * config.time_scale * 1e9, 2)} ns")
        axes[0].scatter(x=centeredge[index][int(path[index])],
                        y=path[index], s=15, c='green', marker='o')
        cbar = fig.colorbar(cplot, orientation="vertical")

        # energy 1D plot
        axes[1].plot(
            y,
            e_new[len(x) // 2, :],
            label="single electron energy",
        )
        axes[1].axhline(
            const.E_F, color="black", linestyle="dashed", label="$E_F$")
        axes[1].axhspan(
            const.E_F - const.U_fluc, const.E_F + const.U_fluc, color="red",
            alpha=0.3)
        axes[1].hlines(
            1.5, 130, 130 + 10e-6 / const.unit_length,
            color="black", linewidth=3)
        axes[1].text(120, 2.5, "10 $\mu m$")
        axes[1].set_xlim(101)
        axes[1].set_ylim(0, const.E_F * 2.5)
        axes[1].set_xlabel("$Y$  ($" + f"{const.M:d}" + " l_B$)")
        axes[1].set_ylabel("Energy  ($e^2 / 4 \pi epsilon l_0$)")
        axes[1].legend(fontsize=12)

        axes[2].plot(velocity[index], color='blue')
        axes[2].set_title("Electron velocity along the edge")
        axes[2].set_ylabel("velocity")
        axes[2].set_xlabel("y-position")
        axes[2].set_ylim(0, 2.10e3)
        print("Completed animation step ", index)
    ani = animation.FuncAnimation(
        fig, plot_anim, interval=100, frames=len(config.gate_potential))
    ani.save(filename='PoC.gif', writer='pillow', dpi=300)
    plt.close()

    # Since time step 0 is run twice to generate the initial animation figure
    ds = ds[1:]
    velocity = velocity[1:]

    print("Time it takes for wavepacket to travel along edge (seconds):")
    print(basic.calc_time(ds, velocity, config.time_scale))
    print("Max edge width: ",
          np.max(edge_width) * const.unit_length * 10e6, "micrometers")


def show_scale_factor() -> None:
    scale_factor = basic.test_local_potential_magnitude(
        energy, config.gate_indices, config.gate_potential, config.bulk,
        const.E_F, const.U_fluc)
    plt.plot(scale_factor)
    plt.title("Scale factor calculated from edge lengths")
    plt.show()

    mag = basic.find_local_potential_magnitude(
        config.desired_scale_factor, scale_factor, config.gate_potential)
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))
    # Adjust figsize as needed
    axes[0].plot(config.gate_potential)
    axes[0].set_title("configuration gate potential")
    axes[1].plot(mag)
    axes[1].set_title("required gate potential for desired scale factor")
    plt.show()

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))
    # Adjust figsize as needed
    axes[0].plot(config.desired_scale_factor)
    axes[0].set_title("Desired scale factor")
    axes[1].plot(basic.test_local_potential_magnitude(
        energy, config.gate_indices, mag,
        config.bulk, const.E_F, const.U_fluc))
    axes[1].set_title("Scale factor calculated from required potential")
    plt.show()

    with open("results.txt", 'w') as f:
        f.write("Scale factor:\n")
        f.write(str(scale_factor))
        f.write("\n")
        f.write("\n")
        f.write("Required potential for desired scale factor:\n")
        f.write(str(mag))
        f.write("\n")
        f.write("\n")
        f.write("Scale factor after applying required potential:\n")
        f.write(str(basic.test_local_potential_magnitude(
            energy, config.gate_indices, mag,
            config.bulk, const.E_F, const.U_fluc)))
    with open("voltage.txt", 'w') as f:
        for x in mag:
            f.write(str(config.convert_to_voltage(x)))
            f.write("\n")


def show_dynamics() -> None:
    ds = []
    velocity = []
    centeredge = []
    for index in range(len(config.gate_potential)):
        e_new = np.copy(energy)
        e_new = basic.apply_local_constant_potential(
            e_new, config.gate_potential[index], config.gate_indices)

        centeredge.append(basic.find_center_edge(e_new, const.E_F))
        ds.append(basic.calc_ds(
            basic.find_center_edge(e_new, const.E_F),
            const.unit_length, const.unit_length))

        # Calculates velocity in SI units
        velocity.append(basic.calc_velocity_along_edge(
            e_new, const.e, const.B_0, const.E_F, const.E_0,
            const.unit_length, const.unit_length))
    stretch = []
    for index in range(len(centeredge)):
        stretch.append([])
        for index2 in range(len(centeredge[0])):
            stretch[index].append(basic.calc_stretch(
                centeredge, ds, index, index2,
                const.unit_length, const.unit_length))
    fig, axes = plt.subplots()

    def animator(index):
        axes.cla()
        axes.plot(stretch[index])
        axes.set_ylim(.985, 1.01)
    anim = animation.FuncAnimation(fig, animator, interval=100,
                                   frames=len(config.gate_potential))
    anim.save(filename='Stretch.gif', writer='pillow', dpi=300)
    plt.close()
    fig, axes = plt.subplots()

    def animator2(index):
        axes.cla()
        axes.plot(centeredge[index])
        axes.set_ylim(100, 350)
    anim2 = animation.FuncAnimation(
        fig, animator2, interval=100, frames=len(config.gate_potential) - 1)
    anim2.save(filename='Edge_movement.gif', writer='pillow', dpi=300)
    plt.close()
    print("Total stretch")
    print(np.power(np.prod(stretch), 1 / float(len(stretch[0]))))
    plt.plot(np.prod(stretch, axis=0))
    plt.title("stretch map")
    plt.show()
    print("path the electron takes:")
    print(basic.calc_path(ds, velocity, config.time_scale, 350))
    print("Electron stretch: ")
    print(basic.calc_electron_stretch(
        centeredge, ds, velocity, config.time_scale, start_index=250,
        pixel_x_width=const.unit_length, pixel_y_width=const.unit_length))
    plt.plot(basic.calc_stretch_of_time(
        centeredge, ds, velocity, config.time_scale, start_index=250,
        pixel_x_width=const.unit_length, pixel_y_width=const.unit_length))
    plt.title("Electron stretch vs time")
    plt.show()
