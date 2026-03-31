import os
import json
import csv
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt


def get_output_folder(mode, plane_mode):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_folder = os.path.join("Simulation_outputs", mode, plane_mode, timestamp)
    os.makedirs(base_folder, exist_ok=True)
    return base_folder


def save_simulation(image, metadata, ground_truth_points, folder):
    """
    Speichert einen einzelnen Simulationslauf:
    - Simulationsbild als .npy
    - Simulationsbild als .png
    - Metadaten als .json
    - Ground Truth Punkte als .npy
    """
    np.save(os.path.join(folder, "laser_sim.npy"), image)
    plt.imsave(os.path.join(folder, "laser_sim.png"), image, cmap="gray")

    with open(os.path.join(folder, "simulation_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    np.save(os.path.join(folder, "ground_truth_points.npy"), ground_truth_points)


def ensure_subfolder(folder, subfolder_name):
    subfolder = os.path.join(folder, subfolder_name)
    os.makedirs(subfolder, exist_ok=True)
    return subfolder


def save_run_metadata(run_metadata, folder):
    filepath = os.path.join(folder, "run_metadata.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(run_metadata, f, indent=4)


def save_frame_table(frame_table, folder):
    filepath = os.path.join(folder, "frame_table.csv")

    if len(frame_table) == 0:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write("")
        return

    fieldnames = list(frame_table[0].keys())

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(frame_table)


def crop_image_around_point(image, center_px, center_py, crop_width, crop_height):
    """
    Schneidet einen Crop um einen bekannten Punkt aus.

    Rückgabe:
    {
        "crop_image": ...,
        "crop_x0": ...,
        "crop_y0": ...,
        "crop_width": ...,
        "crop_height": ...,
        "local_px": ...,
        "local_py": ...,
        "crop_clipped": ...
    }
    """
    img_h, img_w = image.shape

    center_px = float(center_px)
    center_py = float(center_py)

    half_w = crop_width // 2
    half_h = crop_height // 2

    x0 = int(np.floor(center_px)) - half_w
    y0 = int(np.floor(center_py)) - half_h
    x1 = x0 + crop_width
    y1 = y0 + crop_height

    crop_clipped = False

    if x0 < 0:
        x0 = 0
        x1 = min(crop_width, img_w)
        crop_clipped = True

    if y0 < 0:
        y0 = 0
        y1 = min(crop_height, img_h)
        crop_clipped = True

    if x1 > img_w:
        x1 = img_w
        x0 = max(0, img_w - crop_width)
        crop_clipped = True

    if y1 > img_h:
        y1 = img_h
        y0 = max(0, img_h - crop_height)
        crop_clipped = True

    crop = image[y0:y1, x0:x1].copy()

    local_px = center_px - x0
    local_py = center_py - y0

    return {
        "crop_image": crop,
        "crop_x0": int(x0),
        "crop_y0": int(y0),
        "crop_width": int(crop.shape[1]),
        "crop_height": int(crop.shape[0]),
        "local_px": float(local_px),
        "local_py": float(local_py),
        "crop_clipped": bool(crop_clipped),
    }


def save_frame_result(image, ground_truth_points, frame_idx, folder, save_png=True):
    """
    Speichert einen einzelnen Frame innerhalb eines Scanlaufs.

    Struktur:
    folder/
      frames/
        frame_000000.npy
        frame_000000.png
        frame_000000_ground_truth.npy
    """
    frames_folder = ensure_subfolder(folder, "frames")

    image_npy_name = f"frame_{frame_idx:06d}.npy"
    image_png_name = f"frame_{frame_idx:06d}.png"
    gt_name = f"frame_{frame_idx:06d}_ground_truth.npy"

    image_npy_path = os.path.join(frames_folder, image_npy_name)
    image_png_path = os.path.join(frames_folder, image_png_name)
    gt_path = os.path.join(frames_folder, gt_name)

    np.save(image_npy_path, image)
    np.save(gt_path, ground_truth_points)

    if save_png:
        plt.imsave(image_png_path, image, cmap="gray")

    return {
        "image_npy_file": os.path.join("frames", image_npy_name),
        "image_png_file": os.path.join("frames", image_png_name) if save_png else "",
        "ground_truth_file": os.path.join("frames", gt_name),
    }


def save_frame_crop(crop_image, frame_idx, folder, save_png=True):
    """
    Speichert einen Crop innerhalb eines Scanlaufs.

    Struktur:
    folder/
      crops/
        crop_000000.npy
        crop_000000.png
    """
    crops_folder = ensure_subfolder(folder, "crops")

    crop_npy_name = f"crop_{frame_idx:06d}.npy"
    crop_png_name = f"crop_{frame_idx:06d}.png"

    crop_npy_path = os.path.join(crops_folder, crop_npy_name)
    crop_png_path = os.path.join(crops_folder, crop_png_name)

    np.save(crop_npy_path, crop_image)

    if save_png:
        plt.imsave(crop_png_path, crop_image, cmap="gray")

    return {
        "crop_npy_file": os.path.join("crops", crop_npy_name),
        "crop_png_file": os.path.join("crops", crop_png_name) if save_png else "",
    }


def save_preview_sum(preview_image, folder, save_png=True):
    """
    Speichert das überlagerte Vorschaubild eines gesamten Scanlaufs.
    """
    preview_npy_path = os.path.join(folder, "preview_sum.npy")
    np.save(preview_npy_path, preview_image)

    preview_png_file = ""
    if save_png:
        preview_png_path = os.path.join(folder, "preview_sum.png")
        max_val = np.max(preview_image)

        if max_val > 0:
            preview_norm = preview_image / max_val * 255.0
        else:
            preview_norm = preview_image.copy()

        plt.imsave(preview_png_path, preview_norm, cmap="gray")
        preview_png_file = "preview_sum.png"

    return {
        "preview_npy_file": "preview_sum.npy",
        "preview_png_file": preview_png_file,
    }