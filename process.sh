#!/bin/sh

mkdir -p dst

mapillary_tools video_process src dst \
    --geotag_source gpx \
    --geotag_source_path src/recording.gpx
