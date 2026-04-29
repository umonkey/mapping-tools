#!/bin/sh
# This script works with the geo-tagged files extracted using the app, like this:
# uv run python3 -m app src/stretched.mp4 src/track.gpx dst --distance 10.0

export MAPILLARY_TOOLS_MAX_SEQUENCE_PIXELS=100000000000
export MAPILLARY_TOOLS_MAX_SEQUENCE_LENGTH=10000

if [ ! -d dst ]; then
    echo "This script uploads JPEG files from ./dst to Mapillary."
    echo "Please run the app first to generate the files."
    exit 1
fi

mapillary_tools process_and_upload ./dst \
  --organization_key "3351990278289209" \
  --cutoff_distance 999999 \
  --cutoff_time 999999 \
  --duplicate_distance 0
