import numpy as np

from .config import (
    SCAN_MODE,
    TRAJECTORY_TYPE,
    SCAN_N_FRAMES,
    SCAN_START_POS,
    SCAN_END_POS,
    SCAN_ROT_X,
    SCAN_ROT_Y,
    SCAN_ROT_Z,
    EXPLICIT_POSITIONS,
    LASER_POS,
    LASER_ROT_X,
    LASER_ROT_Y,
    LASER_ROT_Z,
    GRID_NX,
    GRID_NY,
    GRID_ORDER,
    LOCAL_INCREMENT_SEQUENCE,
    INCLUDE_START_POSE_IN_LOCAL_SEQUENCE,
)
from .pose_utils import (
    pose_array_to_transform,
    transform_to_pose_array,
    apply_local_increment,
)


def _ensure_pose_array(positions: np.ndarray) -> np.ndarray:
    """
    Wandelt (N,3) → (N,6) um, falls nötig.
    """
    if positions.shape[1] == 6:
        return positions

    if positions.shape[1] != 3:
        raise ValueError("Positions müssen Shape (N,3) oder (N,6) haben.")

    rotations = np.zeros((positions.shape[0], 3), dtype=float)
    return np.hstack([positions, rotations])


def _build_single_pose() -> np.ndarray:
    """
    Baut die Einzelpose aus den Laser-Grundparametern.
    """
    return np.array([[
        LASER_POS[0],
        LASER_POS[1],
        LASER_POS[2],
        LASER_ROT_X,
        LASER_ROT_Y,
        LASER_ROT_Z,
    ]], dtype=float)


def _build_linspace_poses() -> np.ndarray:
    """
    Erzeugt Posen entlang einer linearen Translation mit konstanter Rotation.
    """
    if SCAN_N_FRAMES < 1:
        raise ValueError("SCAN_N_FRAMES muss >= 1 sein.")

    alphas = np.linspace(0.0, 1.0, SCAN_N_FRAMES)

    positions = np.array([
        SCAN_START_POS + a * (SCAN_END_POS - SCAN_START_POS)
        for a in alphas
    ], dtype=float)

    poses = _ensure_pose_array(positions)
    poses[:, 3] = SCAN_ROT_X
    poses[:, 4] = SCAN_ROT_Y
    poses[:, 5] = SCAN_ROT_Z

    return poses


def _build_explicit_poses() -> np.ndarray:
    """
    Erzeugt Posen aus einer expliziten Liste.

    Erlaubt:
    - (N,3): nur Positionen -> Rotation wird aus LASER_ROT_* ergänzt
    - (N,6): vollständige Posen
    """
    if len(EXPLICIT_POSITIONS) == 0:
        raise ValueError("EXPLICIT_POSITIONS ist leer.")

    positions = np.array(EXPLICIT_POSITIONS, dtype=float)

    if positions.ndim != 2 or positions.shape[1] not in [3, 6]:
        raise ValueError("EXPLICIT_POSITIONS muss (N,3) oder (N,6) sein.")

    poses = _ensure_pose_array(positions)

    if positions.shape[1] == 3:
        poses[:, 3] = LASER_ROT_X
        poses[:, 4] = LASER_ROT_Y
        poses[:, 5] = LASER_ROT_Z

    return poses


def _build_grid_poses() -> np.ndarray:
    """
    Erzeugt ein 2D-Raster mit konstanter Rotation.
    """
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

    positions = np.array(positions, dtype=float)
    poses = _ensure_pose_array(positions)

    poses[:, 3] = SCAN_ROT_X
    poses[:, 4] = SCAN_ROT_Y
    poses[:, 5] = SCAN_ROT_Z

    return poses


def _validate_increment_step(step: dict, index: int) -> None:
    """
    Prüft, ob ein Inkrement-Block alle benötigten Schlüssel enthält.
    """
    required_keys = ["dx", "dy", "dz", "drx", "dry", "drz", "repeat"]

    missing = [k for k in required_keys if k not in step]
    if missing:
        raise ValueError(
            f"LOCAL_INCREMENT_SEQUENCE[{index}] fehlt Schlüssel: {missing}"
        )

    if int(step["repeat"]) < 1:
        raise ValueError(
            f"LOCAL_INCREMENT_SEQUENCE[{index}]['repeat'] muss >= 1 sein."
        )


def _build_local_increment_poses() -> np.ndarray:
    """
    Erzeugt eine Posefolge aus lokalen Inkrementen.

    Startpose:
        [LASER_POS, LASER_ROT_X, LASER_ROT_Y, LASER_ROT_Z]

    Danach werden die Inkremente im lokalen Laser-KS angewendet.
    """
    start_pose = np.array([
        LASER_POS[0],
        LASER_POS[1],
        LASER_POS[2],
        LASER_ROT_X,
        LASER_ROT_Y,
        LASER_ROT_Z,
    ], dtype=float)

    T_current = pose_array_to_transform(start_pose)

    poses = []

    if INCLUDE_START_POSE_IN_LOCAL_SEQUENCE:
        poses.append(transform_to_pose_array(T_current))

    for i, step in enumerate(LOCAL_INCREMENT_SEQUENCE):
        _validate_increment_step(step, i)

        dx = float(step["dx"])
        dy = float(step["dy"])
        dz = float(step["dz"])
        drx = float(step["drx"])
        dry = float(step["dry"])
        drz = float(step["drz"])
        repeat = int(step["repeat"])

        for _ in range(repeat):
            T_current = apply_local_increment(
                T_current,
                dx=dx,
                dy=dy,
                dz=dz,
                drx_deg=drx,
                dry_deg=dry,
                drz_deg=drz,
            )
            poses.append(transform_to_pose_array(T_current))

    if len(poses) == 0:
        raise ValueError(
            "Die lokale Inkrement-Trajektorie ist leer. "
            "Prüfe LOCAL_INCREMENT_SEQUENCE und INCLUDE_START_POSE_IN_LOCAL_SEQUENCE."
        )

    return np.array(poses, dtype=float)


def generate_trajectory():
    """
    Gibt ein Array der Form (N, 6) zurück:
        [x, y, z, rx, ry, rz]

    Verhalten:
    - SCAN_MODE = "single"
    - SCAN_MODE = "trajectory"
    """
    # --------------------------------------------------
    # SINGLE
    # --------------------------------------------------
    if SCAN_MODE == "single":
        return _build_single_pose()

    if SCAN_MODE != "trajectory":
        raise ValueError(f"Unbekannter SCAN_MODE: {SCAN_MODE}")

    # --------------------------------------------------
    # TRAJECTORY MODES
    # --------------------------------------------------
    if TRAJECTORY_TYPE == "linspace":
        return _build_linspace_poses()

    if TRAJECTORY_TYPE == "explicit_list":
        return _build_explicit_poses()

    if TRAJECTORY_TYPE == "grid":
        return _build_grid_poses()

    if TRAJECTORY_TYPE == "local_increments":
        return _build_local_increment_poses()

    raise ValueError(f"Unbekannter TRAJECTORY_TYPE: {TRAJECTORY_TYPE}")