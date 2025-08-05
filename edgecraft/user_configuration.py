import numpy as np
import const


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


radius_gate = int(50e-6 / const.unit_length)

x = np.arange(0, int(200e-6 / const.unit_length), 1)
y = np.arange(0, int(150e-6 / const.unit_length), 1)

Y, X = np.meshgrid(y, x)

space_matrix = (
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate) |
    (Y >= y[len(y) // 2])
).astype(int)

diff_y = np.gradient(space_matrix, 1, axis=0)
diff_x = np.gradient(space_matrix, 1, axis=1)
boundary = ((diff_x != 0) | (diff_y != 0)).astype(int)
boundary_y = y[np.where(boundary == 1)[1]]
boundary_x = x[np.where(boundary == 1)[0]]
boundary_indices = np.array(np.where(boundary == 1)).T

bulk = space_matrix.copy()
bulk[boundary == 1] = 0
bulk_indices = np.array(np.where(bulk == 1)).T

vacuum = ((~space_matrix.astype(bool)).astype(int)).copy()

# expansion gate
gate = (true_circle_in(
    Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate)).astype(float)
gate[Y >= y[len(y) // 2]] = 0
gate[boundary == 1] = 0
gate_indices = np.array(np.where(gate == 1)).T
h_0 = 100


def find_gate_potential(max_edge_width, B):
    s = 2 * const.U_fluc / max_edge_width

    # Did a bunch of calculus; This is the function to satisfy for as many z
    def metric(a, b, c) -> float:
        def g(z):
            return (2 * a * z + b) * (const.E_F * z**3 / 2 - B * z) - (a * z ** 2 + b * z + c) * (s * z**3 - 2 * B)
        zeros = np.roots([-s * a, 2 * a * const.E_F / 2 - s * b, b * const.E_F / 2 - s * c, 0, B * b, 2 * B * c])
        real_zeros = [root.real for root in zeros if abs(root.imag) < 1e-9]
        real_positive_zeros = [root.real for root in real_zeros if root.real > 0]
        zero = np.min(real_positive_zeros)

        if (0 < -b / (2 * a) < zero):
            if (4 * (a * (-b / (2 * a)) ** 2 + b * (-b / (2 * a)) + c) < (a * (zero ** 2) + b * zero + c)):
                return -1
            elif (.25 * (a * (-b / (2 * a))**2 + b * (-b / (2 * a)) + c) > (a * (zero**2) + b * zero + c)):
                return -1
            # return (-b+np.sqrt(b**2-4*a*(2*a*(-b/(2*a))**2+2*b*(-b/(2*a))-c)))/(2*a)
        elif (a * (zero ** 2) + b * zero + c < c / 4):
            return -1
            # return (-b+np.sqrt(b**2+4*a*c))/(2*a)
        elif (4 * c < a * (zero**2) + b * zero + c):
            return -1
        return zero

    # Markov Chain Monte Carlo optimizer
    def mcmc_optimizer(metric, initial_state, steps=1000, step_size=10):
        a, b, c = initial_state
        best_a, best_b, best_c = a, b, c
        best_val = metric(a, b, c)
        path = [(a, b, c)]

        for _ in range(steps):
            # Propose new state
            a_new = a + np.random.normal(0, step_size / 1000)
            b_new = b + np.random.normal(0, step_size / 100)
            c_new = c + np.random.normal(0, step_size / 1)
            metric_current = metric(a, b, c)
            metric_new = metric(a=a_new, b=b_new, c=c_new)

            # Acceptance probability
            if metric_new > metric_current:
                accept = True
            else:
                rng = 2 * np.random.rand()
                accept = rng < np.exp(metric_new - metric_current)

            # Update state
            if accept:
                a, b, c = a_new, b_new, c_new
                if metric_new > best_val:
                    best_a, best_b, best_c = a_new, b_new, c_new
                    best_val = metric_new
            path.append((a, b, c))

        return (best_a, best_b, best_c, best_val), path

    # Run optimizer
    initial_guess = (.007, -.079, 45)
    result, trajectory = mcmc_optimizer(metric, initial_guess)
    return result[0], result[1], result[2], result[3]


parabola = find_gate_potential(4, 60)
a, b, c = parabola[0], parabola[1], parabola[2]
metric = parabola[3]


for y_index in range(len(gate)):
    for x_index in range(len(gate[0])):
        if ((-x_index + len(gate[0]) / 2)**2 + (y_index - len(gate) / 2)**2 < radius_gate**2):
            dist_from_edge = x_index - len(gate[0]) / 2 + np.sqrt((radius_gate**2) - (y_index - len(gate) / 2)**2)
            if (-b / (2 * a) < dist_from_edge < metric):
                gate[y_index, x_index] *= 4 * (a * (-b / (2 * a))**2 + b * (-b / (2 * a)) + c) / (a * dist_from_edge**2 + b * dist_from_edge + c)
            elif (dist_from_edge <= (-b / (2 * a))):
                gate[y_index, x_index] *= 4
gate_potential = []
for x in range(0, 101):
    gate_potential.append(const.E_F * x / 300)

etchings = np.array([])
etching_potentials = np.array([])

desired_scale_factor = (np.cos(np.arange(1, 100, 1) / 400))**2
time_scale = 1e-9
start_index = len(space_matrix) // 2 - radius_gate * .8
gate_start = len(space_matrix) // 2 - radius_gate
gate_end = len(space_matrix) // 2 + radius_gate


def convert_to_voltage(eff_potential: np.ndarray) -> np.ndarray:
    # This is a stub. Replace with your effective
    # voltage-to-potential conversion
    return eff_potential
