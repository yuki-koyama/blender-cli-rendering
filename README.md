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

### 02_suzanne.py

- Directional light
- Algorithmic object placement
- Subdivision surfaces
- `TRACK_TO` constraint to achieve camera's _look-at_ behavior
- Depth of field

### 03_ibl.py

- Image-based lighting using an HDR image

### 04_principled_bsdf.py

- Principled BSDF
- Denoising
- Empty object as a target

## License

Scripts in this repository use the Blender Python API, which is licensed under GNU General Public License (GPL). Thus, these scripts are considered as derivative works of a GPL-licensed work, so they are also licensed under GPL following the copyleft rule.
