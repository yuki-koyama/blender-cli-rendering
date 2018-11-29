# blender-cli-rendering

Python scripts for rendering images using Blender from command-line interface.

## Principles

- Able to run without display
- Designed for non-Blender users
- Based on Blender 2.79

## Possible Usages

- Visualization of 3D data with fancy rendering quality.
- Generation of synthetic training datasets for machine learning-based computer vision.

## Scripts

### 01_cube.py

- Cycles renderer

![01_cube](docs/compressed/01_cube.jpg)

### 02_suzanne.py

- Directional light
- Algorithmic object placement
- Subdivision surfaces
- `TRACK_TO` constraint to achieve camera's _look-at_ behavior
- Depth of field

![02_suzanne](docs/compressed/02_suzanne.jpg)

### 03_ibl.py

- Node-tree
- Image-based lighting using an HDR image

![03_ibl](docs/compressed/03_ibl.jpg)

### 04_principled_bsdf.py

- Principled BSDF
- Denoising
- Empty object as a target

![04_principled_bsdf](docs/compressed/04_principled_bsdf.jpg)

### 05_composition.py

- Composition
- Glare
- Lens distortion
- Chromatic aberration

![05_composition](docs/compressed/05_composition.jpg)

## License

Scripts in this repository use the Blender Python API, which is licensed under GNU General Public License (GPL). Thus, these scripts are considered as derivative works of a GPL-licensed work, so they are also licensed under GPL following the copyleft rule.
