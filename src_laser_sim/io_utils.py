import os
import json
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
    Speichert:
    - Simulationsbild als .npy
    - Simulationsbild als .png
    - Metadaten als .json
    - Ground Truth Punkte als .npy

    Parameters
    ----------
    image : np.ndarray
        Bildarray
    metadata : dict
        Metadaten / Randbedingungen der Simulation
    ground_truth_points : np.ndarray
        Array der Form (n, 5) mit [x, y, z, u, v]
    folder : str
        Zielordner
    """
    np.save(os.path.join(folder, "laser_sim.npy"), image)
    plt.imsave(os.path.join(folder, "laser_sim.png"), image, cmap="gray")

    with open(os.path.join(folder, "simulation_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    np.save(os.path.join(folder, "ground_truth_points.npy"), ground_truth_points)