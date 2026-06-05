"""Extract frames from video files."""

from pathlib import Path

import cv2


def extract_frame(video_path: Path, timestamp_sec: float) -> bytes:
    """Return a JPEG image for the frame at the given timestamp."""
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    capture.set(cv2.CAP_PROP_POS_MSEC, timestamp_sec * 1000)
    ok, frame = capture.read()
    capture.release()

    if not ok or frame is None:
        raise RuntimeError(
            f"Failed to read frame at {timestamp_sec}s from {video_path}"
        )

    ok, buffer = cv2.imencode(".jpg", frame)
    if not ok:
        raise RuntimeError(f"Failed to encode frame at {timestamp_sec}s")

    return buffer.tobytes()
