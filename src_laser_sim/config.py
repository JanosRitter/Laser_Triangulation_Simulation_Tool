import numpy as np

# ============================================================
# 📷 KAMERA
# ============================================================
IMG_WIDTH   = 1280
IMG_HEIGHT  = 720

FOCAL_LENGTH = 0.02
PIXEL_SIZE   = 5e-6

SENSOR_WIDTH  = IMG_WIDTH  * PIXEL_SIZE
SENSOR_HEIGHT = IMG_HEIGHT * PIXEL_SIZE


# ============================================================
# 🔴 LASER (Grundparameter / Startpose)
# ============================================================
LASER_POS   = np.array([0.05, 0.0, 0.0], dtype=float)
LASER_ROT_X = 0.0
LASER_ROT_Y = -3.0
LASER_ROT_Z = 0.0


# ============================================================
# 🚗 SCAN / TRAJEKTORIE
# ============================================================
SCAN_MODE = "single"
# Optionen:
# "single"
# "trajectory"

TRAJECTORY_TYPE = "local_increments"
# Optionen:
# "linspace"
# "explicit_list"
# "grid"
# "local_increments"


# ============================================================
# 1D LINSPACE
# ============================================================
SCAN_N_FRAMES = 24
# nur relevant für TRAJECTORY_TYPE = "linspace"

SCAN_START_POS = np.array([-0.02, -0.08, 0.0], dtype=float)
SCAN_END_POS   = np.array([0.12,  0.08, 0.0], dtype=float)

SCAN_ROT_X = LASER_ROT_X
SCAN_ROT_Y = LASER_ROT_Y
SCAN_ROT_Z = LASER_ROT_Z


# ============================================================
# EXPLIZITE POSITIONS-/POSELISTE
# ============================================================
# Erlaubt:
# - (N, 3)  -> nur Positionen, Rotation wird aus LASER_ROT_* ergänzt
# - (N, 6)  -> vollständige Posen [x, y, z, rx, ry, rz]
EXPLICIT_POSITIONS = [
    np.array([0.05, 0.00, 0.0], dtype=float),
    np.array([0.05, 0.01, 0.0], dtype=float),
    np.array([0.05, 0.02, 0.0], dtype=float),
]


# ============================================================
# 2D-RASTER / FLÄCHENSCAN
# ============================================================
GRID_NX = 5
GRID_NY = 5

GRID_ORDER = "serpentine"
# Optionen:
# "row_major"   -> jede Zeile links nach rechts
# "serpentine"  -> Schlangenlinie


# ============================================================
# LOKALE INKREMENT-TRAJEKTORIE
# ============================================================
LOCAL_INCREMENT_SEQUENCE = [
    {
        "dx": 0.02, "dy": 0.0, "dz": 0.0,
        "drx": 0.0, "dry": 0.0, "drz": 0.0,
        "repeat": 5
    },
    {
        "dx": 0.0, "dy": -0.01, "dz": 0.0,
        "drx": 0.0, "dry": 0.0, "drz": 0.0,
        "repeat": 2
    },
    {
        "dx": 0.00, "dy": 0.0, "dz": 0.0,
        "drx": 0.0, "dry": -1, "drz": 0.0,
        "repeat": 5
    },
    {
        "dx": -0.02, "dy": -0.0, "dz": 0.0,
        "drx": 0.0, "dry": 0.0, "drz": 0.0,
        "repeat": 5
    },
    {
        "dx": 0.0, "dy": -0.01, "dz": 0.0,
        "drx": 0.0, "dry": 0.0, "drz": 0.0,
        "repeat": 2
    },
    {
        "dx": 0.0, "dy": 0.00, "dz": 0.0,
        "drx": 0.0, "dry": 1.0, "drz": 0.0,
        "repeat": 5
    }
]

# Soll die Startpose als erster Frame mit in die Trajektorie aufgenommen werden?
INCLUDE_START_POSE_IN_LOCAL_SEQUENCE = True


# ============================================================
# 💾 SPEICHERUNG / CROPPING
# ============================================================
FRAME_SAVE_MODE = "crop"
# Optionen:
# "full"  -> nur Vollbild speichern
# "crop"  -> nur Crop speichern
# "both"  -> Vollbild + Crop speichern

SAVE_PREVIEW_SUM = True

CROP_WIDTH  = 50
CROP_HEIGHT = 50

# Cropping zunächst für diese Modi aktivieren
CROP_ENABLED_MODES = ["Point"]


# ============================================================
# 🔵 SIMULATIONSMODUS
# ============================================================
MODE = "Multi_Line_Laser"
# Optionen:
# "Point"
# "DOE_Square"
# "Line_Laser"
# "Multi_Line_Laser"


# ============================================================
# 🔳 DOE PARAMETER
# ============================================================
DOE_NX     = 8
DOE_NY     = 8
DOE_FOV_X  = 7.0   # Grad
DOE_FOV_Y  = 7.0   # Grad
DOE_CENTER = True


# ============================================================
# 📏 EINZELLINIEN-LASER
# ============================================================
LINE_FOV     = 12.0
LINE_SAMPLES = 1000

LINE_AXIS = np.array([1, 0, 0], dtype=float)


# ============================================================
# 📏📏 MULTILINIEN-LASER
# ============================================================
MULTILINE_COUNT   = 7
MULTILINE_SPACING = 1.0


# ============================================================
# 🧱 SZENE / OBJEKT
# ============================================================
PLANE_MODE = "even_plane"
# Optionen:
# "even_plane"
# "sloped_plane"
# "sphere"

# ---------------------------
# Ebene
# ---------------------------
PLANE_Z     = 1.0
PLANE_ROT_X = 0.0
PLANE_ROT_Y = 45.0

# ---------------------------
# Kugel
# ---------------------------
SPHERE_CENTER = np.array([0.0, 0.0, 1.0], dtype=float)
SPHERE_RADIUS = 0.08

SPHERE_MISS_MODE = "discard"
# "discard"
# "fallback_plane"

FALLBACK_PLANE_Z = 1.5


# ============================================================
# 🎨 RENDERING
# ============================================================
SIGMA       = 3
NOISE_LEVEL = 0.05