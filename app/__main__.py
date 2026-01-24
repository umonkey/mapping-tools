import sys
from . import Reader, Writer, Locator

def main(video_path, gpx_path, output_folder):
    locator = Locator(gpx_path)
    reader = Reader(video_path)
    writer = Writer(distance=1.0, folder=output_folder)

    for index, frame, frame_time in reader.read():
        lat, lon = locator.locate(frame_time)
        writer.write_frame(index, frame, frame_time, lat, lon)

if __name__ == "__main__":
    main(*sys.argv[1:])
