from .config import (
    MODE, PLANE_MODE,
    LASER_POS, LASER_ROT_X, LASER_ROT_Y,
    IMG_WIDTH, IMG_HEIGHT,
    FOCAL_LENGTH, PIXEL_SIZE, SENSOR_WIDTH, SENSOR_HEIGHT,
    DOE_NX, DOE_NY, DOE_FOV_X, DOE_FOV_Y, DOE_CENTER,
    LINE_FOV, LINE_SAMPLES, LINE_AXIS,
    MULTILINE_COUNT, MULTILINE_SPACING,
    PLANE_Z, PLANE_ROT_X, PLANE_ROT_Y,
    SPHERE_CENTER, SPHERE_RADIUS, SPHERE_MISS_MODE, FALLBACK_PLANE_Z,
    SIGMA, NOISE_LEVEL,
    SCAN_MODE, TRAJECTORY_TYPE, SCAN_N_FRAMES,
    SCAN_START_POS, SCAN_END_POS
)


def _build_common_metadata():
    """
    Gemeinsame Metadaten für Einzelbild- und Run-Speicherung.
    """
    return {
        "simulation": {
            "mode": MODE,
            "plane_mode": PLANE_MODE
        },
        "camera": {
            "img_width": IMG_WIDTH,
            "img_height": IMG_HEIGHT,
            "focal_length": FOCAL_LENGTH,
            "pixel_size": PIXEL_SIZE,
            "sensor_width": SENSOR_WIDTH,
            "sensor_height": SENSOR_HEIGHT
        },
        "laser": {
            "position": LASER_POS.tolist(),
            "rotation_x_deg": LASER_ROT_X,
            "rotation_y_deg": LASER_ROT_Y,
            "line_axis": LINE_AXIS.tolist()
        },
        "doe": {
            "nx": DOE_NX,
            "ny": DOE_NY,
            "fov_x_deg": DOE_FOV_X,
            "fov_y_deg": DOE_FOV_Y,
            "center_point": DOE_CENTER
        },
        "line_laser": {
            "fov_deg": LINE_FOV,
            "samples": LINE_SAMPLES
        },
        "multiline_laser": {
            "count": MULTILINE_COUNT,
            "spacing_deg": MULTILINE_SPACING
        },
        "plane": {
            "z": PLANE_Z,
            "rot_x_deg": PLANE_ROT_X,
            "rot_y_deg": PLANE_ROT_Y
        },
        "sphere": {
            "center": SPHERE_CENTER.tolist(),
            "radius": SPHERE_RADIUS,
            "miss_mode": SPHERE_MISS_MODE,
            "fallback_plane_z": FALLBACK_PLANE_Z
        },
        "rendering": {
            "sigma": SIGMA,
            "noise_level": NOISE_LEVEL
        },
        "ground_truth": {
            "columns": ["index_0", "index_1", "x", "y", "z", "u", "v"],
            "index_meaning": {
                "Point": ["ray_idx", "unused"],
                "DOE_Square": ["doe_idx_x", "doe_idx_y"],
                "Line_Laser": ["ray_idx", "unused"],
                "Multi_Line_Laser": ["line_idx", "ray_idx"]
            },
            "special_values": {
                "unused": -1
            },
            "index_convention": {
                "DOE_Square": (
                    "zentrierte signierte DOE-Indizes relativ zum Musterzentrum; "
                    "Zentralstrahl = (0, 0), falls als Zusatzstrahl vorhanden"
                )
            }
        }
    }


def build_metadata(num_visible, num_missing):
    """
    Metadaten für einen einzelnen Simulationslauf.
    """
    metadata = _build_common_metadata()
    metadata["ground_truth"]["file"] = "ground_truth_points.npy"
    metadata["results_summary"] = {
        "num_visible": num_visible,
        "num_missing": num_missing
    }
    return metadata


def build_run_metadata(num_frames_planned, num_frames_valid, num_frames_invalid):
    """
    Metadaten für einen gesamten Scanlauf / eine Trajektorie.
    """
    metadata = _build_common_metadata()

    metadata["scan"] = {
        "scan_mode": SCAN_MODE,
        "trajectory_type": TRAJECTORY_TYPE,
        "num_frames_planned": num_frames_planned,
        "scan_n_frames_config": SCAN_N_FRAMES,
        "start_pos": SCAN_START_POS.tolist(),
        "end_pos": SCAN_END_POS.tolist(),
        "frame_table_file": "frame_table.csv",
        "frames_folder": "frames"
    }

    metadata["results_summary"] = {
        "num_frames_planned": num_frames_planned,
        "num_frames_valid": num_frames_valid,
        "num_frames_invalid": num_frames_invalid
    }

    return metadata