"""Local SQLite vector store for video segment and frame embeddings."""

import json
import sqlite3
from pathlib import Path

import numpy as np

_BACKEND_DIR = Path(__file__).resolve().parent
DB_PATH = _BACKEND_DIR / "data" / "video_search.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS segments (
    id TEXT PRIMARY KEY,
    video_id TEXT NOT NULL,
    video_path TEXT NOT NULL,
    segment_index INTEGER NOT NULL,
    start_sec REAL NOT NULL,
    end_sec REAL NOT NULL,
    vector TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_segments_video_id ON segments(video_id);

CREATE TABLE IF NOT EXISTS frames (
    id TEXT PRIMARY KEY,
    video_id TEXT NOT NULL,
    video_path TEXT NOT NULL,
    frame_index INTEGER NOT NULL,
    timestamp_sec REAL NOT NULL,
    vector TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_frames_video_id ON frames(video_id);
"""


def get_db_path() -> Path:
    return DB_PATH


def init_db(db_path: Path | None = None) -> None:
    """Create tables if they do not exist."""
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.executescript(_SCHEMA)


def upsert_segments(rows: list[dict], db_path: Path | None = None) -> int:
    """Insert or replace segment rows. Returns number of rows written."""
    path = db_path or DB_PATH
    init_db(path)

    with sqlite3.connect(path) as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO segments
                (id, video_id, video_path, segment_index, start_sec, end_sec, vector)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row["id"],
                    row["video_id"],
                    row["video_path"],
                    row["segment_index"],
                    row["start_sec"],
                    row["end_sec"],
                    json.dumps(row["vector"]),
                )
                for row in rows
            ],
        )
        return len(rows)


def upsert_frames(rows: list[dict], db_path: Path | None = None) -> int:
    """Insert or replace frame rows. Returns number of rows written."""
    path = db_path or DB_PATH
    init_db(path)

    with sqlite3.connect(path) as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO frames
                (id, video_id, video_path, frame_index, timestamp_sec, vector)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row["id"],
                    row["video_id"],
                    row["video_path"],
                    row["frame_index"],
                    row["timestamp_sec"],
                    json.dumps(row["vector"]),
                )
                for row in rows
            ],
        )
        return len(rows)


def _cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 1.0
    return float(1.0 - np.dot(a, b) / denom)


def search_segments(
    query_vector: list[float],
    *,
    top_k: int = 5,
    video_id: str | None = None,
    db_path: Path | None = None,
) -> list[dict]:
    """Return top-k segments ranked by cosine distance to the query vector."""
    path = db_path or DB_PATH
    init_db(path)

    query = np.array(query_vector, dtype=np.float32)

    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        if video_id:
            rows = conn.execute(
                "SELECT * FROM segments WHERE video_id = ?",
                (video_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM segments").fetchall()

    results = []
    for row in rows:
        vector = np.array(json.loads(row["vector"]), dtype=np.float32)
        results.append(
            {
                "id": row["id"],
                "video_id": row["video_id"],
                "video_path": row["video_path"],
                "segment_index": row["segment_index"],
                "start_sec": row["start_sec"],
                "end_sec": row["end_sec"],
                "distance": _cosine_distance(query, vector),
            }
        )

    results.sort(key=lambda r: r["distance"])
    return results[:top_k]


def search_frames(
    query_vector: list[float],
    *,
    top_k: int = 5,
    video_id: str | None = None,
    db_path: Path | None = None,
) -> list[dict]:
    """Return top-k frames ranked by cosine distance to the query vector."""
    path = db_path or DB_PATH
    init_db(path)

    query = np.array(query_vector, dtype=np.float32)

    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        if video_id:
            rows = conn.execute(
                "SELECT * FROM frames WHERE video_id = ?",
                (video_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM frames").fetchall()

    results = []
    for row in rows:
        vector = np.array(json.loads(row["vector"]), dtype=np.float32)
        results.append(
            {
                "id": row["id"],
                "video_id": row["video_id"],
                "video_path": row["video_path"],
                "frame_index": row["frame_index"],
                "timestamp_sec": row["timestamp_sec"],
                "distance": _cosine_distance(query, vector),
            }
        )

    results.sort(key=lambda r: r["distance"])
    return results[:top_k]
