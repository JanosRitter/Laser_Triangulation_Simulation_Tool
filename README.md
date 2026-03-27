# Laser Triangulation Simulation Tool

## Overview

This project provides a simulation environment for laser triangulation measurements.
It is designed to generate synthetic measurement data for testing and validating triangulation algorithms before real hardware measurements are available.

The simulation models:

* Laser emission (point, DOE, line, multi-line)
* Interaction with simple geometric objects (plane, sphere)
* Projection onto a virtual camera sensor
* Generation of synthetic measurement images and ground truth data

The output can be directly used as input for the corresponding evaluation and triangulation pipeline.

---

## Features

* Multiple laser models:

  * Point laser
  * DOE (Diffractive Optical Element) grid
  * Line laser
  * Multi-line laser
* Configurable scene geometry:

  * Planes (flat or rotated)
  * Spheres
* Physically motivated projection onto a camera sensor
* Synthetic image generation with:

  * Gaussian spot modeling
  * Noise
* Ground truth export for validation
* Fully reproducible simulations via metadata export

---

## Project Structure

```
laser_simulation/
├─ main.py
├─ src_laser_sim/
│  ├─ config.py
│  ├─ metadata.py
│  ├─ laser.py
│  ├─ plane.py
│  ├─ projection.py
│  ├─ io_utils.py
│  └─ utils.py
├─ data/
│  └─ output/
├─ README.md
└─ .gitignore
```

---

## How It Works

The simulation follows a forward model:

1. **Laser emission**

   * Rays are generated based on the selected laser model and configuration.

2. **Intersection with object**

   * Each ray is intersected with the target geometry (plane or sphere).

3. **Projection to camera**

   * Intersection points are projected onto the camera sensor.

4. **Image generation**

   * Gaussian spots are added to simulate laser intensity.
   * Noise is optionally added.

5. **Data export**

   * Image (`.png`)
   * Raw intensity array (`.npy`)
   * Ground truth (`.npy`)
   * Metadata (`.json`)

---

## Output Files

Each simulation generates:

### 1. Image (`.png`)

* Visual representation of the simulated measurement

### 2. Intensity array (`.npy`)

* Shape: `(height, width)`
* Values: pixel intensities

### 3. Metadata (`.json`)

* Contains all simulation parameters
* Enables full reproducibility

### 4. Ground truth (`.npy`)

Format:

```
[index_0, index_1, x, y, z, u, v]
```

* `(index_0, index_1)` → laser ray index
* `(x, y, z)` → intersection point in world coordinates
* `(u, v)` → projected pixel coordinates

---

## Laser Models

### DOE (Diffractive Optical Element)

* Grid of rays defined by:

  * `DOE_NX`, `DOE_NY`
  * `DOE_FOV_X`, `DOE_FOV_Y`
* Optional central ray (`DOE_CENTER`)
* Uses centered signed indexing:

```
(-2, -2) ... (0,0) ... (2,2)
```

---

### Line Laser

* Rays distributed along a line
* Gaussian intensity profile

---

### Multi-Line Laser

* Multiple parallel line lasers
* Controlled via:

  * `MULTILINE_COUNT`
  * `MULTILINE_SPACING`

---

## Configuration

All parameters are defined in:

```
src_laser_sim/config.py
```

Key categories:

* Camera parameters
* Laser parameters
* Scene geometry
* Rendering options

Example:

```python
MODE = "DOE_Square"

DOE_NX = 4
DOE_NY = 4
DOE_FOV_X = 7.0
DOE_FOV_Y = 7.0
DOE_CENTER = True
```

---

## Usage

Run the simulation:

```bash
python main.py
```

Outputs are stored in:

```
data/output/<timestamp>/
```

---

## Notes

* Camera distortion is currently not modeled.
* The simulation assumes idealized optics.
* Ground truth data is generated before noise is applied.

---

## Intended Use

This tool is intended for:

* Development of triangulation algorithms
* Validation against known ground truth
* Testing detection and fitting pipelines
* Prototyping before real measurements

---

## Future Improvements

* Camera distortion modeling
* More complex geometries
* Realistic noise models
* Calibration support
* Integration with evaluation pipeline

---

## Author

Developed as part of a laser triangulation project.
