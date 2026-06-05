"""Index video frames with CLIP embeddings."""

import sys
from dataclasses import dataclass
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from clip_embeddings import DEFAULT_BATCH_SIZE, embed_frames_batch
from frame_utils import extract_frame
from load_video import get_mp4_path, get_video_info, load_video
from vector_store import upsert_frames

DEFAULT_FRAME_INTERVAL_SEC = 0.25


@dataclass
class FrameIndexResult:
    video_id: str
    video_path: Path
    frames_indexed: int
    frame_interval_sec: float


def index_frames(
    filename: str | None = None,
    *,
    frame_interval_sec: float = DEFAULT_FRAME_INTERVAL_SEC,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> FrameIndexResult:
    """Sample frames at a fixed interval and upsert CLIP embeddings."""
    video_path = get_mp4_path(filename)
    video_id = video_path.stem

    capture = load_video(filename)
    info = get_video_info(capture)
    capture.release()

    fps = info["fps"]
    if fps <= 0:
        raise RuntimeError(f"Invalid FPS for video: {video_path}")

    duration_sec = info["frame_count"] / fps
    timestamps: list[float] = []
    t = 0.0
    while t < duration_sec:
        timestamps.append(t)
        t += frame_interval_sec

    print(
        f"Indexing {len(timestamps)} frames for {video_path.name} "
        f"({duration_sec:.1f}s, every {frame_interval_sec}s)..."
    )

    jpegs: list[bytes] = []
    for i, timestamp_sec in enumerate(timestamps):
        if i % 20 == 0:
            print(f"  Extracting frame {i + 1}/{len(timestamps)} at {timestamp_sec:.2f}s...")
        jpegs.append(extract_frame(video_path, timestamp_sec))

    print(f"  Embedding {len(jpegs)} frames in batches of {batch_size}...")
    vectors = embed_frames_batch(jpegs, batch_size=batch_size)

    rows = []
    for frame_index, (timestamp_sec, vector) in enumerate(zip(timestamps, vectors)):
        rows.append(
            {
                "id": f"{video_id}:frame:{frame_index}",
                "vector": vector,
                "video_id": video_id,
                "video_path": str(video_path),
                "frame_index": frame_index,
                "timestamp_sec": timestamp_sec,
            }
        )

    upsert_frames(rows)
    print(f"Saved {len(rows)} frames to local database")

    return FrameIndexResult(
        video_id=video_id,
        video_path=video_path,
        frames_indexed=len(rows),
        frame_interval_sec=frame_interval_sec,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Index video frames with CLIP")
    parser.add_argument("filename", nargs="?", default=None)
    parser.add_argument(
        "--frame-interval",
        type=float,
        default=DEFAULT_FRAME_INTERVAL_SEC,
        help=f"Seconds between sampled frames (default: {DEFAULT_FRAME_INTERVAL_SEC})",
    )
    args = parser.parse_args()

    result = index_frames(args.filename, frame_interval_sec=args.frame_interval)
    print(f"Indexed {result.frames_indexed} frames for {result.video_id}")
