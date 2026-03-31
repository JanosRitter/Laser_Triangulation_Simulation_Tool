import numpy as np

from .io_utils import save_preview_sum


def initialize_preview(first_result):
    """
    Initialisiert die Preview-Summe anhand der Form des rauschfreien Signalbildes.
    """
    return np.zeros_like(first_result["signal_image"])


def update_preview(preview_sum, result):
    """
    Addiert das rauschfreie Signalbild eines Frames auf die Preview-Summe.
    """
    preview_sum += result["signal_image"]
    return preview_sum


def save_preview(preview_sum, folder, save_png=True):
    """
    Speichert die Preview-Summe und liefert ein Metadaten-Dict zurück.
    """
    preview_files = save_preview_sum(preview_sum, folder, save_png=save_png)

    return {
        "enabled": True,
        "source": "signal_image_without_noise",
        "preview_npy_file": preview_files["preview_npy_file"],
        "preview_png_file": preview_files["preview_png_file"]
    }


def build_preview_disabled_metadata():
    """
    Metadaten für den Fall, dass keine Preview gespeichert wird.
    """
    return {
        "enabled": False
    }