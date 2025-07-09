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

radius_gate = int(50e-6 / const.l)

x = np.arange(0, int(200e-6 / const.l), 1)
y = np.arange(0, int(150e-6 / const.l), 1)

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


U_etching9 = 0.3
U_etching8 = U_etching9 + 0.3
U_etching7 = U_etching8 + 0.3
U_etching6 = U_etching7 + 0.3
U_etching5 = U_etching6 + 0.3
U_etching4 = U_etching5 + 0.3
U_etching3 = U_etching4 + 0.3
U_etching2 = U_etching3 + 0.3
U_etching1 = U_etching2 + 0.3
# shallow etching region 1
etched1 = np.logical_xor(
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate),
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(5e-6 / const.l)),
).astype(int)
etched1[Y >= y[len(y) // 2]] = 0
etched1[boundary == 1] = 0
etched1_indices = np.array(np.where(etched1 == 1)).T

# shallow etching region 2
etched2 = np.logical_xor(
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(5e-6 / const.l)),
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(9e-6 / const.l)),
).astype(int)
etched2[Y >= y[len(y) // 2]] = 0
etched2[boundary == 1] = 0
etched2[etched1 == 1] = 0
etched2_indices = np.array(np.where(etched2 == 1)).T

# shallow etching region 3
etched3 = np.logical_xor(
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(9e-6 / const.l)),
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(11e-6 / const.l)),
).astype(int)
etched3[Y >= y[len(y) // 2]] = 0
etched3[boundary == 1] = 0
etched3[etched1 == 1] = 0
etched3[etched2 == 1] = 0
etched3_indices = np.array(np.where(etched3 == 1)).T

# shallow etching region 4
etched4 = np.logical_xor(
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(11e-6 / const.l)),
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(13e-6 / const.l)),
).astype(int)
etched4[Y >= y[len(y) // 2]] = 0
etched4[boundary == 1] = 0
etched4[etched1 == 1] = 0
etched4[etched2 == 1] = 0
etched4[etched3 == 1] = 0
etched4_indices = np.array(np.where(etched4 == 1)).T

# shallow etching region 5
etched5 = np.logical_xor(
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(13e-6 / const.l)),
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(15e-6 / const.l)),
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
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(15e-6 / const.l)),
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(17e-6 / const.l)),
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
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(17e-6 / const.l)),
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(19e-6 / const.l)),
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
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(19e-6 / const.l)),
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(21e-6 / const.l)),
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
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(21e-6 / const.l)),
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(23e-6 / const.l)),
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
    true_circle_in(Y, X, y[len(y) // 2], x[len(x) // 2], radius_gate - int(25e-6 / const.l)),
).astype(int)
gate[Y >= y[len(y) // 2]] = 0
gate[boundary == 1] = 0
gate_indices = np.array(np.where(gate == 1)).T
gate_potential=[]
for x in range(0,101):
    gate_potential.append(const.E_F*x/100)

etchings=np.array([etched1,etched2,etched3,etched4,etched5,etched6,etched7,etched8,etched9])
etching_potentials=np.array([U_etching1,U_etching2,U_etching3,U_etching4,U_etching5,U_etching6,U_etching7,U_etching8,U_etching9])

desired_scale_factor=(np.cos(np.arange(1,100,1)/400))**2