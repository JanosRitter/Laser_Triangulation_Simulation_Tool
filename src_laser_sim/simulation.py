import numpy as np

from .config import MODE, IMG_WIDTH, IMG_HEIGHT
from .laser import (
    get_laser_direction,
    generate_doe_directions,
    generate_line_directions,
    generate_multiline_directions
)
from .plane import intersect_plane
from .projection import (
    is_visible,
    project,
    add_gaussian_spot,
    add_noise,
    normalize_image
)


def build_rays(base_dir):
    if MODE == "Point":
        directions = [base_dir]
        weights = np.ones(len(directions))
        ray_metadata = [{"ray_idx": 0}]

    elif MODE == "DOE_Square":
        directions, doe_indices = generate_doe_directions(base_dir)
        weights = np.ones(len(directions))
        ray_metadata = [
            {
                "doe_idx_x": int(idx_x),
                "doe_idx_y": int(idx_y)
            }
            for idx_x, idx_y in doe_indices
        ]

    elif MODE == "Line_Laser":
        directions, weights, ray_indices = generate_line_directions(base_dir)
        ray_metadata = [{"ray_idx": int(ray_idx)} for ray_idx in ray_indices]

    elif MODE == "Multi_Line_Laser":
        directions, weights, multiline_indices = generate_multiline_directions(base_dir)
        ray_metadata = [
            {
                "line_idx": int(line_idx),
                "ray_idx": int(ray_idx)
            }
            for line_idx, ray_idx in multiline_indices
        ]

    else:
        raise ValueError(f"Unbekannter MODE: {MODE}")

    return directions, weights, ray_metadata


def build_ground_truth_row(mode, meta, point_3d, px, py):
    if mode == "Point":
        col0 = meta["ray_idx"]
        col1 = -1

    elif mode == "DOE_Square":
        col0 = meta["doe_idx_x"]
        col1 = meta["doe_idx_y"]

    elif mode == "Line_Laser":
        col0 = meta["ray_idx"]
        col1 = -1

    elif mode == "Multi_Line_Laser":
        col0 = meta["line_idx"]
        col1 = meta["ray_idx"]

    else:
        raise ValueError(f"Unbekannter MODE: {mode}")

    return [col0, col1, point_3d[0], point_3d[1], point_3d[2], px, py]


def simulate_frame(laser_pos, laser_rot_x, laser_rot_y, laser_rot_z=0.0):
    """
    Simuliert einen einzelnen Frame.

    Parameters
    ----------
    laser_pos : np.ndarray shape (3,)
        Laserposition im Kamerakoordinatensystem
    laser_rot_x, laser_rot_y, laser_rot_z : float
        Euler-Winkel des Lasers in Grad

    Hinweis
    -------
    laser_rot_z wird ab jetzt berücksichtigt.
    """
    laser_pos = np.asarray(laser_pos, dtype=float)
    if laser_pos.shape != (3,):
        raise ValueError("laser_pos muss die Form (3,) haben.")

    base_dir = get_laser_direction(laser_rot_x, laser_rot_y, laser_rot_z)

    image = np.zeros((IMG_HEIGHT, IMG_WIDTH), dtype=float)
    visible_points = []
    ground_truth_rows = []
    missing_points = 0

    directions, weights, ray_metadata = build_rays(base_dir)

    for i, d in enumerate(directions):
        p = intersect_plane(laser_pos, d)

        if p is None:
            missing_points += 1
            continue

        if not is_visible(p):
            missing_points += 1
            continue

        px, py = project(p)
        add_gaussian_spot(image, px, py, intensity=weights[i])

        visible_points.append({
            "point_3D": p.tolist(),
            "pixel": [px, py]
        })

        row = build_ground_truth_row(MODE, ray_metadata[i], p, px, py)
        ground_truth_rows.append(row)

    if MODE in ["Line_Laser", "Multi_Line_Laser"]:
        image = normalize_image(image)

    # Rauschfreie Signalversion für Preview-Summe etc.
    signal_image = image.copy()

    # Finales Bild für Datensatz mit Rauschen
    image = add_noise(image)

    if len(ground_truth_rows) == 0:
        ground_truth_points = np.empty((0, 7), dtype=np.float32)
    else:
        ground_truth_points = np.array(ground_truth_rows, dtype=np.float32)
        ground_truth_points = ground_truth_points[
            np.lexsort((ground_truth_points[:, 1], ground_truth_points[:, 0]))
        ]

    return {
        "image": image,
        "signal_image": signal_image,
        "base_dir": base_dir,
        "visible_points": visible_points,
        "ground_truth_points": ground_truth_points,
        "num_visible": len(visible_points),
        "num_missing": missing_points
    }