print("running")
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import const
import basic
import config


#Plotting the energy
x=np.arange(0,len(config.space_matrix),1)
y=np.arange(0,len(config.space_matrix[0]),1)
energy = np.zeros_like(config.space_matrix, dtype=float)
energy = basic.apply_QH_energy(energy, const.E_QH, config.bulk_indices)
energy = basic.apply_confinement_potential(energy, config.bulk_indices, config.boundary_indices, const.alpha)

fig, axis = plt.subplots()
cplot = axis.pcolor(
    y,
    x,
    energy,
    cmap="jet",
    shading="nearest",
)
cplot.set_clim(0, const.E_F * 3 / 2)
axis.set_aspect("equal")
axis.set_xlabel("$Y$  ($" + f"{const.M:d}" + " l_B$)")
axis.set_ylabel("$X$  ($" + f"{const.M:d}" + " l_B$)")
fig.colorbar(cplot)
plt.show()

fig, axis = plt.subplots()
axis.plot(
    y,
    energy[len(x) // 2, :],
    label="single electron energy",
)
axis.axhline(const.E_F, color="black", linestyle="dashed", label="$E_\mathrm{F}$")
axis.hlines(2, 130, 130 + 10e-6 / const.l, color="black", linewidth=3)
axis.text(120, 2.5, "10 $\mathrm{\mu m}$")
axis.set_xlim(101)
axis.set_ylim(0, const.E_F * 3 / 2)
axis.set_xlabel("$Y$  ($" + f"{const.M:d}" + " l_B$)")
axis.set_ylabel("Energy  ($e^2 / 4 \pi \epsilon l_0$)")
axis.legend()
plt.show()

#Applying etchings
for index in range(len(config.etchings)):
    energy=energy+config.etchings[index]*config.etching_potentials[index]

fig, axis = plt.subplots()
cplot = axis.pcolor(
    y,
    x,
    energy,
    cmap="jet",
    shading="nearest",
)
cplot.set_clim(0, const.E_F * 3 / 2)
axis.set_aspect("equal")
axis.set_xlabel("$Y$  ($" + f"{const.M:d}" + " l_B$)")
axis.set_ylabel("$X$  ($" + f"{const.M:d}" + " l_B$)")
fig.colorbar(cplot)
plt.show()

fig, axis = plt.subplots()
axis.plot(
    y,
    energy[len(x) // 2, :],
    label="single electron energy",
)
axis.axhline(const.E_F, color="black", linestyle="dashed", label="$E_\mathrm{F}$")
axis.hlines(2, 130, 130 + 10e-6 / const.l, color="black", linewidth=3)
axis.text(120, 2.5, "10 $\mathrm{\mu m}$")
axis.set_xlim(101)
axis.set_ylim(0, const.E_F * 3 / 2)
axis.set_xlabel("$Y$  ($" + f"{const.M:d}" + " l_B$)")
axis.set_ylabel("Energy  ($e^2 / 4 \pi \epsilon l_0$)")
axis.legend()
plt.show()

fig, axes = plt.subplots(1, 2)
fig.set_size_inches(9, 4)
cbar = None
frames = 101
#Literally E_F/100
E_gate_step = (const.E_F) / (frames - 1)
edge_yWidth = []

fig, axes = plt.subplots(1, 2)
fig.set_size_inches(9, 4)
cbar = None
#Literally E_F/100
E_gate_step = (const.E_F) / (frames - 1)
edge_yWidth = []

def plot_anim(index: int) -> None:
    global cbar
    global energy

    if cbar is not None:
        cbar.remove()
    
    #clears plot
    axes[0].cla()
    axes[1].cla()

    e_new=np.copy(energy)
    e_new = basic.apply_local_constant_potential(e_new, config.gate_potential[index], config.gate_indices)

    edge = basic.find_edge(e_new, const.E_F, const.U_fluc, config.bulk)
    
    #I deleted an index because I'm pretty sure it was wrong
    #Also I think this if statement is messing things up. How the animation works, it should run every time.
    #if len(edge_yWidth) == index:
    edge_yWidth.append(len(np.where(basic.find_edge(e_new, const.E_F, const.U_fluc, config.bulk)[len(x) // 2, :] == 1)))

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
    axes[0].set_title(f"step: {index}")
    cbar = fig.colorbar(cplot, orientation="vertical")

    # energy 1D plot
    axes[1].plot(
        y,
        e_new[len(x) // 2, :],
        label="single electron energy",
    )
    axes[1].axhline(const.E_F, color="black", linestyle="dashed", label="$E_F$")
    axes[1].axhspan(const.E_F - const.U_fluc, const.E_F + const.U_fluc, color="red", alpha=0.3)
    axes[1].hlines(1.5, 130, 130 + 10e-6 / const.l, color="black", linewidth=3)
    axes[1].text(120, 2.5, "10 $mu m$")
    axes[1].set_xlim(101)
    axes[1].set_ylim(0, const.E_F * 2.5)
    axes[1].set_xlabel("$Y$  ($" + f"{const.M:d}" + " l_B$)")
    axes[1].set_ylabel("Energy  ($e^2 / 4 pi epsilon l_0$)")
    axes[1].legend(fontsize=12)
anim = animation.FuncAnimation(fig, plot_anim, interval=len(config.gate_potential), frames=len(config.gate_potential))
#Can't get the saving to work. It works fine in other PoC_copy.ipynb though.
#anim.save(filename="PoC.gif", writer="pillow", dpi=300)

dt=[]
dt.append(basic.calculate_edge_length(basic.find_edge(energy,const.E_F,const.U_fluc,config.bulk)))
for t in range (0,len(config.gate_potential)):
    e_new=np.copy(energy)
    e_new = basic.apply_local_constant_potential(e_new, config.gate_potential[t], config.gate_indices)
    dt.append(basic.calculate_edge_length(basic.find_edge(e_new,const.E_F, const.U_fluc, config.bulk)))

a=basic.calc_scale_factor(dt,dt[0])
plt.plot(a)
plt.show()

mag=basic.find_local_potential_magnitude(dt,a)