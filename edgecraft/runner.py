import numpy as np
import scipy
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
    energy, config.bulk_indices, config.boundary_indices,
    const.alpha, .02)
# print((basic.find_center_edge(energy, const.E_F)[len(energy) // 2] - (len(
#     energy[0]) // 2 - config.radius_gate)) * const.unit_length)
for index in range(len(config.etchings)):
    energy = energy + config.etchings[index] * config.etching_potentials[index]
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
path = basic.calc_path(ds, velocity, config.time_scale, config.start_index)


def run(
    energy_graphs: bool,
    anim: bool,
    scale_factor: bool,
    dynamics: bool,
    pulse: bool,
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
    if (pulse):
        print("calculating pulse...")
        calc_pulse()

    print("Finished!")


def show_energy_graphs():
    # Makes a copy of energy to do weird things to
    energy = np.zeros_like(config.space_matrix, dtype=float)
    energy = basic.apply_QH_energy(energy, const.E_QH, config.bulk_indices)
    energy = basic.apply_confinement_potential(
        energy, config.bulk_indices, config.boundary_indices,
        const.alpha, .02)
    # Plotting the energy
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
    axes[1].axhspan(
        const.E_F - const.U_fluc, const.E_F + const.U_fluc, color="red",
        alpha=0.3)
    axes[1].hlines(
        2, 130, 130 + 10e-6 / const.unit_length, color="black", linewidth=3)
    axes[1].text(120, 2.5, "10 $\mathrm{\mu m}$")
    axes[1].set_xlim(0)
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
    axes[1].axhspan(
        const.E_F - const.U_fluc, const.E_F + const.U_fluc, color="red",
        alpha=0.3)
    axes[1].hlines(2, 130, 130 + 10e-6 / const.unit_length,
                   color="black", linewidth=3)
    axes[1].text(120, 2.5, "10 $\mathrm{\mu m}$")
    axes[1].set_xlim(0)
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

    # Un-applying etchings
    for index in range(len(config.etchings)):
        energy -= config.etchings[index] * config.etching_potentials[index]
    # Applying gate voltage
    energy = basic.apply_local_varying_potential(
        energy,
        config.gate_potential[len(config.gate_potential) // 2] * config.gate)

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
    axes[0].set_title("Potential with some gate")
    fig.colorbar(cplot)

    axes[1].plot(
        y,
        energy[len(x) // 2, :],
        label="single electron energy",
    )
    axes[1].axhline(const.E_F, color="black", linestyle="dashed",
                    label="$E_\mathrm{F}$")
    axes[1].axhspan(
        const.E_F - const.U_fluc, const.E_F + const.U_fluc, color="red",
        alpha=0.3)
    axes[1].hlines(2, 130, 130 + 10e-6 / const.unit_length,
                   color="black", linewidth=3)
    axes[1].text(120, 2.5, "10 $\mathrm{\mu m}$")
    axes[1].set_xlim(0)
    axes[1].set_ylim(0, const.E_F * 3 / 2)
    axes[1].set_xlabel("distance from material edge  ($" +
                       f"{const.M:d}" + " l_B$)")
    axes[1].legend()
    axes[1].set_title("Potential profile with some gate")

    axes[2].plot(
        basic.calc_velocity_along_edge(
            energy, const.e, const.B_0, const.E_F,
            const.E_0, const.unit_length, const.unit_length))
    axes[2].set_title("Electron velocity along the edge with some gate")
    axes[2].set_ylabel("velocity")
    axes[2].set_xlabel("y-position")
    plt.show()

    # Reapplying etchings
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
    axes[0].set_title("Potential with gate and etchings")
    fig.colorbar(cplot)

    axes[1].plot(
        y,
        energy[len(x) // 2, :],
        label="single electron energy",
    )
    axes[1].axhline(const.E_F, color="black", linestyle="dashed",
                    label="$E_\mathrm{F}$")
    axes[1].axhspan(
        const.E_F - const.U_fluc, const.E_F + const.U_fluc, color="red",
        alpha=0.3)
    axes[1].hlines(2, 130, 130 + 10e-6 / const.unit_length,
                   color="black", linewidth=3)
    axes[1].text(120, 2.5, "10 $\mathrm{\mu m}$")
    axes[1].set_xlim(0)
    axes[1].set_ylim(0, const.E_F * 3 / 2)
    axes[1].set_xlabel("distance from material edge  ($" +
                       f"{const.M:d}" + " l_B$)")
    axes[1].legend()
    axes[1].set_title("Potential profile with gate and etchings")

    axes[2].plot(
        basic.calc_velocity_along_edge(
            energy, const.e, const.B_0, const.E_F,
            const.E_0, const.unit_length, const.unit_length))
    axes[2].set_title(
        "Electron velocity along the edge with gate and etchings")
    axes[2].set_ylabel("velocity")
    axes[2].set_xlabel("y-position")
    plt.show()


cbar = None


def make_animation() -> None:
    fig, axes = plt.subplots(1, 3)
    fig.set_size_inches(14, 4)

    def plot_anim(index: int) -> None:
        # Gets energy and cbar from outside function
        global cbar
        global energy

        if cbar is not None:
            cbar.remove()

        # clears plot
        axes[0].cla()
        axes[1].cla()
        axes[2].cla()

        # Makes a copy of energy to mess with
        e_new = energy.copy()
        # Applies the gate voltage at the time step
        e_new = basic.apply_local_varying_potential(
            e_new, config.gate_potential[index] * config.gate)

        edge = basic.find_edge(e_new, const.E_F, const.U_fluc, config.bulk)

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
        if (path[index] < len(energy)):
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
        axes[1].set_xlim(0)
        axes[1].set_ylim(0, const.E_F * 1.5)
        axes[1].set_xlabel("$Y$  ($" + f"{const.M:d}" + " l_B$)")
        axes[1].set_ylabel("Energy  ($e^2 / 4 \pi epsilon l_0$)")
        axes[1].legend(fontsize=12)

        # velocity 1D plot
        axes[2].plot(velocity[index], color='blue')
        axes[2].axhline(
            258.2, color="black", linestyle="dashed", label="$start velocity$")
        axes[2].axhline(
            1414.95, color="black", linestyle="dashed", label="$end velocity$")
        axes[2].set_title("Electron velocity along the edge")
        axes[2].set_ylabel("velocity")
        axes[2].set_xlabel("y-position")
        axes[2].set_ylim(0, np.max(velocity))
        print("Completed animation step ", index)
    ani = animation.FuncAnimation(
        fig, plot_anim, interval=100, frames=len(config.gate_potential))
    ani.save(filename='PoC.gif', writer='pillow', dpi=300)
    plt.close()

    print("Time it takes for wavepacket to travel along edge (seconds):")
    print(basic.calc_time(ds, velocity, config.time_scale))
    print("Max edge width: ",
          np.max(edge_width) * const.unit_length * 1e6, "micrometers")


def show_scale_factor() -> None:
    # Calculates scale factor from gate potential
    scale_factor = basic.test_local_potential_magnitude(
        energy, config.gate, config.gate_potential,
        const.E_F, config.gate_start, config.gate_end)
    plt.plot(scale_factor)
    plt.title("Scale factor calculated from configuration gate potential")
    plt.show()

    # Calculates required gate potential for desired scale factor
    mag = basic.find_local_potential_magnitude(
        config.desired_scale_factor, scale_factor, config.gate_potential)
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))
    axes[0].plot(config.gate_potential)
    axes[0].set_title("configuration gate potential")
    axes[1].plot(mag)
    axes[1].set_title("required gate potential for desired scale factor")
    plt.show()

    # Compares the resulting scale factor with the desired scale factor.
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))
    axes[0].plot(config.desired_scale_factor)
    axes[0].set_title("Desired scale factor")
    axes[1].plot(basic.test_local_potential_magnitude(
        energy, config.gate, mag, const.E_F,
        config.gate_start, config.gate_end))
    axes[1].set_title("Scale factor calculated from required potential")
    plt.show()

    # Saves scale factor from configuration gate potential, required gate
    # potential, and scale factor from required potential into txt files
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
            energy, config.gate, mag, const.E_F,
            config.gate_start, config.gate_end)))
    with open("voltage.txt", 'w') as f:
        for x in mag:
            f.write(str(config.convert_to_voltage(x)))
            f.write("\n")


def show_dynamics() -> None:
    global velocity
    global centeredge
    global ds
    # Computes the relative scale factor at each point in time and space
    stretch = []
    for index in range(len(centeredge)):
        stretch.append([])
        for index2 in range(len(centeredge[0])):
            stretch[index].append(basic.calc_stretch(
                centeredge, ds, index, index2,
                const.unit_length, const.unit_length))
    fig, axes = plt.subplots()

    def animator(index):
        # Animates the relative change in edge length at each point
        axes.cla()
        axes.plot(stretch[index])
        axes.set_ylim(np.min(stretch), np.max(stretch))
    anim = animation.FuncAnimation(
        fig, animator, interval=100, frames=len(config.gate_potential))
    anim.save(filename='Stretch.gif', writer='pillow', dpi=300)
    plt.close()
    fig, axes = plt.subplots()
    diff_edge = np.array(centeredge[1:]) - np.array(centeredge[:-1])

    def animator2(index):
        # Animates the movement of the edge.
        axes.cla()
        if (index == 0):
            axes.plot(np.zeros_like(centeredge[0]))
        else:
            axes.plot(diff_edge[index - 1])
        axes.set_ylim(np.max(diff_edge), np.min(diff_edge))
    anim2 = animation.FuncAnimation(
        fig, animator2, interval=100, frames=len(config.gate_potential) - 1)
    anim2.save(filename='Edge_movement.gif', writer='pillow', dpi=300)
    plt.close()
    print("Total stretch")
    total_stretch = np.power(np.prod(
        stretch, axis=0), 1 / float(len(stretch[0])))
    print(np.prod(total_stretch))
    plt.plot(total_stretch)
    plt.title("stretch map (average stretch per time step)")
    plt.ylim(min(total_stretch[config.gate_start + 10:config.gate_end - 10]),
             max(total_stretch[config.gate_start + 10:config.gate_end - 10]))
    plt.show()
    plt.plot(path)
    plt.title("electron path")
    plt.ylabel("electron y-coordinate")
    plt.xlabel("time")
    plt.show()
    print("Electron stretch: ")
    print(basic.calc_electron_stretch(
        centeredge, ds, velocity, config.time_scale,
        start_index=config.start_index,
        pixel_x_width=const.unit_length, pixel_y_width=const.unit_length))
    plt.plot(basic.calc_stretch_of_time(
        centeredge, ds, velocity, config.time_scale,
        start_index=config.start_index,
        pixel_x_width=const.unit_length, pixel_y_width=const.unit_length))
    plt.title("Electron stretch vs time")
    plt.show()

    # The following doesn't work
    """
    mag = basic.find_local_potential_dynamic_magnitude(
        energy, const.E_F, config.gate,
        config.desired_scale_factor,
        config.gate_potential[1] - config.gate_potential[0],
        centeredge, ds, const.e, const.B_0, const.E_0, velocity,
        config.time_scale, config.start_index,
        const.unit_length, const.unit_length)

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))
    # Adjust figsize as needed
    axes[0].plot(config.gate_potential)
    axes[0].set_title("configuration gate potential")
    axes[1].plot(mag)
    axes[1].set_title("required gate potential for desired scale factor")
    plt.show()

    ds = []
    velocity = []
    centeredge = []
    for index in range(len(mag)):
        e_new = np.copy(energy)
        e_new = basic.apply_local_varying_potential(
            e_new, mag[index] * config.gate)

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
    fig, axes = plt.subplots(1, 2)
    axes[0].plot(config.desired_scale_factor)
    axes[0].set_title("Desired scale factor")
    axes[1].plot(basic.calc_stretch_of_time(
        centeredge, ds, velocity, config.time_scale,
        start_index=config.start_index,
        pixel_x_width=const.unit_length, pixel_y_width=const.unit_length))
    axes[1].set_title("Electron scale factor from required magnitude")
    plt.show()
    """


def calc_pulse():
    # We should let the pulse fill up the region between this point and
    # the beginning of the expanding region.
    stopping_point = int(
        (3 * config.gate_end + config.gate_start) / 4)
    dist = np.sum(
        ds[0][config.gate_start + 5:stopping_point])
    # Assuming we let the pulse fill up the region between these indices

    speed = velocity[0]
    speed = np.average(
        speed[config.gate_start:config.gate_end])
    # Assuming the speed is uniform and fluctuation are due to poor pixelation
    end_speed = velocity[len(velocity) - 1]
    end_speed = np.average(
        end_speed[config.gate_start:config.gate_end])
    # The speed changes as the potential changes. Difference in speed causes
    # nodes of the pulse to be closer in time, thus increasing frequency.
    speed_difference = end_speed / speed
    pulse_end_path = basic.calc_path(
        ds, velocity, config.time_scale, stopping_point)[len(ds) - 1]
    if (pulse_end_path >= config.gate_end):
        print("pulse exits the expanding region before expansion is finished.")
    pulse_time = dist / speed
    # Our machine can't emit short pulses
    if (pulse_time < 10e-9):
        print("pulse too short")
    # We're tyring to measure scale factor redshift.
    scale_factor = basic.test_local_potential_magnitude(
        energy, config.gate,
        config.gate_potential,
        const.E_F, config.gate_start,
        config.gate_end)
    scale_factor = scale_factor[len(scale_factor) - 1]
    freq_diff = speed_difference / scale_factor
    frequency = min(10e9, 10e9 * scale_factor / speed_difference)
    sampling_rate = 100 * frequency  # Hz
    t = np.linspace(
        0, pulse_time, int(sampling_rate * pulse_time), endpoint=False)
    t2 = np.linspace(
        0, pulse_time / speed_difference, int(
            sampling_rate * pulse_time), endpoint=False)
    t3 = np.linspace(
        0, pulse_time * scale_factor, int(
            sampling_rate * pulse_time), endpoint=False)
    t4 = np.linspace(
        0, pulse_time / freq_diff, int(
            sampling_rate * pulse_time), endpoint=False)
    signal = np.sin(2 * np.pi * frequency * t)
    signal2 = np.sin(
        2 * np.pi * frequency * speed_difference * t2)
    signal3 = np.sin(
        2 * np.pi * frequency / scale_factor * t3)
    signal4 = np.sin(
        2 * np.pi * frequency * freq_diff * t4)
    N = len(signal)
    frequencies = np.abs(scipy.fft.fftfreq(N, d=1 / sampling_rate))
    frequencies2 = np.abs(scipy.fft.fftfreq(
        N, d=1 / sampling_rate / speed_difference))
    frequencies3 = np.abs(scipy.fft.fftfreq(
        N, d=1 / sampling_rate * scale_factor))
    frequencies4 = np.abs(scipy.fft.fftfreq(
        N, d=1 / sampling_rate / freq_diff))
    # Compute the FFT and only consider positive frequencies
    FT = np.abs(scipy.fft.fft(signal))
    FT2 = np.abs(scipy.fft.fft(signal2))
    FT3 = np.abs(scipy.fft.fft(signal3))
    FT4 = np.abs(scipy.fft.fft(signal4))
    plt.figure(figsize=(10, 6))
    # Calculates shift due to each combination of velocity and scale factor
    plt.plot(frequencies, FT, label="Input pulse")
    plt.plot(frequencies2, FT2, label="Output pulse: velocity shift only")
    plt.plot(frequencies3, FT3, label="Output pulse: scale factor shift only")
    plt.plot(frequencies4, FT4,
             label="Output pulse: velocity and scale factor shift")
    plt.legend()
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    # Makes the plots all appear on screen. Won't work if the scale factor
    # redshift is too large compared to velocity redshift.
    plt.xlim(
        min(frequency / freq_diff ** .2, freq_diff ** 1.2 * frequency),
        max(frequency / freq_diff ** .1, freq_diff ** 1.1 * frequency))
    plt.title('Frequency Spectrum of Signal')
    plt.grid(True)
    plt.show()
