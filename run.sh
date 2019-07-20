#!/bin/bash

RESOLUTION=100
SAMPLINGS=128

mkdir -p out
blender --background --python ./01_cube.py -- ./out/01_cube.png ${RESOLUTION}
blender --background --python ./02_suzanne.py -- ./out/02_suzanne.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./03_ibl.py -- ./out/03_ibl.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./04_principled_bsdf.py -- ./out/04_principled_bsdf.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./05_composition.py -- ./out/05_composition.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./06_vignette.py -- ./out/06_vignette.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./07_texturing.py -- ./out/07_texturing.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./08_animation.py -- ./out/08/frame ${RESOLUTION} ${SAMPLINGS} && ffmpeg -r 24 -i ./out/08/frame%04d.png -pix_fmt yuv420p ./out/08_animation.mp4
blender --background --python ./09_armature.py -- ./out/09/frame ${RESOLUTION} ${SAMPLINGS} && ffmpeg -r 24 -i ./out/09/frame%04d.png -pix_fmt yuv420p ./out/09_armature.mp4
blender --background --python ./10_mocap.py -- ./assets/motion/102_01.bvh ./out/10/frame ${RESOLUTION} ${SAMPLINGS} && ffmpeg -r 24 -i ./out/10/frame%04d.png -pix_fmt yuv420p ./out/10_mocap.mp4
blender --background --python ./11_mesh_visualization.py -- ./out/11_mesh_visualization.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./12_split_tone.py -- ./out/12_split_tone.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./13_matcap.py -- ./out/13_matcap.png ${RESOLUTION} ${SAMPLINGS}
