# Geo-tagging video frames

This repository contains code to extract geo-tagged frames from a video file and a GPX track, then create a 3D dot cloud from that.


## Extracting the frames

Use the provided app:

``` sh
mkdir -p dst
python3 -m app src/recording.mp4 src/recording.gpx dst
```

This will create a bunch of files in the `dst` folder, named like `dst/frame_000674.jpg`.
