"""
This class implements a video frame reader.
"""

from datetime import datetime, timedelta

import av


class Reader:
    def __init__(self, video_path, offset_seconds=0.0):
        self._container = av.open(video_path)
        self._stream = self._container.streams.video[0]
        self._creation_time = self._get_creation_time(self._container)
        self._offset_seconds = timedelta(seconds=offset_seconds)

        self.total_frames = self._get_total_frames()
        print(f"Opening {video_path} to read {self.total_frames} video frames.")

    def _get_total_frames(self):
        """
        Returns the total number of frames in the video stream.
        Uses the metadata if available, otherwise estimates from duration
        and frame rate.
        """
        if self._stream.frames:
            return self._stream.frames

        if self._stream.duration and self._stream.average_rate:
            return int(
                self._stream.duration
                * self._stream.time_base
                * self._stream.average_rate
            )

        return 0

    def read(self):
        for index, frame in enumerate(self._container.decode(self._stream)):
            frame_time_sec = frame.pts * self._stream.time_base
            time_offset = timedelta(seconds=float(frame_time_sec))
            current_real_time = self._creation_time + time_offset + self._offset_seconds
            progress = self._get_progress(index)

            yield index, frame, current_real_time, progress

    def _get_progress(self, index):
        """
        Calculates current progress percentage.
        """
        if self.total_frames > 0:
            return (index + 1) / self.total_frames * 100
        return 0.0

    def _get_creation_time(self, container):
        creation_time = container.metadata.get("creation_time")

        if creation_time is None:
            raise RuntimeError("creation_time missing in the video")

        creation_time = creation_time.replace("Z", "+00:00")
        return datetime.fromisoformat(creation_time)
