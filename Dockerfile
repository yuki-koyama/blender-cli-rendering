FROM ubuntu:18.04

WORKDIR /home

RUN apt-get update && apt-get install -y \
  blender \
  ffmpeg

COPY . .

RUN chmod +x ./run.sh
RUN mkdir -p ./out

ENTRYPOINT ["./run.sh"]
