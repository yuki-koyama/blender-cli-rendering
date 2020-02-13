#!/bin/bash

OUT_DIR="./out"

RESOLUTION=100
SAMPLINGS=128
ANIM_FRAMES_OPTION="--render-anim"

# Make this "true" when testing the scripts
TEST=false
if ${TEST}; then
  RESOLUTION=10
  SAMPLINGS=16
  ANIM_FRAMES_OPTION="--render-frame 1..5"
fi

# Create the output directory
mkdir -p ${OUT_DIR}

# Run the scripts
blender --background --python ./01_cube.py --render-frame 1 -- ${OUT_DIR}/01_cube_ ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./02_suzanne.py --render-frame 1 -- ${OUT_DIR}/02_suzanne_ ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./03_ibl.py --render-frame 1 -- ${OUT_DIR}/03_ibl_ ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./04_principled_bsdf.py --render-frame 1 -- ${OUT_DIR}/04_principled_bsdf_ ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./05_composition.py --render-frame 1 -- ${OUT_DIR}/05_composition_ ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./06_split_tone.py --render-frame 1 -- ${OUT_DIR}/06_split_tone_ ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./07_texturing.py --render-frame 1 -- ${OUT_DIR}/07_texturing_ ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./08_animation.py ${ANIM_FRAMES_OPTION} -- ${OUT_DIR}/08/frame_ ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./09_armature.py ${ANIM_FRAMES_OPTION} -- ${OUT_DIR}/09/frame_ ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./10_mocap.py ${ANIM_FRAMES_OPTION} -- ./assets/motion/102_01.bvh ${OUT_DIR}/10/frame_ ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./11_mesh_visualization.py --render-frame 1 -- ${OUT_DIR}/11_mesh_visualization_ ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./12_cloth.py ${ANIM_FRAMES_OPTION} -- ${OUT_DIR}/12/frame_ ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./13_matcap.py --render-frame 1 -- ${OUT_DIR}/13_matcap_ ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./14_procedural_texturing.py --render-frame 1 -- ${OUT_DIR}/14_procedural_texturing_ ${RESOLUTION} ${SAMPLINGS}

# Perform ffmpeg for animations
ffmpeg -y -r 24 -i ${OUT_DIR}/08/frame_%04d.png -pix_fmt yuv420p ${OUT_DIR}/08_animation.mp4
ffmpeg -y -r 24 -i ${OUT_DIR}/09/frame_%04d.png -pix_fmt yuv420p ${OUT_DIR}/09_armature.mp4
ffmpeg -y -r 24 -i ${OUT_DIR}/10/frame_%04d.png -pix_fmt yuv420p ${OUT_DIR}/10_mocap.mp4
ffmpeg -y -r 24 -i ${OUT_DIR}/12/frame_%04d.png -pix_fmt yuv420p ${OUT_DIR}/12_cloth.mp4
