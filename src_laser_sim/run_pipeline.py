from .config import (
    MODE, PLANE_MODE,
    LASER_ROT_X, LASER_ROT_Y,
    FRAME_SAVE_MODE,
    SAVE_PREVIEW_SUM,
    CROP_WIDTH, CROP_HEIGHT,
    CROP_ENABLED_MODES
)

from .metadata import build_metadata, build_run_metadata
from .io_utils import (
    get_output_folder,
    save_simulation,
    save_run_metadata,
    save_frame_table
)
from .utils import print_simulation_summary
from .simulation import simulate_frame
from .frame_processing import process_frame_result
from .preview import (
    initialize_preview,
    update_preview,
    save_preview,
    build_preview_disabled_metadata
)


def run_single_simulation(laser_pos):
    """
    Führt eine Einzelbild-Simulation aus und speichert sie wie bisher
    als klassischen Einzel-Output.
    """
    result = simulate_frame(
        laser_pos=laser_pos,
        laser_rot_x=LASER_ROT_X,
        laser_rot_y=LASER_ROT_Y
    )

    folder = get_output_folder(MODE, PLANE_MODE)

    print_simulation_summary(
        result["base_dir"],
        result["visible_points"],
        result["num_missing"],
        folder
    )

    metadata = build_metadata(
        num_visible=result["num_visible"],
        num_missing=result["num_missing"]
    )

    print(result["ground_truth_points"])

    save_simulation(
        result["image"],
        metadata,
        result["ground_truth_points"],
        folder
    )

    print("\n📊 Ergebnis:")
    print(f"  ✅ Sichtbar: {result['num_visible']}")
    print(f"  ❌ Verworfen: {result['num_missing']}")
    print(f"  💾 Gespeichert in: {folder}")


def run_trajectory_simulation(positions):
    """
    Führt eine Trajektorien-Simulation mit mehreren Laserpositionen aus.
    """
    print(f"\n🚗 Trajektorie mit {len(positions)} Positionen")

    folder = get_output_folder(MODE, PLANE_MODE)
    frame_table = []

    preview_sum = None
    if SAVE_PREVIEW_SUM:
        first_result = simulate_frame(
            laser_pos=positions[0],
            laser_rot_x=LASER_ROT_X,
            laser_rot_y=LASER_ROT_Y
        )
        preview_sum = initialize_preview(first_result)

    cropping_active = MODE in CROP_ENABLED_MODES
    save_full_images = FRAME_SAVE_MODE in ["full", "both"]
    save_crops = FRAME_SAVE_MODE in ["crop", "both"] and cropping_active

    for frame_idx, laser_pos in enumerate(positions):
        result = simulate_frame(
            laser_pos=laser_pos,
            laser_rot_x=LASER_ROT_X,
            laser_rot_y=LASER_ROT_Y
        )

        processed = process_frame_result(
            result=result,
            frame_idx=frame_idx,
            laser_pos=laser_pos,
            folder=folder,
            save_full_images=save_full_images,
            save_crops=save_crops,
            crop_width=CROP_WIDTH,
            crop_height=CROP_HEIGHT
        )

        if processed["has_signal"] and SAVE_PREVIEW_SUM:
            preview_sum = update_preview(preview_sum, result)

        frame_table.append(processed["frame_row"])

        print(
            f"Frame {frame_idx:03d}: "
            f"LASER_POS={laser_pos} | "
            f"sichtbar={result['num_visible']} | "
            f"verworfen={result['num_missing']} | "
            f"status={processed['status']}"
        )

    num_frames_planned = len(frame_table)
    num_frames_valid = sum(1 for row in frame_table if row["status"] == "valid")
    num_frames_invalid = num_frames_planned - num_frames_valid

    run_metadata = build_run_metadata(
        num_frames_planned=num_frames_planned,
        num_frames_valid=num_frames_valid,
        num_frames_invalid=num_frames_invalid
    )

    if SAVE_PREVIEW_SUM and preview_sum is not None:
        run_metadata["preview"] = save_preview(
            preview_sum=preview_sum,
            folder=folder,
            save_png=True
        )
    else:
        run_metadata["preview"] = build_preview_disabled_metadata()

    run_metadata["storage"] = {
        "frame_save_mode": FRAME_SAVE_MODE,
        "cropping_active_for_mode": cropping_active,
        "crop_width": CROP_WIDTH,
        "crop_height": CROP_HEIGHT
    }

    save_run_metadata(run_metadata, folder)
    save_frame_table(frame_table, folder)

    print("\n📊 Trajektorien-Zusammenfassung:")
    print(f"  Gesamtframes: {num_frames_planned}")
    print(f"  Frames mit Signal: {num_frames_valid}")
    print(f"  Frames ohne Signal: {num_frames_invalid}")
    print(f"  Cropping aktiv: {save_crops}")
    print(f"  Preview gespeichert: {SAVE_PREVIEW_SUM}")
    print(f"  💾 Gespeichert in: {folder}")