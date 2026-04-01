import numpy as np


# ============================================================
# ROTATIONSMATRIZEN
# ============================================================
def rotation_matrix_x(rx_rad: float) -> np.ndarray:
    c = np.cos(rx_rad)
    s = np.sin(rx_rad)
    return np.array([
        [1.0, 0.0, 0.0],
        [0.0, c,   -s],
        [0.0, s,    c],
    ])


def rotation_matrix_y(ry_rad: float) -> np.ndarray:
    c = np.cos(ry_rad)
    s = np.sin(ry_rad)
    return np.array([
        [c,   0.0, s],
        [0.0, 1.0, 0.0],
        [-s,  0.0, c],
    ])


def rotation_matrix_z(rz_rad: float) -> np.ndarray:
    c = np.cos(rz_rad)
    s = np.sin(rz_rad)
    return np.array([
        [c,  -s,  0.0],
        [s,   c,  0.0],
        [0.0, 0.0, 1.0],
    ])


def euler_xyz_to_rotation_matrix(
    rx_deg: float,
    ry_deg: float,
    rz_deg: float
) -> np.ndarray:
    """
    Erzeugt eine Rotationsmatrix aus Euler-Winkeln in Grad.

    Konvention:
    - erst Rotation um X
    - dann um Y
    - dann um Z

    Gesamtrotation:
        R = Rz @ Ry @ Rx

    Diese Konvention sollte projektweit konsistent verwendet werden.
    """
    rx = np.deg2rad(rx_deg)
    ry = np.deg2rad(ry_deg)
    rz = np.deg2rad(rz_deg)

    Rx = rotation_matrix_x(rx)
    Ry = rotation_matrix_y(ry)
    Rz = rotation_matrix_z(rz)

    return Rz @ Ry @ Rx


# ============================================================
# POSE <-> HOMOGENE TRANSFORMATION
# ============================================================
def pose_to_transform(
    x: float,
    y: float,
    z: float,
    rx_deg: float,
    ry_deg: float,
    rz_deg: float
) -> np.ndarray:
    """
    Wandelt eine Pose (x,y,z,rx,ry,rz) in eine 4x4-Transformationsmatrix um.
    """
    T = np.eye(4, dtype=float)
    T[:3, :3] = euler_xyz_to_rotation_matrix(rx_deg, ry_deg, rz_deg)
    T[:3, 3] = np.array([x, y, z], dtype=float)
    return T


def transform_to_pose(T: np.ndarray) -> np.ndarray:
    """
    Wandelt eine 4x4-Transformationsmatrix zurück in
    [x, y, z, rx_deg, ry_deg, rz_deg].

    Hinweis:
    Die Rückrechnung von Eulerwinkeln ist konventionsabhängig und
    kann Singularitäten (Gimbal Lock) aufweisen.
    Für moderate Winkelbereiche ist diese Implementierung ausreichend.
    """
    if T.shape != (4, 4):
        raise ValueError("T muss die Form (4,4) haben.")

    x, y, z = T[:3, 3]
    R = T[:3, :3]

    # Für R = Rz @ Ry @ Rx
    sy = -R[2, 0]
    cy = np.sqrt(max(0.0, 1.0 - sy**2))

    singular = cy < 1e-10

    if not singular:
        rx = np.arctan2(R[2, 1], R[2, 2])
        ry = np.arcsin(sy)
        rz = np.arctan2(R[1, 0], R[0, 0])
    else:
        # Gimbal-Lock-Fall
        rx = np.arctan2(-R[1, 2], R[1, 1])
        ry = np.arcsin(sy)
        rz = 0.0

    return np.array([
        x,
        y,
        z,
        np.rad2deg(rx),
        np.rad2deg(ry),
        np.rad2deg(rz),
    ], dtype=float)


# ============================================================
# TRANSFORMATIONSALGEBRA
# ============================================================
def invert_transform(T: np.ndarray) -> np.ndarray:
    """
    Invertiert eine starre 4x4-Transformation.
    """
    if T.shape != (4, 4):
        raise ValueError("T muss die Form (4,4) haben.")

    R = T[:3, :3]
    t = T[:3, 3]

    T_inv = np.eye(4, dtype=float)
    T_inv[:3, :3] = R.T
    T_inv[:3, 3] = -R.T @ t
    return T_inv


def compose_transforms(T_a: np.ndarray, T_b: np.ndarray) -> np.ndarray:
    """
    Verknüpft zwei 4x4-Transformationen:
        T_result = T_a @ T_b
    """
    if T_a.shape != (4, 4) or T_b.shape != (4, 4):
        raise ValueError("Beide Matrizen müssen die Form (4,4) haben.")
    return T_a @ T_b


# ============================================================
# PUNKTE / VEKTORRICHTUNGEN TRANSFORMIEREN
# ============================================================
def transform_point(T: np.ndarray, point: np.ndarray) -> np.ndarray:
    """
    Transformiert einen 3D-Punkt mit einer 4x4-Transformation.
    """
    point = np.asarray(point, dtype=float)
    if point.shape != (3,):
        raise ValueError("point muss die Form (3,) haben.")

    point_h = np.array([point[0], point[1], point[2], 1.0], dtype=float)
    transformed = T @ point_h
    return transformed[:3]


def transform_direction(T: np.ndarray, direction: np.ndarray) -> np.ndarray:
    """
    Transformiert einen Richtungsvektor mit dem Rotationsanteil
    einer 4x4-Transformation.

    Translation wird ignoriert.
    """
    direction = np.asarray(direction, dtype=float)
    if direction.shape != (3,):
        raise ValueError("direction muss die Form (3,) haben.")

    R = T[:3, :3]
    transformed = R @ direction
    norm = np.linalg.norm(transformed)

    if norm < 1e-12:
        raise ValueError("Transformierter Richtungsvektor hat Norm 0.")

    return transformed / norm


# ============================================================
# LOKALE INKREMENTBEWEGUNGEN
# ============================================================
def local_increment_to_transform(
    dx: float,
    dy: float,
    dz: float,
    drx_deg: float,
    dry_deg: float,
    drz_deg: float
) -> np.ndarray:
    """
    Erzeugt eine lokale Inkrement-Transformation.

    Diese Transformation ist im lokalen Koordinatensystem des
    bewegten Körpers definiert.
    """
    return pose_to_transform(dx, dy, dz, drx_deg, dry_deg, drz_deg)


def apply_local_increment(
    T_current: np.ndarray,
    dx: float,
    dy: float,
    dz: float,
    drx_deg: float,
    dry_deg: float,
    drz_deg: float
) -> np.ndarray:
    """
    Wendet eine lokale Inkrementbewegung auf eine aktuelle Pose an.

    Lokale Bewegung bedeutet:
        T_next = T_current @ T_increment
    """
    T_increment = local_increment_to_transform(
        dx, dy, dz, drx_deg, dry_deg, drz_deg
    )
    return T_current @ T_increment


def apply_global_increment(
    T_current: np.ndarray,
    dx: float,
    dy: float,
    dz: float,
    drx_deg: float,
    dry_deg: float,
    drz_deg: float
) -> np.ndarray:
    """
    Wendet eine globale Inkrementbewegung auf eine aktuelle Pose an.

    Globale Bewegung bedeutet:
        T_next = T_increment @ T_current
    """
    T_increment = local_increment_to_transform(
        dx, dy, dz, drx_deg, dry_deg, drz_deg
    )
    return T_increment @ T_current


# ============================================================
# HILFSFUNKTIONEN FÜR POSE-DARSTELLUNG
# ============================================================
def pose_array_to_transform(pose: np.ndarray) -> np.ndarray:
    """
    Erwartet pose = [x, y, z, rx_deg, ry_deg, rz_deg]
    """
    pose = np.asarray(pose, dtype=float)
    if pose.shape != (6,):
        raise ValueError("pose muss die Form (6,) haben.")

    return pose_to_transform(
        pose[0], pose[1], pose[2],
        pose[3], pose[4], pose[5]
    )


def transform_to_pose_array(T: np.ndarray) -> np.ndarray:
    """
    Alias für transform_to_pose, für konsistente Namensgebung.
    """
    return transform_to_pose(T)