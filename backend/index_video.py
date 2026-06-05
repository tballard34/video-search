"""Index video segments and frames into local SQLite."""

import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

load_dotenv(_BACKEND_DIR / ".env")

from chunk_video import chunk_video
from extract_embeddings import extract_segment_embedding, get_client
from frame_index import DEFAULT_FRAME_INTERVAL_SEC, index_frames
from load_video import get_mp4_path, get_video_info, load_video
from vector_store import upsert_segments


@dataclass
class IndexResult:
    video_id: str
    video_path: Path
    segments_indexed: int
    frames_indexed: int


def index_video(
    filename: str | None = None,
    *,
    segment_sec: float = 5.0,
    overlap_sec: float = 2.0,
    frame_interval_sec: float = DEFAULT_FRAME_INTERVAL_SEC,
    index_segments: bool = True,
    index_clip_frames: bool = True,
) -> IndexResult:
    """Chunk a video, embed segments and frames, and upsert into local SQLite."""
    video_path = get_mp4_path(filename)
    video_id = video_path.stem
    segments_indexed = 0
    frames_indexed = 0

    if index_segments:
        capture = load_video(filename)
        info = get_video_info(capture)
        capture.release()

        print(f"Chunking {video_path.name} ({info['frame_count']} frames)...")
        segments = chunk_video(
            video_path,
            segment_sec=segment_sec,
            overlap_sec=overlap_sec,
        )
        print(f"Created {len(segments)} segments")

        client = get_client()
        rows = []
        for segment in segments:
            print(
                f"  Embedding segment {segment.index} "
                f"({segment.start_sec:.1f}s–{segment.end_sec:.1f}s)..."
            )
            vector = extract_segment_embedding(segment.bytes, client=client)
            rows.append(
                {
                    "id": f"{video_id}:{segment.index}",
                    "vector": vector,
                    "video_id": video_id,
                    "video_path": str(video_path),
                    "segment_index": segment.index,
                    "start_sec": segment.start_sec,
                    "end_sec": segment.end_sec,
                }
            )

        upsert_segments(rows)
        segments_indexed = len(rows)
        print(f"Saved {segments_indexed} segments to local database")

    if index_clip_frames:
        frame_result = index_frames(
            filename,
            frame_interval_sec=frame_interval_sec,
        )
        frames_indexed = frame_result.frames_indexed

    return IndexResult(
        video_id=video_id,
        video_path=video_path,
        segments_indexed=segments_indexed,
        frames_indexed=frames_indexed,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Index a video for search")
    parser.add_argument("filename", nargs="?", default=None)
    parser.add_argument("--frames-only", action="store_true")
    parser.add_argument("--segments-only", action="store_true")
    parser.add_argument(
        "--frame-interval",
        type=float,
        default=DEFAULT_FRAME_INTERVAL_SEC,
        help=f"Seconds between CLIP frame samples (default: {DEFAULT_FRAME_INTERVAL_SEC})",
    )
    args = parser.parse_args()

    result = index_video(
        args.filename,
        index_segments=not args.frames_only,
        index_clip_frames=not args.segments_only,
        frame_interval_sec=args.frame_interval,
    )
    print(
        f"Indexed {result.segments_indexed} segments and "
        f"{result.frames_indexed} frames for {result.video_id}"
    )
