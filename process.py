#!/usr/bin/env python3

"""
This script reads a video file and a GPX track to create series of geotagged images.
"""

import av
import gpxpy
from datetime import datetime, timedelta
import math

from app import Reader, Writer, Locator


def get_video_start_time(container):
    creation_time = container.metadata.get("creation_time")

    if creation_time is None:
        raise RuntimeError("creation_time missing in the video")

    creation_time = creation_time.replace('Z', '+00:00')
    return datetime.fromisoformat(creation_time)


def load_gpx(gpx_path):
    with open(gpx_path, "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    points = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if point.time is None:
                    continue

                points.append((
                    point.time,
                    point.latitude,
                    point.longitude,
                    point.elevation,
                ))

    points.sort()

    print(f"Found {len(points)} points in {gpx_path}")

    return points


def interpolate_coordinates(frame_time, prev, next):
    t1, lat1, lon1, _ = prev
    t2, lat2, lon2, _ = next

    time_delta = (t2 - t1).total_seconds()

    if time_delta == 0:
        return lat1, lon1

    time_elapsed = (frame_time - t1).total_seconds()
    fraction = time_elapsed / time_delta

    interp_lat = lat1 + (lat2 - lat1) * fraction
    interp_lon = lon1 + (lon2 - lon1) * fraction

    return interp_lat, interp_lon


def get_gps_at_time(points, current_real_time):
    prev = points[0]

    for next in points[1:]:
        if next[0] < current_real_time:
            prev = next
            continue

        return interpolate_coordinates(current_real_time, prev, next)

    return None, None


def get_distance(lat1, lon1, lat2, lon2):
    """
    Get distance in meters between two GPS points.
    """
    R = 6371000

    # Convert decimal degrees to radians
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(dlambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def write_frame(frame, idx, lat, lon):
    print(f"Writing frame {idx} << {lat},{lon}")


points = load_gpx("src/recording.gpx")

locator = Locator("src/recording.gpx")
reader = Reader("src/recording.mp4")
writer = Writer(distance=1.0)

for index, frame, frame_time in reader.read():
    lat, lon = locator.locate(frame_time)
    writer.write_frame(index, frame, frame_time, lat, lon)


container = av.open("src/recording.mp4")
stream = container.streams.video[0]

creation_time = container.metadata.get("creation_time")
video_start_time_utc = get_video_start_time(container)
print(f"Video start time is {video_start_time_utc}")

# Track GPS location of the last saved frame.
prev_location = None

for index, frame in enumerate(container.decode(stream)):
    frame_time_sec = frame.pts * stream.time_base
    time_offset = timedelta(seconds=float(frame_time_sec))
    current_real_time = video_start_time_utc + time_offset

    lat, lon = get_gps_at_time(points, current_real_time)

    print(f"Frame {index} @ {current_real_time} << {lat}, {lon}")

    write_frame(frame, index, lat, lon)
