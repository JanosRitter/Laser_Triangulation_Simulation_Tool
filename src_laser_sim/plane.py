import numpy as np
from .config import (
    PLANE_MODE, PLANE_Z,
    PLANE_ROT_X, PLANE_ROT_Y,
    SPHERE_CENTER, SPHERE_RADIUS,
    SPHERE_MISS_MODE, FALLBACK_PLANE_Z
)

def intersect_sphere(pos, direction):
    oc = pos - SPHERE_CENTER

    a = np.dot(direction, direction)
    b = 2.0 * np.dot(direction, oc)
    c = np.dot(oc, oc) - SPHERE_RADIUS**2

    discriminant = b**2 - 4*a*c

    if discriminant < 0:
        return None  # kein Schnitt

    sqrt_d = np.sqrt(discriminant)

    t1 = (-b - sqrt_d) / (2*a)
    t2 = (-b + sqrt_d) / (2*a)

    # wir wollen den nächsten positiven Schnittpunkt
    t = None
    if t1 > 0 and t2 > 0:
        t = min(t1, t2)
    elif t1 > 0:
        t = t1
    elif t2 > 0:
        t = t2
    else:
        return None  # beide hinter dem Laser

    return pos + t * direction

def intersect_fallback_plane(pos, direction):
    t = (FALLBACK_PLANE_Z - pos[2]) / direction[2]
    return pos + t * direction

def intersect_plane(pos, direction):

    if PLANE_MODE == "even_plane":
        t = (PLANE_Z - pos[2]) / direction[2]
        return pos + t * direction

    elif PLANE_MODE == "sloped_plane":
        # Rotation in Radiant
        rx = np.deg2rad(PLANE_ROT_X)
        ry = np.deg2rad(PLANE_ROT_Y)
    
        # Start-Normalenvektor (z-Achse)
        normal = np.array([0, 0, 1])
    
        # Rotationsmatrix um X
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(rx), -np.sin(rx)],
            [0, np.sin(rx),  np.cos(rx)]
        ])
    
        # Rotationsmatrix um Y
        Ry = np.array([
            [ np.cos(ry), 0, np.sin(ry)],
            [0,           1, 0],
            [-np.sin(ry), 0, np.cos(ry)]
        ])
    
        # Normale rotieren
        normal = Ry @ Rx @ normal
    
        # Punkt auf der Ebene (wie bei even_plane)
        plane_point = np.array([0, 0, PLANE_Z])
    
        # Ebenengleichung: n · x = d
        d = np.dot(normal, plane_point)
    
        denom = np.dot(normal, direction)
    
        # Strahl parallel zur Ebene → kein Schnitt
        if abs(denom) < 1e-8:
            return None
    
        t = (d - np.dot(normal, pos)) / denom
    
        # Schnittpunkt hinter dem Laser → ignorieren
        if t < 0:
            return None
    
        return pos + t * direction

    elif PLANE_MODE == "sphere":
        p = intersect_sphere(pos, direction)

        if p is not None:
            return p

        # kein Schnitt → Verhalten abhängig vom Modus
        if SPHERE_MISS_MODE == "discard":
            return None

        elif SPHERE_MISS_MODE == "fallback_plane":
            return intersect_fallback_plane(pos, direction)

        else:
            raise ValueError("Unbekannter SPHERE_MISS_MODE")

    else:
        raise ValueError(f"Unbekannter Ebenenmodus: {PLANE_MODE}")