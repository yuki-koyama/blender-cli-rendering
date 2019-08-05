FROM_DIR=./original
TO_DIR=./compressed

PNG_FILES=`find ${FROM_DIR} -maxdepth 1 -type f -name *.png`
echo ${PNG_FILES}
for in_file in ${PNG_FILES}
do
  echo ---------------------------------------
  echo input: ${in_file}         # ./original/01_cube.png
  temp=${in_file%.png}           # ./original/01_cube
  temp=${temp#${FROM_DIR}}       # /01_cube
  out_file=${TO_DIR}${temp}.jpg  # ./compressed/01_cube.jpg
  echo output: ${out_file}
  convert ${in_file} -resize 960x540 -background gray -flatten ${out_file}
done
