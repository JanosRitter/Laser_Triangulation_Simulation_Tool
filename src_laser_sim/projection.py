import numpy as np
from .config import (
    IMG_WIDTH, IMG_HEIGHT,
    FOCAL_LENGTH, PIXEL_SIZE,
    SENSOR_WIDTH, SENSOR_HEIGHT,
    SIGMA, NOISE_LEVEL
)

# ---------------------------
# SICHTFELD
# ---------------------------
def is_visible(point):
    x, y, z = point

    if z <= 0:
        return False

    max_x = (SENSOR_WIDTH / 2) / FOCAL_LENGTH
    max_y = (SENSOR_HEIGHT / 2) / FOCAL_LENGTH

    return abs(x / z) <= max_x and abs(y / z) <= max_y


# ---------------------------
# PROJEKTION
# ---------------------------
def project(point):
    x, y, z = point

    u = FOCAL_LENGTH * (x / z)
    v = FOCAL_LENGTH * (y / z)

    px = IMG_WIDTH / 2 + u / PIXEL_SIZE
    py = IMG_HEIGHT / 2 - v / PIXEL_SIZE

    return px, py


# ---------------------------
# GAUSS SPOT
# ---------------------------
def add_gaussian_spot(image, px, py, intensity=1.0):
    radius = int(3 * SIGMA)

    x_min = max(0, int(px - radius))
    x_max = min(IMG_WIDTH, int(px + radius))
    y_min = max(0, int(py - radius))
    y_max = min(IMG_HEIGHT, int(py + radius))

    x = np.arange(x_min, x_max)
    y = np.arange(y_min, y_max)
    xx, yy = np.meshgrid(x, y)

    gaussian = np.exp(-((xx - px)**2 + (yy - py)**2) / (2 * SIGMA**2))
    gaussian *= 255 * intensity

    image[y_min:y_max, x_min:x_max] += gaussian


# ---------------------------
# NORMALISIERUNG (NEU)
# ---------------------------
def normalize_image(image):
    max_val = np.max(image)
    

    if max_val > 0:
        image = image / max_val * 255

    return image


# ---------------------------
# RAUSCHEN
# ---------------------------
def add_noise(image):
    noise = np.random.normal(0, NOISE_LEVEL * 255, image.shape)
    image = image + noise

    return np.clip(image, 0, 255)


