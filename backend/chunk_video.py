"""Split videos into overlapping time-bounded segments."""

from dataclasses import dataclass
from pathlib import Path
import tempfile

import cv2


@dataclass
class VideoSegment:
    index: int
    start_sec: float
    end_sec: float
    bytes: bytes
    mime_type: str = "video/mp4"


def chunk_video(
    video_path: Path,
    *,
    segment_sec: float = 5.0,
    overlap_sec: float = 2.0,
) -> list[VideoSegment]:
    """Split a video into overlapping MP4 segments."""
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        capture.release()
        raise RuntimeError(f"Invalid FPS for video: {video_path}")

    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_sec = frame_count / fps

    step_sec = segment_sec - overlap_sec
    if step_sec <= 0:
        capture.release()
        raise ValueError("overlap_sec must be less than segment_sec")

    segments: list[VideoSegment] = []
    start_sec = 0.0
    index = 0

    while start_sec < duration_sec:
        end_sec = min(start_sec + segment_sec, duration_sec)
        segment_bytes = _extract_segment_bytes(
            capture,
            start_sec=start_sec,
            end_sec=end_sec,
            fps=fps,
            width=width,
            height=height,
        )
        if segment_bytes:
            segments.append(
                VideoSegment(
                    index=index,
                    start_sec=start_sec,
                    end_sec=end_sec,
                    bytes=segment_bytes,
                )
            )
            index += 1

        if end_sec >= duration_sec:
            break
        start_sec += step_sec

    capture.release()
    return segments


def extract_segment(video_path: Path, start_sec: float, end_sec: float) -> bytes:
    """Extract a single MP4 segment from a video."""
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    segment_bytes = _extract_segment_bytes(
        capture,
        start_sec=start_sec,
        end_sec=end_sec,
        fps=fps,
        width=width,
        height=height,
    )
    capture.release()

    if not segment_bytes:
        raise RuntimeError(
            f"Failed to extract segment {start_sec}-{end_sec}s from {video_path}"
        )
    return segment_bytes


def _extract_segment_bytes(
    capture: cv2.VideoCapture,
    *,
    start_sec: float,
    end_sec: float,
    fps: float,
    width: int,
    height: int,
) -> bytes | None:
    start_frame = int(start_sec * fps)
    end_frame = int(end_sec * fps)

    capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=True) as tmp:
        writer = cv2.VideoWriter(
            tmp.name,
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )
        if not writer.isOpened():
            raise RuntimeError("Failed to create segment video writer")

        frame_idx = start_frame
        while frame_idx < end_frame:
            ok, frame = capture.read()
            if not ok:
                break
            writer.write(frame)
            frame_idx += 1

        writer.release()
        data = Path(tmp.name).read_bytes()
        return data if data else None
