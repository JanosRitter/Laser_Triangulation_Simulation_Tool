from .config import (
    MODE, PLANE_MODE,
    LASER_POS, LASER_ROT_X, LASER_ROT_Y, LASER_ROT_Z,
    IMG_WIDTH, IMG_HEIGHT,
    FOCAL_LENGTH, PIXEL_SIZE, SENSOR_WIDTH, SENSOR_HEIGHT,
    DOE_NX, DOE_NY, DOE_FOV_X, DOE_FOV_Y, DOE_CENTER,
    LINE_FOV, LINE_SAMPLES, LINE_AXIS,
    MULTILINE_COUNT, MULTILINE_SPACING,
    PLANE_Z, PLANE_ROT_X, PLANE_ROT_Y,
    SPHERE_CENTER, SPHERE_RADIUS, SPHERE_MISS_MODE, FALLBACK_PLANE_Z,
    SIGMA, NOISE_LEVEL,
    SCAN_MODE, TRAJECTORY_TYPE, SCAN_N_FRAMES,
    SCAN_START_POS, SCAN_END_POS,
    SCAN_ROT_X, SCAN_ROT_Y, SCAN_ROT_Z,
    GRID_NX, GRID_NY, GRID_ORDER,
    EXPLICIT_POSITIONS,
    LOCAL_INCREMENT_SEQUENCE,
    INCLUDE_START_POSE_IN_LOCAL_SEQUENCE,
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
            "rotation_z_deg": LASER_ROT_Z,
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


def _build_trajectory_config():
    """
    Baut die konfigurationsspezifischen Trajectory-Metadaten
    abhängig vom ausgewählten TRAJECTORY_TYPE.
    """
    if TRAJECTORY_TYPE == "linspace":
        return {
            "type": "linspace",
            "num_frames": SCAN_N_FRAMES,
            "start_pos": SCAN_START_POS.tolist(),
            "end_pos": SCAN_END_POS.tolist(),
            "rotation_x_deg": SCAN_ROT_X,
            "rotation_y_deg": SCAN_ROT_Y,
            "rotation_z_deg": SCAN_ROT_Z,
        }

    if TRAJECTORY_TYPE == "grid":
        return {
            "type": "grid",
            "start_pos": SCAN_START_POS.tolist(),
            "end_pos": SCAN_END_POS.tolist(),
            "grid_nx": GRID_NX,
            "grid_ny": GRID_NY,
            "grid_order": GRID_ORDER,
            "rotation_x_deg": SCAN_ROT_X,
            "rotation_y_deg": SCAN_ROT_Y,
            "rotation_z_deg": SCAN_ROT_Z,
        }

    if TRAJECTORY_TYPE == "explicit_list":
        return {
            "type": "explicit_list",
            "num_entries": len(EXPLICIT_POSITIONS),
            "positions_or_poses": [
                list(map(float, p)) for p in EXPLICIT_POSITIONS
            ],
            "note": (
                "Einträge mit Länge 3 werden als Positionen interpretiert und "
                "mit der globalen Laserrotation ergänzt; Einträge mit Länge 6 "
                "werden als vollständige Pose [x,y,z,rx,ry,rz] interpretiert."
            )
        }

    if TRAJECTORY_TYPE == "local_increments":
        return {
            "type": "local_increments",
            "start_pose": [
                float(LASER_POS[0]),
                float(LASER_POS[1]),
                float(LASER_POS[2]),
                float(LASER_ROT_X),
                float(LASER_ROT_Y),
                float(LASER_ROT_Z),
            ],
            "include_start_pose": INCLUDE_START_POSE_IN_LOCAL_SEQUENCE,
            "increments": [
                {
                    "dx_m": float(step["dx"]),
                    "dy_m": float(step["dy"]),
                    "dz_m": float(step["dz"]),
                    "drx_deg": float(step["drx"]),
                    "dry_deg": float(step["dry"]),
                    "drz_deg": float(step["drz"]),
                    "repeat": int(step["repeat"]),
                }
                for step in LOCAL_INCREMENT_SEQUENCE
            ],
            "note": (
                "Die Inkremente sind lokal im aktuellen Laser-Koordinatensystem "
                "definiert und werden sequentiell verkettet."
            )
        }

    return {
        "type": TRAJECTORY_TYPE,
        "note": "Keine spezifische Trajectory-Konfiguration hinterlegt."
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
        "frame_table_file": "frame_table.csv",
        "frames_folder": "frames",
        "trajectory_config": _build_trajectory_config()
    }

    metadata["results_summary"] = {
        "num_frames_planned": num_frames_planned,
        "num_frames_valid": num_frames_valid,
        "num_frames_invalid": num_frames_invalid
    }

    return metadata