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
# 🔴 LASER (Grundparameter)
# ============================================================
LASER_POS   = np.array([0.01, 0.0, 0.0])
LASER_ROT_X = 0.0
LASER_ROT_Y = 0.0


# ============================================================
# 🔵 SIMULATIONSMODUS
# ============================================================
MODE = "DOE_Square"
# Optionen:
# "Point"
# "DOE_Square"
# "Line_Laser"
# "Multi_Line_Laser"   ← NEU


# ============================================================
# 🔳 DOE PARAMETER
# ============================================================
DOE_NX     = 4
DOE_NY     = 4
DOE_FOV_X  = 7.0   # Grad
DOE_FOV_Y  = 7.0   # Grad
DOE_CENTER = True


# ============================================================
# 📏 EINZELLINIEN-LASER
# ============================================================
LINE_FOV     = 12.0     # Grad (Öffnungswinkel)
LINE_SAMPLES = 1000     # Anzahl Strahlen entlang der Linie

# Orientierung der Linie (Default: X-Achse)
LINE_AXIS = np.array([1, 0, 0])


# ============================================================
# 📏📏 MULTILINIEN-LASER (NEU)
# ============================================================
MULTILINE_COUNT   = 7      # Anzahl Linien
MULTILINE_SPACING = 1.0    # Abstand in Grad zwischen Linien

# Orientierung identisch zur Einzellinie
# Linien werden orthogonal zur LINE_AXIS verteilt


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
SPHERE_CENTER = np.array([0.0, 0.0, 1.0])
SPHERE_RADIUS = 0.05


# Verhalten bei "Miss"
SPHERE_MISS_MODE = "fallback_plane"
# "discard"
# "fallback_plane"

FALLBACK_PLANE_Z = 1.5


# ============================================================
# 🎨 RENDERING
# ============================================================
SIGMA       = 3       # Gaußbreite
NOISE_LEVEL = 0.05    # Rauschlevel