"""Extract video embeddings using Gemini Embedding 2."""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

load_dotenv(_BACKEND_DIR / ".env")

from load_video import get_mp4_path

MODEL = "gemini-embedding-2"
DEFAULT_OUTPUT_DIMENSIONALITY = 768
SEARCH_QUERY_PREFIX = "task: search result | query: "


def get_client() -> genai.Client:
    """Create a Gemini API client using GEMINI_API_KEY."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is required. Set it in backend/.env or as an "
            "environment variable. Get a key at https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=api_key)


def _embed(
    contents: list,
    *,
    output_dimensionality: int = DEFAULT_OUTPUT_DIMENSIONALITY,
    client: genai.Client | None = None,
    label: str = "content",
) -> list[float]:
    client = client or get_client()
    result = client.models.embed_content(
        model=MODEL,
        contents=contents,
        config=types.EmbedContentConfig(
            output_dimensionality=output_dimensionality,
        ),
    )
    if not result.embeddings:
        raise RuntimeError(f"No embeddings returned for {label}")
    return list(result.embeddings[0].values)


def extract_text_embedding(
    query: str,
    *,
    output_dimensionality: int = DEFAULT_OUTPUT_DIMENSIONALITY,
    client: genai.Client | None = None,
) -> list[float]:
    """Embed a search query for cross-modal video retrieval."""
    formatted_query = f"{SEARCH_QUERY_PREFIX}{query}"
    return _embed(
        [formatted_query],
        output_dimensionality=output_dimensionality,
        client=client,
        label=f"query: {query}",
    )


def extract_segment_embedding(
    segment_bytes: bytes,
    *,
    output_dimensionality: int = DEFAULT_OUTPUT_DIMENSIONALITY,
    client: genai.Client | None = None,
) -> list[float]:
    """Embed a video segment."""
    return _embed(
        [
            types.Part.from_bytes(
                data=segment_bytes,
                mime_type="video/mp4",
            ),
        ],
        output_dimensionality=output_dimensionality,
        client=client,
        label="video segment",
    )


def extract_video_embedding(
    filename: str | None = None,
    *,
    output_dimensionality: int = DEFAULT_OUTPUT_DIMENSIONALITY,
    client: genai.Client | None = None,
) -> list[float]:
    """Embed an MP4 from the backend directory and return the embedding vector."""
    video_path = get_mp4_path(filename)
    return extract_segment_embedding(
        video_path.read_bytes(),
        output_dimensionality=output_dimensionality,
        client=client,
    )


def save_embedding(
    embedding: list[float],
    output_path: Path,
    *,
    video_path: Path | None = None,
    model: str = MODEL,
) -> Path:
    """Save an embedding vector to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": model,
        "dimensions": len(embedding),
        "video": str(video_path) if video_path else None,
        "embedding": embedding,
    }
    output_path.write_text(json.dumps(payload, indent=2))
    return output_path


if __name__ == "__main__":
    video_path = get_mp4_path()
    embedding = extract_video_embedding()
    output_file = _BACKEND_DIR / "embeddings" / f"{video_path.stem}.json"
    save_embedding(embedding, output_file, video_path=video_path)

    print(f"Video: {video_path}")
    print(f"Model: {MODEL}")
    print(f"Dimensions: {len(embedding)}")
    print(f"Saved to: {output_file}")
