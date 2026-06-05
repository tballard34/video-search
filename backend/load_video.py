"""Load MP4 video files from the backend directory."""

from pathlib import Path

import cv2

BACKEND_DIR = Path(__file__).resolve().parent


def get_mp4_path(filename: str | None = None) -> Path:
    """Return the path to an MP4 file in the backend directory."""
    if filename:
        path = BACKEND_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"MP4 not found: {path}")
        return path

    mp4_files = sorted(BACKEND_DIR.glob("*.mp4"))
    if not mp4_files:
        raise FileNotFoundError(f"No MP4 files found in {BACKEND_DIR}")
    return mp4_files[0]


def load_video(filename: str | None = None) -> cv2.VideoCapture:
    """Open an MP4 file and return a VideoCapture handle."""
    path = get_mp4_path(filename)
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise RuntimeError(f"Failed to open video: {path}")
    return capture


def get_video_info(capture: cv2.VideoCapture) -> dict:
    """Return basic metadata for an opened video."""
    return {
        "frame_count": int(capture.get(cv2.CAP_PROP_FRAME_COUNT)),
        "fps": capture.get(cv2.CAP_PROP_FPS),
        "width": int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
    }


if __name__ == "__main__":
    video = load_video()
    info = get_video_info(video)
    print(f"Loaded: {get_mp4_path()}")
    print(f"Frames: {info['frame_count']}, FPS: {info['fps']:.2f}")
    print(f"Resolution: {info['width']}x{info['height']}")
    video.release()
