# Mapping tools

This repository contains some work-in-progress code that helps mapping trees.  This code is being developed for the [tree mapping](https://github.com/umonkey/treemap/) application and will eventually be moved there.


## Existing code

### Video Geotagging

The application in `app` is designed to extract frames from video files and a corresponding GPX track, extract and geo-tag frames at certain distance.

Requirements:

- The video file has accurate creation_time set.
- The GPS track has data for the whole video.

To extract the frames, run the app as following:

``` sh
mkdir -p dst
uv run python3 -m app src/stretched.mp4 src/track.gpx dst --distance 3.0
```

This will create a bunch of files in the `dst` folder, named like `dst/frame_000674.jpg`.  The output files contain GPS coordinates and thumbnails.  The remaining workflow is normally the following:

1. Use [Photini](https://photini.readthedocs.io/en/latest/) to review how the images are aligned on the map, delete images that aren't needed (e.g. waiting for the green light), and move the images on the map to compensate for GPS errors.
2. Upload the imagery to Mapillary using a command like this:

   ``` bash

   ```


### Creating the dot cloud

The idea is to feed geo-tagged images from the previous step to the OpenDroneMap application to create a dot cloud for extracting trees.  This is not yet working, as with all recent experiments ODM failed to produce anything after hours of processing the data.

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
  --split 200 \
  --split-overlap 50 \
  --feature-quality high \
  --mesh-size 200000 \
  --project-path /project .
```

On a laptop with the Ryzen 5 5500U CPU and 32 GB of RAM, processing a set of 694 4K images took more than 20 hours.
