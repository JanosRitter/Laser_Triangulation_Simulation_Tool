import numpy as np
from .config import (
    DOE_NX, DOE_NY, DOE_FOV_X, DOE_FOV_Y, DOE_CENTER,
    LINE_FOV, LINE_SAMPLES, LINE_AXIS,
    MULTILINE_COUNT, MULTILINE_SPACING
)
from .pose_utils import euler_xyz_to_rotation_matrix


# ============================================================
# 🔴 BASISRICHTUNG
# ============================================================
def get_laser_direction(rx_deg, ry_deg, rz_deg=0.0):
    """
    Berechnet die Basisrichtung des Lasers aus Euler-Winkeln.

    Ausgangsrichtung ist die +z-Achse.
    Rotation wird über pose_utils konsistent mit
    R = Rz @ Ry @ Rx aufgebaut.
    """
    direction = np.array([0.0, 0.0, 1.0], dtype=float)
    R = euler_xyz_to_rotation_matrix(rx_deg, ry_deg, rz_deg)
    dir_vec = R @ direction
    return dir_vec / np.linalg.norm(dir_vec)


# ============================================================
# 🔳 DOE HILFSFUNKTION: ZENTRIERTE INDEZES
# ============================================================
def get_centered_doe_indices(n, include_center=False):
    """
    Erzeugt zentrierte ganzzahlige Indizes für eine DOE-Achse.

    Beispiele
    ---------
    n = 5, include_center=False -> [-2, -1, 0, 1, 2]
    n = 4, include_center=False -> [-2, -1, 1, 2]
    n = 4, include_center=True  -> [-2, -1, 1, 2]
                                    (0 wird nicht hier erzeugt,
                                     sondern separat als Zentralstrahl)

    Hinweise
    --------
    - Bei ungerader Punktzahl liegt der Mittelpunkt bereits im Gitter.
    - Bei gerader Punktzahl existiert kein Gitterpunkt im Zentrum.
    - Falls DOE_CENTER=True und beide Achsen gerade sind, wird der
      Zentralstrahl später separat mit Index (0, 0) ergänzt.
    """
    if n <= 0:
        raise ValueError("DOE-Achsengröße n muss > 0 sein.")

    if n % 2 == 1:
        half = n // 2
        return list(range(-half, half + 1))

    half = n // 2
    return list(range(-half, 0)) + list(range(1, half + 1))


# ============================================================
# 🔳 DOE
# ============================================================
def generate_doe_directions(base_dir):
    directions = []
    indices = []

    angles_x = np.linspace(-DOE_FOV_X / 2, DOE_FOV_X / 2, DOE_NX)
    angles_y = np.linspace(-DOE_FOV_Y / 2, DOE_FOV_Y / 2, DOE_NY)

    idx_x = get_centered_doe_indices(DOE_NX, include_center=DOE_CENTER)
    idx_y = get_centered_doe_indices(DOE_NY, include_center=DOE_CENTER)

    for ax, kx in zip(angles_x, idx_x):
        for ay, ky in zip(angles_y, idx_y):
            # DOE-Abweichungen relativ zur Basisrichtung
            R = euler_xyz_to_rotation_matrix(ay, ax, 0.0)

            dir_vec = R @ base_dir
            dir_vec = dir_vec / np.linalg.norm(dir_vec)

            directions.append(dir_vec)
            indices.append((kx, ky))

    # Zusatz-Zentralstrahl nur dann, wenn beide Achsen gerade sind
    # und DOE_CENTER aktiviert ist
    if DOE_CENTER and (DOE_NX % 2 == 0 and DOE_NY % 2 == 0):
        directions.append(base_dir / np.linalg.norm(base_dir))
        indices.append((0, 0))

    return directions, indices


# ============================================================
# 📏 EINZELLINIEN-LASER
# ============================================================
def generate_line_directions(base_dir):
    directions = []
    weights = []
    ray_indices = []

    angles = np.linspace(-LINE_FOV / 2, LINE_FOV / 2, LINE_SAMPLES)
    sigma = LINE_FOV / 6

    axis = np.cross(base_dir, LINE_AXIS)
    if np.linalg.norm(axis) < 1e-8:
        axis = np.array([0.0, 1.0, 0.0], dtype=float)
    axis = axis / np.linalg.norm(axis)

    for ray_idx, angle in enumerate(angles):
        theta = np.deg2rad(angle)

        K = np.array([
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0]
        ], dtype=float)

        R = np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)

        dir_vec = R @ base_dir
        dir_vec /= np.linalg.norm(dir_vec)

        directions.append(dir_vec)

        weight = np.exp(-(angle**2) / (2 * sigma**2))
        weights.append(weight)

        ray_indices.append(ray_idx)

    return directions, weights, ray_indices


# ============================================================
# 📏📏 MULTILINIEN-LASER
# ============================================================
def generate_multiline_directions(base_dir):
    all_directions = []
    all_weights = []
    all_indices = []

    axis = LINE_AXIS / np.linalg.norm(LINE_AXIS)

    offsets = np.linspace(
        -MULTILINE_SPACING * (MULTILINE_COUNT - 1) / 2,
         MULTILINE_SPACING * (MULTILINE_COUNT - 1) / 2,
         MULTILINE_COUNT
    )

    for line_idx, offset in enumerate(offsets):
        theta = np.deg2rad(offset)

        K = np.array([
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0]
        ], dtype=float)

        R = np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)

        shifted_base = R @ base_dir
        shifted_base /= np.linalg.norm(shifted_base)

        dirs, weights, ray_indices = generate_line_directions(shifted_base)

        all_directions.extend(dirs)
        all_weights.extend(weights)

        for ray_idx in ray_indices:
            all_indices.append((line_idx, ray_idx))

    return all_directions, all_weights, all_indices