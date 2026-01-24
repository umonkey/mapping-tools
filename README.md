# Geo-tagging video frames

This repository contains code to extract geo-tagged frames from a video file and a GPX track, then create a 3D dot cloud from that.


## Extracting the frames

Use the provided app:

``` sh
mkdir -p dst
python3 -m app src/recording.mp4 src/recording.gpx dst
```

This will create a bunch of files in the `dst` folder, named like `dst/frame_000674.jpg`.


## Create the dot cloud

After the previous step finishes, you get a bunch of JPEG files in the `dst` folder:

```
dst/frame_000001.jpg
dst/frame_000002.jpg
dst/frame_000003.jpg
dst/frame_000004.jpg
```

Copy them to folder `my_project/images` and run ODM to create a dot cloud from them:

```bash
mkdir -p my_project/images odm_orthophoto odm_texturing
cp dst/frame*.jpg my_project/images/

docker run -ti --rm \
  -v "$(pwd)/my_project:/project:z" \
  docker.io/opendronemap/odm \
  --skip-orthophoto --skip-report \
  --project-path /project .
```
