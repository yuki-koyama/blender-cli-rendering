FROM_DIR=./original
TO_DIR=./compressed

WIDTH=960
TARGET_FPS=12

echo commands:
echo - `which convert`
echo - `which ffmpeg`

png_files=`find ${FROM_DIR} -maxdepth 1 -type f -name *.png`

for in_file in ${png_files}
do
  echo ---------------------------------------
  echo input: ${in_file}         # ./original/01_cube.png
  temp=${in_file%.png}           # ./original/01_cube
  temp=${temp#${FROM_DIR}}       # /01_cube
  out_file=${TO_DIR}${temp}.jpg  # ./compressed/01_cube.jpg
  echo output: ${out_file}
  convert ${in_file} -resize ${WIDTH}x -background gray -flatten ${out_file}
done

mp4_files=`find ${FROM_DIR} -maxdepth 1 -type f -name *.mp4`

for in_file in ${mp4_files}
do
  echo ---------------------------------------
  echo input: ${in_file}         # ./original/10_mocap.mp4
  temp=${in_file%.mp4}           # ./original/10_mocap
  temp=${temp#${FROM_DIR}}       # /10_mocap
  out_file=${TO_DIR}${temp}.gif  # ./compressed/10_mocap.gif
  echo output: ${out_file}

  temp_pallete=./temp.png
  filters="fps=${TARGET_FPS},scale=${WIDTH}:-1:flags=lanczos"
  ffmpeg -ss 0.2 -t 1.8 -i ${in_file} -vf "${filters},palettegen" ${temp_pallete} -y
  ffmpeg -ss 0.2 -t 1.8 -i ${in_file} -i ${temp_pallete} -lavfi "${filters} [x]; [x][1:v] paletteuse" -loop 100 ${out_file} -y
  rm ${temp_pallete}
done
