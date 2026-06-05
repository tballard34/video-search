"""Search indexed video segments and frames by natural language query."""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from google.genai import types

_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

load_dotenv(_BACKEND_DIR / ".env")

from chunk_video import extract_segment
from clip_embeddings import embed_text as clip_embed_text
from extract_embeddings import extract_text_embedding, get_client
from vector_store import search_frames, search_segments

REFINEMENT_MODEL = "gemini-2.5-flash"
REFINE_TOP_N = 3
CLIP_REFINE_TOP_N = 8
CLIP_CANDIDATE_POOL = 15
NARROW_REFINE_WINDOW_SEC = 1.5
HYBRID_CLIP_WEIGHT = 0.7
HYBRID_GEMINI_WEIGHT = 0.3

SearchBackend = Literal["clip", "gemini", "hybrid"]

_CONFIDENCE_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class SearchMatch:
    video_id: str
    video_path: str
    segment_index: int
    segment_start_sec: float
    segment_end_sec: float
    distance: float
    refined_timestamp_sec: float | None = None
    confidence: str | None = None
    description: str | None = None

    @property
    def frame_url(self) -> str | None:
        timestamp = self.refined_timestamp_sec or self.segment_start_sec
        return f"/videos/{self.video_id}/frame?t={timestamp:.2f}"


def search_videos(
    query: str,
    *,
    top_k: int = 5,
    video_id: str | None = None,
    refine: bool = True,
    backend: SearchBackend = "clip",
) -> list[SearchMatch]:
    """Search indexed content for a natural language query."""
    if backend == "clip":
        return _search_clip(query, top_k=top_k, video_id=video_id, refine=refine)
    if backend == "gemini":
        return _search_gemini(query, top_k=top_k, video_id=video_id, refine=refine)
    return _search_hybrid(query, top_k=top_k, video_id=video_id, refine=refine)


def _search_clip(
    query: str,
    *,
    top_k: int,
    video_id: str | None,
    refine: bool,
) -> list[SearchMatch]:
    query_vector = clip_embed_text(query)
    pool_size = max(top_k, CLIP_CANDIDATE_POOL) if refine else top_k
    results = search_frames(query_vector, top_k=pool_size, video_id=video_id)

    matches = [_frame_row_to_match(row) for row in results]

    if refine and matches:
        matches = _rerank_clip_with_refinement(query, matches)
        return matches[:top_k]

    return matches[:top_k]


def _search_gemini(
    query: str,
    *,
    top_k: int,
    video_id: str | None,
    refine: bool,
) -> list[SearchMatch]:
    query_vector = extract_text_embedding(query)
    results = search_segments(query_vector, top_k=top_k, video_id=video_id)
    matches = [_segment_row_to_match(row) for row in results]

    if refine and matches:
        matches = _rerank_with_refinement(query, matches)

    return matches


def _search_hybrid(
    query: str,
    *,
    top_k: int,
    video_id: str | None,
    refine: bool,
) -> list[SearchMatch]:
    clip_vector = clip_embed_text(query)
    gemini_vector = extract_text_embedding(query)

    clip_pool = max(top_k, CLIP_CANDIDATE_POOL) if refine else max(top_k * 2, 10)
    clip_results = search_frames(clip_vector, top_k=clip_pool, video_id=video_id)
    gemini_results = search_segments(
        gemini_vector, top_k=max(top_k * 2, 10), video_id=video_id
    )

    fused: list[SearchMatch] = []
    for row in clip_results:
        timestamp = row["timestamp_sec"]
        gemini_distances = [
            g["distance"]
            for g in gemini_results
            if g["start_sec"] <= timestamp <= g["end_sec"]
        ]
        gemini_bonus = min(gemini_distances) if gemini_distances else 1.0
        fused_distance = (
            HYBRID_CLIP_WEIGHT * row["distance"]
            + HYBRID_GEMINI_WEIGHT * gemini_bonus
        )
        match = _frame_row_to_match(row)
        match.distance = fused_distance
        fused.append(match)

    fused.sort(key=lambda m: m.distance)
    matches = fused[:top_k]

    if refine and matches:
        matches = _rerank_clip_with_refinement(query, matches)
        return matches[:top_k]

    return matches


def _rerank_clip_with_refinement(
    query: str, matches: list[SearchMatch]
) -> list[SearchMatch]:
    """Refine top CLIP frame candidates and rerank by vision confidence then distance."""
    candidates = matches[:CLIP_REFINE_TOP_N]
    for match in candidates:
        refinement = _refine_narrow_window(query, match)
        match.refined_timestamp_sec = refinement.get("absolute_timestamp_sec")
        match.confidence = refinement.get("confidence")
        match.description = refinement.get("description")

    candidates.sort(
        key=lambda m: (
            _CONFIDENCE_RANK.get(m.confidence, 3),
            m.distance,
        )
    )
    refined_ids = {id(m) for m in candidates}
    remainder = [m for m in matches if id(m) not in refined_ids]
    return candidates + remainder


def _frame_row_to_match(row: dict) -> SearchMatch:
    ts = row["timestamp_sec"]
    return SearchMatch(
        video_id=row["video_id"],
        video_path=row["video_path"],
        segment_index=row["frame_index"],
        segment_start_sec=ts,
        segment_end_sec=ts,
        distance=row["distance"],
        refined_timestamp_sec=ts,
    )


def _segment_row_to_match(row: dict) -> SearchMatch:
    return SearchMatch(
        video_id=row["video_id"],
        video_path=row["video_path"],
        segment_index=row["segment_index"],
        segment_start_sec=row["start_sec"],
        segment_end_sec=row["end_sec"],
        distance=row["distance"],
    )


def _rerank_with_refinement(
    query: str, matches: list[SearchMatch]
) -> list[SearchMatch]:
    """Refine top-N segment matches and rerank by vision confidence then distance."""
    candidates = matches[:REFINE_TOP_N]
    for match in candidates:
        refinement = _refine_match(query, match)
        match.refined_timestamp_sec = refinement.get("absolute_timestamp_sec")
        match.confidence = refinement.get("confidence")
        match.description = refinement.get("description")

    candidates.sort(
        key=lambda m: (
            _CONFIDENCE_RANK.get(m.confidence, 3),
            m.distance,
        )
    )
    refined_ids = {id(m) for m in candidates}
    remainder = [m for m in matches if id(m) not in refined_ids]
    return candidates + remainder


def _refine_narrow_window(query: str, match: SearchMatch) -> dict:
    """Refine around the CLIP top frame using a short clip (±window)."""
    center = match.refined_timestamp_sec or match.segment_start_sec
    start_sec = max(0.0, center - NARROW_REFINE_WINDOW_SEC)
    end_sec = center + NARROW_REFINE_WINDOW_SEC
    narrow_match = SearchMatch(
        video_id=match.video_id,
        video_path=match.video_path,
        segment_index=match.segment_index,
        segment_start_sec=start_sec,
        segment_end_sec=end_sec,
        distance=match.distance,
    )
    return _refine_match(query, narrow_match)


def _refine_match(query: str, match: SearchMatch) -> dict:
    """Use a vision model to pinpoint the moment inside a segment."""
    video_path = Path(match.video_path)
    segment_bytes = extract_segment(
        video_path,
        match.segment_start_sec,
        match.segment_end_sec,
    )
    clip_duration = match.segment_end_sec - match.segment_start_sec

    prompt = f"""Watch this video clip and find the moment that best matches the user's query.

The clip is {clip_duration:.1f} seconds long. Return timestamps relative to the start of this clip (0.0 to {clip_duration:.1f}).

User query: {query}

Return JSON with:
- timestamp_sec: number or null (seconds into this clip)
- confidence: "high", "medium", or "low"
- description: brief description of the matched moment
"""

    client = get_client()
    response = client.models.generate_content(
        model=REFINEMENT_MODEL,
        contents=[
            types.Part.from_bytes(data=segment_bytes, mime_type="video/mp4"),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )

    parsed = json.loads(response.text)
    relative_ts = parsed.get("timestamp_sec")
    absolute_ts = None
    if relative_ts is not None:
        absolute_ts = match.segment_start_sec + float(relative_ts)

    return {
        "absolute_timestamp_sec": absolute_ts,
        "confidence": parsed.get("confidence"),
        "description": parsed.get("description"),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search indexed videos")
    parser.add_argument("query", help="Natural language search query")
    parser.add_argument(
        "--backend",
        choices=["clip", "gemini", "hybrid"],
        default="clip",
        help="Search backend (default: clip)",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--no-refine", action="store_true")
    parser.add_argument("--video-id", default=None)
    args = parser.parse_args()

    results = search_videos(
        args.query,
        top_k=args.top_k,
        video_id=args.video_id,
        refine=not args.no_refine,
        backend=args.backend,
    )
    for i, match in enumerate(results, 1):
        print(f"\nMatch {i} (distance={match.distance:.4f})")
        print(f"  Video: {match.video_id}")
        if match.segment_start_sec == match.segment_end_sec:
            print(f"  Frame: {match.segment_start_sec:.1f}s")
        else:
            print(
                f"  Segment: {match.segment_start_sec:.1f}s–"
                f"{match.segment_end_sec:.1f}s"
            )
        if match.refined_timestamp_sec is not None:
            print(f"  Refined: {match.refined_timestamp_sec:.2f}s ({match.confidence})")
            print(f"  Description: {match.description}")
        print(f"  Frame URL: {match.frame_url}")
