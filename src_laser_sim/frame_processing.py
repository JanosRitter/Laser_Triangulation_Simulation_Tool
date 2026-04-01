import numpy as np

from .io_utils import (
    save_frame_result,
    crop_image_around_point,
    save_frame_crop
)


def extract_primary_spot_from_ground_truth(ground_truth_points):
    """
    Verwendet den ersten Ground-Truth-Punkt als primären Spot.
    Das ist insbesondere für MODE='Point' passend.
    """
    if ground_truth_points is None or len(ground_truth_points) == 0:
        return None

    px = float(ground_truth_points[0, 5])
    py = float(ground_truth_points[0, 6])

    return px, py


def get_frame_status(result):
    """
    Bestimmt den einfachen Frame-Status auf Basis der Sichtbarkeit.
    """
    has_signal = result["num_visible"] > 0
    status = "valid" if has_signal else "invalid"
    return has_signal, status


def process_frame_result(
    result,
    frame_idx,
    laser_pose,
    folder,
    save_full_images,
    save_crops,
    crop_width,
    crop_height
):
    """
    Verarbeitet einen simulierten Frame für Speicherung und frame_table.

    Parameters
    ----------
    result : dict
        Ausgabe von simulate_frame(...)
    frame_idx : int
        Index des Frames
    laser_pose : np.ndarray, shape (6,)
        [x, y, z, rx, ry, rz]
    folder : str
        Zielordner
    save_full_images : bool
    save_crops : bool
    crop_width : int
    crop_height : int

    Rückgabe:
    {
        "has_signal": bool,
        "status": str,
        "spot": (px, py) oder None,
        "frame_row": {...}
    }
    """
    laser_pose = np.asarray(laser_pose, dtype=float)
    if laser_pose.shape != (6,):
        raise ValueError("laser_pose muss die Form (6,) haben.")

    has_signal, status = get_frame_status(result)

    image_npy_file = ""
    image_png_file = ""
    ground_truth_file = ""

    crop_npy_file = ""
    crop_png_file = ""
    crop_x0 = ""
    crop_y0 = ""
    out_crop_width = ""
    out_crop_height = ""
    local_px = ""
    local_py = ""
    crop_clipped = ""

    full_px = ""
    full_py = ""

    spot = None

    if has_signal:
        spot = extract_primary_spot_from_ground_truth(result["ground_truth_points"])
        if spot is not None:
            full_px, full_py = spot

        if save_full_images:
            saved_files = save_frame_result(
                image=result["image"],
                ground_truth_points=result["ground_truth_points"],
                frame_idx=frame_idx,
                folder=folder,
                save_png=True
            )
            image_npy_file = saved_files["image_npy_file"]
            image_png_file = saved_files["image_png_file"]
            ground_truth_file = saved_files["ground_truth_file"]

        else:
            # Ground truth trotzdem speichern, auch wenn kein Vollbild gespeichert wird.
            # Dazu wird wie bisher ein Dummy-Bild über save_frame_result abgewickelt.
            saved_files = save_frame_result(
                image=np.zeros((1, 1), dtype=float),
                ground_truth_points=result["ground_truth_points"],
                frame_idx=frame_idx,
                folder=folder,
                save_png=False
            )
            ground_truth_file = saved_files["ground_truth_file"]

        if save_crops and spot is not None:
            crop_info = crop_image_around_point(
                image=result["image"],
                center_px=spot[0],
                center_py=spot[1],
                crop_width=crop_width,
                crop_height=crop_height
            )

            crop_files = save_frame_crop(
                crop_image=crop_info["crop_image"],
                frame_idx=frame_idx,
                folder=folder,
                save_png=True
            )

            crop_npy_file = crop_files["crop_npy_file"]
            crop_png_file = crop_files["crop_png_file"]
            crop_x0 = crop_info["crop_x0"]
            crop_y0 = crop_info["crop_y0"]
            out_crop_width = crop_info["crop_width"]
            out_crop_height = crop_info["crop_height"]
            local_px = crop_info["local_px"]
            local_py = crop_info["local_py"]
            crop_clipped = crop_info["crop_clipped"]

    frame_row = {
        "frame_idx": frame_idx,

        "laser_x": float(laser_pose[0]),
        "laser_y": float(laser_pose[1]),
        "laser_z": float(laser_pose[2]),
        "laser_rx": float(laser_pose[3]),
        "laser_ry": float(laser_pose[4]),
        "laser_rz": float(laser_pose[5]),

        "num_visible": int(result["num_visible"]),
        "num_missing": int(result["num_missing"]),
        "status": status,

        "full_px": full_px,
        "full_py": full_py,

        "image_npy_file": image_npy_file,
        "image_png_file": image_png_file,
        "ground_truth_file": ground_truth_file,

        "crop_npy_file": crop_npy_file,
        "crop_png_file": crop_png_file,
        "crop_x0": crop_x0,
        "crop_y0": crop_y0,
        "crop_width": out_crop_width,
        "crop_height": out_crop_height,
        "local_px": local_px,
        "local_py": local_py,
        "crop_clipped": crop_clipped
    }

    return {
        "has_signal": has_signal,
        "status": status,
        "spot": spot,
        "frame_row": frame_row
    }