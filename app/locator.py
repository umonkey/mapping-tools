"""
This service gets exact GPS coordinates from a GPX track by a timestamp.
Uses interpolation to accurately tag frames between GPS data points.
"""

import gpxpy

class Locator:
    def __init__(self, gpx_path):
        self._points = self._load_points(gpx_path)

        print(f"Found {len(self._points)} points in {gpx_path}")

    def locate(self, time):
        """
        Get precise GPS coordinates by time.
        """
        prev, next = self._find_points(time)

        if prev is None or next is None:
            return None, None  # Could not locate anything.

        lat, lon = self._interpolate(time, prev, next)

        return lat, lon

    def _load_points(self, gpx_path):
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

        return points

    def _find_points(self, current_real_time):
        prev = self._points[0]

        for next in self._points[1:]:
            if next[0] < current_real_time:
                prev = next
                continue

            return prev, next

        return None, None

    def _interpolate(self, frame_time, prev, next):
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
