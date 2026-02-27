"""
This class implements a video frame reader.
"""

import av
from datetime import datetime, timedelta

class Reader:
    def __init__(self, video_path, offset_seconds=0.0):
        self._container = av.open(video_path)
        self._stream = self._container.streams.video[0]
        self._creation_time = self._get_creation_time(self._container)
        self._offset_seconds = timedelta(seconds=offset_seconds)

        print(f"Opening {video_path} to read {self._stream.frames} video frames.")


    def read(self):
        for index, frame in enumerate(self._container.decode(self._stream)):
            frame_time_sec = frame.pts * self._stream.time_base
            time_offset = timedelta(seconds=float(frame_time_sec))
            current_real_time = self._creation_time + time_offset + self._offset_seconds

            yield index, frame, current_real_time

    def _get_creation_time(self, container):
        creation_time = container.metadata.get("creation_time")

        if creation_time is None:
            raise RuntimeError("creation_time missing in the video")

        creation_time = creation_time.replace('Z', '+00:00')
        return datetime.fromisoformat(creation_time)
