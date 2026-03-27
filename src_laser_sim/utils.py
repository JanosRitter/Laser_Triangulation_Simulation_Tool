import numpy as np
from .config import (
    SENSOR_WIDTH, SENSOR_HEIGHT, FOCAL_LENGTH,
    DOE_FOV_X, DOE_FOV_Y,
    LASER_POS
)
from .config import (
    LINE_FOV, LINE_SAMPLES,
    MULTILINE_COUNT, MULTILINE_SPACING,
    MODE
)
from .plane import intersect_plane
from .projection import project


# ---------------------------
# KAMERA FOV
# ---------------------------
def compute_camera_fov():
    fov_x = 2 * np.arctan(SENSOR_WIDTH / (2 * FOCAL_LENGTH))
    fov_y = 2 * np.arctan(SENSOR_HEIGHT / (2 * FOCAL_LENGTH))
    return np.rad2deg(fov_x), np.rad2deg(fov_y)


# ---------------------------
# KAMERA FENSTER @ DISTANZ
# ---------------------------
def compute_window_size_at_distance(distance=1.0):
    width = SENSOR_WIDTH * distance / FOCAL_LENGTH
    height = SENSOR_HEIGHT * distance / FOCAL_LENGTH
    return width, height


# ---------------------------
# DOE GRÖSSE @ DISTANZ
# ---------------------------
def compute_doe_size(distance=1.0):
    fov_x = np.deg2rad(DOE_FOV_X)
    fov_y = np.deg2rad(DOE_FOV_Y)

    width = 2 * distance * np.tan(fov_x / 2)
    height = 2 * distance * np.tan(fov_y / 2)

    return width, height


# ---------------------------
# ZENTRALER LASERPUNKT (3D)
# ---------------------------
def compute_center_intersection(base_dir):
    return intersect_plane(LASER_POS, base_dir)


# ---------------------------
# ZENTRALER LASERPUNKT (PIXEL)
# ---------------------------
def compute_center_pixel(base_dir):
    p = compute_center_intersection(base_dir)

    if p is None:
        return None, None

    return project(p)




def print_simulation_summary(base_dir, visible_points, missing_points, folder):
    # ---------------------------
    # Basiswerte berechnen
    # ---------------------------
    cam_fov_x, cam_fov_y = compute_camera_fov()
    win_w, win_h = compute_window_size_at_distance(1.0)
    doe_w, doe_h = compute_doe_size(1.0)

    center_point = compute_center_intersection(base_dir)
    center_px, center_py = compute_center_pixel(base_dir)

    # ---------------------------
    # Kamera
    # ---------------------------
    print("\n📷 Kamera:")
    print(f"  FOV: {cam_fov_x:.2f}° x {cam_fov_y:.2f}°")
    print(f"  Sichtfenster @1m: {win_w*100:.2f} cm x {win_h*100:.2f} cm")

    # ---------------------------
    # DOE
    # ---------------------------
    print("\n🔴 DOE:")
    print(f"  Winkel: {DOE_FOV_X}° x {DOE_FOV_Y}°")
    print(f"  Fläche @1m: {doe_w*100:.2f} cm x {doe_h*100:.2f} cm")

    print("\n⚖️ Verhältnis DOE zu Kamera:")
    print(f"  Breite: {doe_w / win_w * 100:.1f}%")
    print(f"  Höhe:   {doe_h / win_h * 100:.1f}%")

    # ---------------------------
    # Laser Zentrum
    # ---------------------------
    print("\n🎯 Laser Zentrum:")
    if center_point is not None:
        print(f"  3D Punkt: {center_point}")
        print(f"  Pixel: ({center_px:.1f}, {center_py:.1f})")
    else:
        print("  Kein Schnitt mit aktueller Geometrie!")

    # ---------------------------
    # Linienlaser
    # ---------------------------
    if MODE == "Line_Laser":
        print("\n📏 Linienlaser:")
        print(f"  Öffnungswinkel: {LINE_FOV}°")
        print(f"  Strahlen: {LINE_SAMPLES}")

    if MODE == "Multi_Line_Laser":
        print("\n📏📏 Multilinienlaser:")
        print(f"  Linien: {MULTILINE_COUNT}")
        print(f"  Abstand: {MULTILINE_SPACING}°")
        print(f"  Strahlen pro Linie: {LINE_SAMPLES}")
        print(f"  Gesamtstrahlen: {MULTILINE_COUNT * LINE_SAMPLES}")

    # ---------------------------
    # Ergebnis
    # ---------------------------
    print("\n📊 Ergebnis:")
    print(f"  ✅ Sichtbar: {len(visible_points)}")
    print(f"  ❌ Verworfen: {missing_points}")
    print(f"  💾 Gespeichert in: {folder}")