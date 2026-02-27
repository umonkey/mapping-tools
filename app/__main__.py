import argparse

from . import Locator, Reader, Writer
from .locator import NoCoordinates


def main():
    parser = argparse.ArgumentParser(description="Map video frames to GPX coordinates.")
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("gpx_path", help="Path to the GPX file")
    parser.add_argument("output_folder", help="Folder to save extracted frames")
    parser.add_argument(
        "--offset", type=float, default=0.0, help="Time offset in seconds"
    )
    parser.add_argument(
        "--distance",
        type=float,
        default=3.0,
        help="Minimum distance between frames in meters",
    )

    args = parser.parse_args()

    locator = Locator(args.gpx_path)
    reader = Reader(args.video_path, offset_seconds=args.offset)
    writer = Writer(distance=args.distance, folder=args.output_folder)

    for index, frame, frame_time in reader.read():
        try:
            lat, lon = locator.locate(frame_time)
            writer.write_frame(index, frame, frame_time, lat, lon)
        except NoCoordinates:
            print(f"No coordinates for frame {index}")


if __name__ == "__main__":
    main()
