# Theoretical Principles

## Overview

The `edgecraft` simulator is designed to model edge deformation in quantum Hall systems for analog universe experiments. It implements a comprehensive theoretical framework based on quantum Hall physics, incorporating Landau levels, edge states, confinement potentials, and disorder effects.

## Quantum Hall Effect Fundamentals

### Landau Levels

In a strong perpendicular magnetic field \(B\), the motion of electrons in a 2D system is quantized into Landau levels with energies:

\[
E_n = \hbar \omega_c \left(n + \frac{1}{2}\right)
\]

where \(\omega_c = \frac{eB}{m^*}\) is the cyclotron frequency and \(m^*\) is the effective mass of electrons in the material.

For GaAs, the effective mass is:
\[
m^* = 0.067 \cdot m_e
\]

The Landau level gap is given by:
\[
\Delta E_{LL} = \hbar \omega_c = \frac{\hbar e B}{m^*}
\]

### Magnetic Length

The natural length scale in the quantum Hall regime is the magnetic length:

\[
l_B = \sqrt{\frac{\hbar}{eB}}
\]

This length characterizes the spatial extent of the lowest Landau level wavefunction.

### Filling Factor

The filling factor describes how many Landau levels are occupied:

\[
\nu = \frac{n_s h}{eB} = \frac{n_s \phi_0}{B}
\]

where \(n_s\) is the electron density and \(\phi_0 = h/e\) is the magnetic flux quantum.

## Edge States

### Edge State Formation

At the boundary of a quantum Hall system, the confinement potential creates edge states that propagate along the boundary. These are chiral states with velocity:

\[
v_{edge} = \frac{1}{\hbar} \frac{dE}{dk}
\]

### Edge Current

The edge current is quantized and given by:

\[
I_{edge} = \nu \frac{e^2}{h} V
\]

where \(V\) is the applied voltage and \(e^2/h\) is the conductance quantum.

## Energy Scales and Unit System

### Unit Length and Energy

The simulator uses a rescaled unit system based on the magnetic length. The unit length is:

\[
l_{unit} = M \cdot l_B
\]

where \(M\) is a dimensionless multiplier (typically 20).

The corresponding unit energy is the Coulomb energy at this length scale:

\[
E_{unit} = \frac{e^2}{4\pi\epsilon l_{unit}}
\]

where \(\epsilon = \epsilon_r \epsilon_0\) is the permittivity of the material (GaAs: \(\epsilon_r = 12.9\)).

### Fermi Energy

The Fermi energy is typically set at:

\[
E_F = \frac{\Delta E_{LL}}{2}
\]

This places the Fermi level in the middle of the Landau level gap.

## Confinement Potential

### Mathematical Formulation

The confinement potential models the electrostatic effects at sample boundaries. For a bulk point at position \(\mathbf{r}\), the potential due to boundary charges is:

\[
V_{conf}(\mathbf{r}) = \alpha \sum_{i \in boundary} \frac{1}{|\mathbf{r} - \mathbf{r}_i|^{3/2}} \cdot dl
\]

where:
- \(\alpha\) is the confinement strength parameter
- \(\mathbf{r}_i\) are boundary point positions  
- \(dl\) is the differential length element

### Physical Interpretation

This \(r^{-3/2}\) dependence arises from the electrostatic potential of a line charge distribution representing the boundary. The potential creates the necessary edge confinement to support edge states.

## Disorder and Thermal Effects

### Disorder Potential

Random potential fluctuations are included through a disorder energy scale:

\[
U_{disorder} = \frac{60 \times 10^{-6} \text{ eV}}{E_{unit}}
\]

This represents typical disorder strength in high-quality GaAs heterostructures.

### Thermal Energy

Thermal broadening is modeled through:

\[
U_{thermal} = \frac{k_B T}{E_{unit}}
\]

### Total Fluctuation Energy

The combined fluctuation energy is:

\[
U_{fluc} = U_{disorder} + U_{thermal}
\]

This sets the energy scale for edge width and thermal smearing.

## Edge Finding Algorithm

### Edge Definition

The edge region is defined as spatial regions where the local energy satisfies:

\[
E_F - U_{fluc} \leq E(\mathbf{r}) \leq E_F + U_{fluc}
\]

This identifies regions where the local potential brings the system close to the Fermi energy, allowing edge state formation.

### Numerical Implementation

The algorithm proceeds by:

1. Calculate local energy \(E(x,y)\) including all potential contributions
2. Identify points satisfying the edge condition
3. Apply geometric constraints (bulk connectivity)
4. Calculate edge length and track evolution

## Gate Effects and Edge Deformation

### Local Potential Modification

Gate voltages modify the local potential through:

\[
E_{local}(\mathbf{r}) = E_{base}(\mathbf{r}) + V_{gate}
\]

This allows controlled deformation of edge positions.

### Edge Length Calculation

The edge length is calculated by connecting edge points and computing:

\[
L_{edge} = \sum_{i} \sqrt{(\Delta x_i)^2 + (\Delta y_i)^2}
\]

where the sum is over connected edge segments.

## Applications to Analog Universe Experiments

### Curved Spacetime Analogy

The edge deformation can simulate effects analogous to curved spacetime, where:
- Edge trajectory \(\leftrightarrow\) Geodesic in curved space
- Gate potentials \(\leftrightarrow\) Spacetime curvature
- Edge length changes \(\leftrightarrow\) Gravitational effects

### Parameter Correspondence

The mapping between quantum Hall parameters and gravitational analogs allows the simulator to model various spacetime geometries and test theoretical predictions in an accessible condensed matter system.