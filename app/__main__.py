import argparse

from tqdm import tqdm

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
    parser.add_argument(
        "--timestamp",
        type=str,
        help="Manually specify the video creation date (e.g., 2026-04-27T12:44:15Z)",
    )

    args = parser.parse_args()

    locator = Locator(args.gpx_path)
    reader = Reader(
        args.video_path, offset_seconds=args.offset, timestamp=args.timestamp
    )
    writer = Writer(distance=args.distance, folder=args.output_folder)

    for index, frame, frame_time, progress in tqdm(
        reader.read(), total=reader.total_frames, desc="Processing frames"
    ):
        try:
            lat, lon = locator.locate(frame_time)
            writer.write_frame(index, frame, frame_time, lat, lon)
        except NoCoordinates:
            # print(f"No coordinates for frame {index}")
            pass


if __name__ == "__main__":
    main()
