import argparse

import sys

from tqdm import tqdm  # type: ignore

from . import Locator, Reader, Writer
from .exceptions import UsageException
from .locator import NoCoordinates


def handle_extract(args):
    try:
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
    except UsageException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_synchronize(args):
    print(f"Synchronizing {args.video_path} with {args.gpx_path}...")
    print("Dummy message: Synchronization logic not implemented yet.")


def main():
    parser = argparse.ArgumentParser(description="Map video frames to GPX coordinates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser(
        "extract", help="Extract frames from video and map to GPX"
    )
    extract_parser.add_argument("video_path", help="Path to the video file")
    extract_parser.add_argument("gpx_path", help="Path to the GPX file")
    extract_parser.add_argument("output_folder", help="Folder to save extracted frames")
    extract_parser.add_argument(
        "--offset", type=float, default=0.0, help="Time offset in seconds"
    )
    extract_parser.add_argument(
        "--distance",
        type=float,
        default=3.0,
        help="Minimum distance between frames in meters",
    )
    extract_parser.add_argument(
        "--timestamp",
        type=str,
        help="Manually specify the video creation date (e.g., 2026-04-27T12:44:15Z)",
    )
    extract_parser.set_defaults(func=handle_extract)

    sync_parser = subparsers.add_parser(
        "synchronize", help="Synchronize video with GPX (dummy)"
    )
    sync_parser.add_argument("video_path", help="Path to the video file")
    sync_parser.add_argument("gpx_path", help="Path to the GPX file")
    sync_parser.set_defaults(func=handle_synchronize)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
