"""FastAPI HTTP API for video indexing and search."""

import sys
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from dotenv import load_dotenv

load_dotenv(_BACKEND_DIR / ".env")

from frame_utils import extract_frame
from frame_index import DEFAULT_FRAME_INTERVAL_SEC
from index_video import index_video
from load_video import BACKEND_DIR
from search import SearchMatch, search_videos

SearchBackend = Literal["clip", "gemini", "hybrid"]

app = FastAPI(
    title="Video Search API",
    description="Search indexed videos by natural-language prompt.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IndexRequest(BaseModel):
    filename: str | None = None
    index_segments: bool = True
    index_clip_frames: bool = True
    frame_interval_sec: float = Field(
        default=DEFAULT_FRAME_INTERVAL_SEC,
        gt=0,
        description="Seconds between CLIP frame samples (default 0.25 = 4 fps)",
    )


class IndexResponse(BaseModel):
    video_id: str
    video_path: str
    segments_indexed: int
    frames_indexed: int


class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Natural language search prompt")
    top_k: int = Field(default=5, ge=1, le=20)
    video_id: str | None = Field(
        default=None,
        description="Limit search to a single indexed video",
    )
    refine: bool = Field(
        default=True,
        description="Use Gemini vision to pinpoint the moment in top candidates",
    )
    backend: SearchBackend = Field(
        default="clip",
        description="clip (frame-level), gemini (segment-level), or hybrid",
    )


class PromptResult(BaseModel):
    video_id: str
    timestamp_sec: float
    distance: float
    confidence: str | None = None
    description: str | None = None
    frame_url: str


class PromptResponse(BaseModel):
    prompt: str
    backend: SearchBackend
    results: list[PromptResult]


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    video_id: str | None = None
    refine: bool = True
    backend: SearchBackend = "clip"


class SearchMatchResponse(BaseModel):
    video_id: str
    video_path: str
    segment_index: int
    segment_start_sec: float
    segment_end_sec: float
    distance: float
    refined_timestamp_sec: float | None = None
    confidence: str | None = None
    description: str | None = None
    frame_url: str | None = None


class SearchResponse(BaseModel):
    query: str
    backend: SearchBackend
    matches: list[SearchMatchResponse]


def _run_search(
    prompt: str,
    *,
    top_k: int,
    video_id: str | None,
    refine: bool,
    backend: SearchBackend,
) -> list[SearchMatch]:
    return search_videos(
        prompt,
        top_k=top_k,
        video_id=video_id,
        refine=refine,
        backend=backend,
    )


def _match_to_prompt_result(match: SearchMatch) -> PromptResult:
    timestamp = match.refined_timestamp_sec or match.segment_start_sec
    return PromptResult(
        video_id=match.video_id,
        timestamp_sec=timestamp,
        distance=match.distance,
        confidence=match.confidence,
        description=match.description,
        frame_url=match.frame_url or f"/videos/{match.video_id}/frame?t={timestamp:.2f}",
    )


def _match_to_response(match: SearchMatch) -> SearchMatchResponse:
    return SearchMatchResponse(
        video_id=match.video_id,
        video_path=match.video_path,
        segment_index=match.segment_index,
        segment_start_sec=match.segment_start_sec,
        segment_end_sec=match.segment_end_sec,
        distance=match.distance,
        refined_timestamp_sec=match.refined_timestamp_sec,
        confidence=match.confidence,
        description=match.description,
        frame_url=match.frame_url,
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/prompt", response_model=PromptResponse)
def prompt_search_post(request: PromptRequest) -> PromptResponse:
    """Search indexed videos with a natural-language prompt."""
    try:
        matches = _run_search(
            request.prompt,
            top_k=request.top_k,
            video_id=request.video_id,
            refine=request.refine,
            backend=request.backend,
        )
    except (EnvironmentError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PromptResponse(
        prompt=request.prompt,
        backend=request.backend,
        results=[_match_to_prompt_result(m) for m in matches],
    )


@app.get("/prompt", response_model=PromptResponse)
def prompt_search_get(
    prompt: str = Query(..., min_length=1, description="Natural language search prompt"),
    top_k: int = Query(default=5, ge=1, le=20),
    video_id: str | None = Query(default=None),
    refine: bool = Query(default=True),
    backend: SearchBackend = Query(default="clip"),
) -> PromptResponse:
    """Search indexed videos (GET variant for quick testing)."""
    try:
        matches = _run_search(
            prompt,
            top_k=top_k,
            video_id=video_id,
            refine=refine,
            backend=backend,
        )
    except (EnvironmentError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PromptResponse(
        prompt=prompt,
        backend=backend,
        results=[_match_to_prompt_result(m) for m in matches],
    )


@app.post("/search", response_model=SearchResponse)
def search_endpoint(request: SearchRequest) -> SearchResponse:
    """Legacy search endpoint (same as /prompt, detailed match fields)."""
    try:
        matches = _run_search(
            request.query,
            top_k=request.top_k,
            video_id=request.video_id,
            refine=request.refine,
            backend=request.backend,
        )
    except (EnvironmentError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return SearchResponse(
        query=request.query,
        backend=request.backend,
        matches=[_match_to_response(match) for match in matches],
    )


@app.post("/videos/index", response_model=IndexResponse)
def index_video_endpoint(request: IndexRequest) -> IndexResponse:
    try:
        result = index_video(
            request.filename,
            index_segments=request.index_segments,
            index_clip_frames=request.index_clip_frames,
            frame_interval_sec=request.frame_interval_sec,
        )
    except (FileNotFoundError, EnvironmentError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return IndexResponse(
        video_id=result.video_id,
        video_path=str(result.video_path),
        segments_indexed=result.segments_indexed,
        frames_indexed=result.frames_indexed,
    )


@app.get("/videos/{video_id}/frame")
def get_frame(
    video_id: str,
    t: float = Query(..., description="Timestamp in seconds"),
) -> Response:
    video_path = BACKEND_DIR / f"{video_id}.mp4"
    if not video_path.exists():
        matches = list(BACKEND_DIR.glob(f"{video_id}*.mp4"))
        if not matches:
            raise HTTPException(status_code=404, detail=f"Video not found: {video_id}")
        video_path = matches[0]

    try:
        jpeg = extract_frame(video_path, t)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return Response(content=jpeg, media_type="image/jpeg")
