import numpy as np

from src_laser_sim.config import (
    MODE, PLANE_MODE,
    LASER_POS, LASER_ROT_X, LASER_ROT_Y,
    IMG_WIDTH, IMG_HEIGHT
)

from src_laser_sim.metadata import build_metadata

from src_laser_sim.laser import (
    get_laser_direction,
    generate_doe_directions,
    generate_line_directions,
    generate_multiline_directions
)

from src_laser_sim.plane import intersect_plane
from src_laser_sim.projection import (
    is_visible,
    project,
    add_gaussian_spot,
    add_noise,
    normalize_image
)

from src_laser_sim.io_utils import get_output_folder, save_simulation
from src_laser_sim.utils import print_simulation_summary


def main():
    print("🔧 Lasertriangulation Simulation gestartet")

    # ---------------------------
    # Basisrichtung Laser
    # ---------------------------
    base_dir = get_laser_direction(LASER_ROT_X, LASER_ROT_Y)

    # ---------------------------
    # Bild initialisieren
    # ---------------------------
    image = np.zeros((IMG_HEIGHT, IMG_WIDTH), dtype=float)
    visible_points = []
    ground_truth_rows = []
    missing_points = 0

    # ---------------------------
    # STRAHLEN DEFINIEREN
    # ---------------------------
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

    # ---------------------------
    # HAUPTSCHLEIFE
    # ---------------------------
    for i, d in enumerate(directions):
        p = intersect_plane(LASER_POS, d)

        if p is None:
            missing_points += 1
            continue

        if is_visible(p):
            px, py = project(p)
            add_gaussian_spot(image, px, py, intensity=weights[i])

            visible_points.append({
                "point_3D": p.tolist(),
                "pixel": [px, py]
            })

            meta = ray_metadata[i]

            if MODE == "Point":
                col0 = meta["ray_idx"]
                col1 = -1

            elif MODE == "DOE_Square":
                col0 = meta["doe_idx_x"]
                col1 = meta["doe_idx_y"]

            elif MODE == "Line_Laser":
                col0 = meta["ray_idx"]
                col1 = -1

            elif MODE == "Multi_Line_Laser":
                col0 = meta["line_idx"]
                col1 = meta["ray_idx"]

            else:
                raise ValueError(f"Unbekannter MODE: {MODE}")

            ground_truth_rows.append([col0, col1, p[0], p[1], p[2], px, py])

        else:
            missing_points += 1

    # ---------------------------
    # NORMALISIERUNG (für Linienlaser)
    # ---------------------------
    if MODE in ["Line_Laser", "Multi_Line_Laser"]:
        image = normalize_image(image)

    # ---------------------------
    # NOISE
    # ---------------------------
    image = add_noise(image)

    # ---------------------------
    # OUTPUT-ORDNER
    # ---------------------------
    folder = get_output_folder(MODE, PLANE_MODE)

    # ---------------------------
    # SUMMARY PRINT
    # ---------------------------
    print_simulation_summary(
        base_dir,
        visible_points,
        missing_points,
        folder
    )

    # ---------------------------
    # GROUND TRUTH ARRAY
    # ---------------------------
    if len(ground_truth_rows) == 0:
        ground_truth_points = np.empty((0, 7), dtype=np.float32)
    else:
        ground_truth_points = np.array(ground_truth_rows, dtype=np.float32)
    
        # Sortierung nach index_0, dann index_1
        ground_truth_points = ground_truth_points[
            np.lexsort((ground_truth_points[:, 1], ground_truth_points[:, 0]))
        ]

    # ---------------------------
    # METADATA
    # ---------------------------
    metadata = build_metadata(
    num_visible=len(visible_points),
    num_missing=missing_points
    )

    # ---------------------------
    # SPEICHERN
    # ---------------------------
    print(ground_truth_points)
    save_simulation(image, metadata, ground_truth_points, folder)

    print("\n📊 Ergebnis:")
    print(f"  ✅ Sichtbar: {len(visible_points)}")
    print(f"  ❌ Verworfen: {missing_points}")
    print(f"  💾 Gespeichert in: {folder}")


if __name__ == "__main__":
    main()