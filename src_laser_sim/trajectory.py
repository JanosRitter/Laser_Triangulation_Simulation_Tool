import numpy as np

from .config import (
    SCAN_MODE,
    TRAJECTORY_TYPE,
    SCAN_N_FRAMES,
    SCAN_START_POS,
    SCAN_END_POS,
    EXPLICIT_POSITIONS,
    LASER_POS,
    GRID_NX,
    GRID_NY,
    GRID_ORDER
)


def generate_trajectory():
    """
    Gibt ein Array der Form (N, 3) zurück.
    Jede Zeile ist eine Laserposition [x, y, z].

    Verhalten:
    - SCAN_MODE = "single"      -> genau eine Position: LASER_POS
    - SCAN_MODE = "trajectory"  -> mehrere Positionen gemäß TRAJECTORY_TYPE
    """
    if SCAN_MODE == "single":
        return np.array([LASER_POS], dtype=float)

    if SCAN_MODE != "trajectory":
        raise ValueError(f"Unbekannter SCAN_MODE: {SCAN_MODE}")

    if TRAJECTORY_TYPE == "linspace":
        if SCAN_N_FRAMES < 1:
            raise ValueError("SCAN_N_FRAMES muss >= 1 sein.")

        alphas = np.linspace(0.0, 1.0, SCAN_N_FRAMES)
        positions = np.array([
            SCAN_START_POS + a * (SCAN_END_POS - SCAN_START_POS)
            for a in alphas
        ], dtype=float)
        return positions

    if TRAJECTORY_TYPE == "explicit_list":
        if len(EXPLICIT_POSITIONS) == 0:
            raise ValueError("EXPLICIT_POSITIONS ist leer.")

        positions = np.array(EXPLICIT_POSITIONS, dtype=float)

        if positions.ndim != 2 or positions.shape[1] != 3:
            raise ValueError(
                "EXPLICIT_POSITIONS muss eine Liste von 3D-Koordinaten sein."
            )

        return positions

    if TRAJECTORY_TYPE == "grid":
        if GRID_NX < 1 or GRID_NY < 1:
            raise ValueError("GRID_NX und GRID_NY müssen >= 1 sein.")

        xs = np.linspace(SCAN_START_POS[0], SCAN_END_POS[0], GRID_NX)
        ys = np.linspace(SCAN_START_POS[1], SCAN_END_POS[1], GRID_NY)
        zs = np.linspace(SCAN_START_POS[2], SCAN_END_POS[2], GRID_NY)

        positions = []

        for row_idx, (y, z) in enumerate(zip(ys, zs)):
            if GRID_ORDER == "row_major":
                x_iter = xs

            elif GRID_ORDER == "serpentine":
                x_iter = xs if row_idx % 2 == 0 else xs[::-1]

            else:
                raise ValueError(f"Unbekannter GRID_ORDER: {GRID_ORDER}")

            for x in x_iter:
                positions.append([x, y, z])

        return np.array(positions, dtype=float)

    raise ValueError(f"Unbekannter TRAJECTORY_TYPE: {TRAJECTORY_TYPE}")