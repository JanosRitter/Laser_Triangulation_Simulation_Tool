# Laser Triangulation Simulation Tool

## Overview

This project provides a simulation environment for laser triangulation measurements.  
It is designed to generate synthetic measurement data for testing and validating triangulation algorithms before real hardware measurements are available.

The simulation models:

- Laser emission (point, DOE, line, multi-line)
- Interaction with simple geometric objects (plane, sphere)
- Projection onto a virtual camera sensor
- Generation of synthetic measurement images and ground truth data

The output can be directly used as input for the corresponding evaluation and triangulation pipeline.

---

## Features

### Core Simulation

- Multiple laser models:
  - Point laser
  - DOE (Diffractive Optical Element) grid
  - Line laser
  - Multi-line laser

- Configurable scene geometry:
  - Planes (flat or rotated)
  - Spheres

- Physically motivated projection onto a camera sensor

- Synthetic image generation with:
  - Gaussian spot modeling
  - Configurable noise

---

### Trajectory & Scanning

- Simulation of moving laser / robot-based scanning
- Multiple trajectory types:
  - Single pose
  - 1D linspace trajectory
  - Explicit position list
  - 2D grid scanning (area scans)

- Supports:
  - Line scans
  - Surface scans
  - Dense measurement patterns

---

### Data Management

- Structured output for full scan runs
- One folder per simulation run
- Centralized metadata instead of per-frame duplication
- Frame-wise tracking via CSV table

---

### Cropping & Efficient Storage

- Optional cropping around laser spot:
  - Reduces data size drastically
  - Keeps exact pixel correspondence

- Stores:
  - Global pixel position
  - Crop origin
  - Local pixel coordinates inside crop

---

### Preview & Debug Visualization

- Aggregated preview image of full scan
- Built from noise-free signal
- Useful for:
  - Scan coverage validation
  - Debugging trajectories
  - Visual sanity checks

---

### Ground Truth & Reproducibility

- Exact ground truth for every visible ray
- Full simulation metadata export
- Fully reproducible runs

---

## Project Structure


laser_simulation/
├─ main.py
├─ src_laser_sim/
│ ├─ config.py
│ ├─ simulation.py
│ ├─ trajectory.py
│ ├─ frame_processing.py
│ ├─ preview.py
│ ├─ run_pipeline.py
│ ├─ metadata.py
│ ├─ laser.py
│ ├─ plane.py
│ ├─ projection.py
│ ├─ io_utils.py
│ └─ utils.py
├─ Simulation_outputs/
├─ README.md
└─ .gitignore


---

## How It Works

The simulation follows a forward model:

### 1. Laser emission

- Rays are generated based on the selected laser model.

### 2. Intersection with object

- Rays intersect with scene geometry (plane or sphere).

### 3. Projection to camera

- Intersection points are projected onto the camera sensor.

### 4. Image generation

- Gaussian spots simulate laser intensity
- A noise-free signal image is created
- Noise is added to produce the final measurement image

### 5. Data processing

- Frame results are processed:
  - Visibility classification
  - Optional cropping
  - File generation

### 6. Data export

Depending on configuration:

- Full images
- Cropped images
- Ground truth
- Frame table
- Run metadata
- Preview image

---

## Output Structure

Each trajectory run creates:


Simulation_outputs/
<MODE>/
<PLANE_MODE>/
<timestamp>/
run_metadata.json
frame_table.csv
preview_sum.npy
preview_sum.png
frames/
frame_000000.npy
frame_000000.png
frame_000000_ground_truth.npy
crops/
crop_000000.npy
crop_000000.png


---

## Frame Table (frame_table.csv)

Each row corresponds to one simulated frame:

| Column | Description |
|--------|-------------|
| frame_idx | Frame index |
| laser_x/y/z | Laser position |
| num_visible | Number of visible rays |
| num_missing | Missing rays |
| status | valid / invalid |
| full_px/py | Pixel location in full image |
| crop_* | Crop metadata |
| image_* | Stored image files |
| ground_truth_file | Ground truth file |

---

## Ground Truth Format


[index_0, index_1, x, y, z, u, v]


- (index_0, index_1) → ray index  
- (x, y, z) → 3D intersection  
- (u, v) → pixel position  

---

## Trajectory Configuration

Defined in:


src_laser_sim/config.py


### Example: Line Scan

```python
TRAJECTORY_TYPE = "linspace"

SCAN_START_POS = np.array([0.05, -0.1, 0.0])
SCAN_END_POS   = np.array([0.05,  0.1, 0.0])
SCAN_N_FRAMES  = 50
Example: Grid Scan (Area Scan)
TRAJECTORY_TYPE = "grid"

SCAN_START_POS = np.array([0.05, 0.05, 0.0])
SCAN_END_POS   = np.array([0.10, 0.10, 0.0])

GRID_NX = 10
GRID_NY = 10
GRID_ORDER = "serpentine"
Cropping Configuration
FRAME_SAVE_MODE = "both"   # "full", "crop", "both"

CROP_WIDTH  = 50
CROP_HEIGHT = 50

CROP_ENABLED_MODES = ["Point"]
Preview Configuration
SAVE_PREVIEW_SUM = True
Preview is generated from noise-free signal images
Intended for visualization only (not evaluation)
Usage

Run the simulation:

python main.py

Outputs are stored in:

Simulation_outputs/
Architecture

The system is modularized into layers:

Simulation Layer
simulation.py
laser.py
plane.py
projection.py

→ Generates physical measurement data

Trajectory Layer
trajectory.py

→ Defines scan paths

Processing Layer
frame_processing.py

→ Converts raw simulation output into structured frame data

Preview Layer
preview.py

→ Handles scan visualization

Pipeline Layer
run_pipeline.py

→ Controls execution flow (single vs trajectory)

I/O Layer
io_utils.py
metadata.py

→ Handles storage and reproducibility

Notes
Camera distortion is not modeled
Idealized optics assumed
Ground truth is generated before noise
Preview images are noise-free aggregations
Intended Use
Development of triangulation algorithms
Validation with exact ground truth
Testing detection pipelines
Simulation of robotic scanning strategies
Data generation for ML or optimization
Future Improvements
Camera distortion models
More complex geometries
Advanced noise models
Real sensor simulation
Calibration workflows
Multi-camera setups
Author

Developed as part of a laser triangulation research project.
