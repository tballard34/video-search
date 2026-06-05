"""Index a video into searchable segments."""

import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from index_video import index_video
from load_video import get_mp4_path, get_video_info, load_video


def main(filename: str | None = None) -> None:
    video_path = get_mp4_path(filename)

    print("Loading video...")
    capture = load_video(filename)
    info = get_video_info(capture)
    capture.release()

    print(f"Loaded: {video_path}")
    print(f"Frames: {info['frame_count']}, FPS: {info['fps']:.2f}")
    print(f"Resolution: {info['width']}x{info['height']}")

    print("Indexing video segments...")
    result = index_video(filename)

    print(f"Indexed {result.segments_indexed} segments for {result.video_id}")
    print("Search via: python search.py \"your query\"")
    print("Or start API:  uvicorn api:app --reload --port 8000")
    print("Then POST:     curl -X POST http://localhost:8000/prompt -H 'Content-Type: application/json' -d '{\"prompt\":\"your query\"}'")


if __name__ == "__main__":
    main()
