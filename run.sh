#!/bin/bash

RESOLUTION=100
SAMPLINGS=128
OUT_DIR="./out"

mkdir -p ${OUT_DIR}
blender --background --python ./01_cube.py -- ${OUT_DIR}/01_cube.png ${RESOLUTION}
blender --background --python ./02_suzanne.py -- ${OUT_DIR}/02_suzanne.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./03_ibl.py -- ${OUT_DIR}/03_ibl.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./04_principled_bsdf.py -- ${OUT_DIR}/04_principled_bsdf.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./05_composition.py -- ${OUT_DIR}/05_composition.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./06_vignette.py -- ${OUT_DIR}/06_vignette.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./07_texturing.py -- ${OUT_DIR}/07_texturing.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./08_animation.py -- ${OUT_DIR}/08/frame ${RESOLUTION} ${SAMPLINGS} && ffmpeg -r 24 -i ${OUT_DIR}/08/frame%04d.png -pix_fmt yuv420p ${OUT_DIR}/08_animation.mp4
blender --background --python ./09_armature.py -- ${OUT_DIR}/09/frame ${RESOLUTION} ${SAMPLINGS} && ffmpeg -r 24 -i ${OUT_DIR}/09/frame%04d.png -pix_fmt yuv420p ${OUT_DIR}/09_armature.mp4
blender --background --python ./10_mocap.py -- ./assets/motion/102_01.bvh ${OUT_DIR}/10/frame ${RESOLUTION} ${SAMPLINGS} && ffmpeg -r 24 -i ${OUT_DIR}/10/frame%04d.png -pix_fmt yuv420p ${OUT_DIR}/10_mocap.mp4
blender --background --python ./11_mesh_visualization.py -- ${OUT_DIR}/11_mesh_visualization.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./12_split_tone.py -- ${OUT_DIR}/12_split_tone.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./13_matcap.py -- ${OUT_DIR}/13_matcap.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./14_cloth.py -- ${OUT_DIR}/14/frame ${RESOLUTION} ${SAMPLINGS} && ffmpeg -r 24 -i ${OUT_DIR}/14/frame%04d.png -pix_fmt yuv420p ${OUT_DIR}/14_cloth.mp4
