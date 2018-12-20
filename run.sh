#!/bin/bash

RESOLUTION=100
SAMPLINGS=1000

mkdir -p out
blender --background --python ./01_cube.py -- ./out/01_cube.png ${RESOLUTION}
blender --background --python ./02_suzanne.py -- ./out/02_suzanne.png ${RESOLUTION}
blender --background --python ./03_ibl.py -- ./out/03_ibl.png ${RESOLUTION}
blender --background --python ./04_principled_bsdf.py -- ./out/04_principled_bsdf.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./05_composition.py -- ./out/05_composition.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./06_vignette.py -- ./out/06_vignette.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./07_texturing.py -- ./out/07_texturing.png ${RESOLUTION} ${SAMPLINGS}
blender --background --python ./08_animation.py -- ./out/temp/frame ${RESOLUTION} ${SAMPLINGS} && ffmpeg -r 24 -i ./out/temp/frame%04d.png -pix_fmt yuv420p ./out/08_animation.mp4
