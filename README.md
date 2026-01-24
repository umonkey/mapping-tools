# Geo-tagging video frames

## 1. Extracting the frames

Using ffmpeg we can extract the frames at even intervals.  For example, 2 per second.  We probably need to calculate the average speed to understand the required fps later.

The frames probably also might need resizing, 4k might be too big.

```
ffmpeg -i recording.mp4 -vf "fps=1,scale=1920:-1" "frames/frame_%06d.jpg"
```
