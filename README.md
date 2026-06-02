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
    export MAPILLARY_TOOLS_MAX_SEQUENCE_PIXELS=100000000000
    export MAPILLARY_TOOLS_MAX_SEQUENCE_COUNT=99999
    
    mapillary_tools process_and_upload ./dst \
      --cutoff_distance 999999 \
      --cutoff_time 999999 \
      --duplicate_distance 0
   ```


### Map Matching

If the extracted frames have GPS errors or are not perfectly aligned with the road, you can use Valhalla to snap them to the road network.

1. Start a local Valhalla instance using Docker:

   ```bash
   docker compose up -d
   ```

   (Note: The first run will download OSM data for Armenia and build routing tiles).

2. Run the map matching command:

   ```bash
   uv run python3 -m app match projects/kievyan/dst projects/kievyan/matched
   ```

   This will create a new set of images in `projects/kievyan/matched` with corrected GPS coordinates and added bearing information (direction of travel).


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


## Other processes

### GPS Synchronization

Phone GPS normally has a 2-3 second lag, so even if phone and camera timers are in perfect sync, you can still get a 30-50 meter offset while driving.  To fix this, you need to synchronize the video manually.  To do this, use `mpv` to find a part of the video where (a) the car is moving on its normal speed, not standing on a red light, and (b) it is in a location that can be accurately identified on the map, e.g. a crosswalk or a building corner.  Take the frame number, coordinates and pass them to this command:

```
uv run python3 -m app synchronize --frame 100500 --lat 40.0 --lon 50.0 src/video.mp4 src/track.gpx
```

To get the frame number, you might use `mpv`.  The 8K video will likely lag heavily, so you might need to transcode it to 720p:

```
ffmpeg -i src/video.mp4 -vf "scale=-1:720" -c:v libx264 -crf 30 -preset veryfast -an -b:a 128k src/video-720p.mp4
```

Then run `mpv` to play the video while showing the frame number and some guides for front, right and back margins:

```
mpv --hwdec=no --osd-msg1='Frame: ${estimated-frame-number} / ${estimated-frame-count}' --vf=lavfi='[drawgrid=w=iw/4:h=ih:x=iw*0.5:c=red:t=2]' src/video-720p.MP4
```
