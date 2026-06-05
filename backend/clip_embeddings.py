"""Local CLIP embeddings for frame-level image-text search."""

from __future__ import annotations

import io
from functools import lru_cache

import open_clip
import torch
from PIL import Image

MODEL_NAME = "ViT-B-32"
PRETRAINED = "openai"
DEFAULT_BATCH_SIZE = 16


def _get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


@lru_cache(maxsize=1)
def _load_model() -> tuple[torch.nn.Module, object, torch.device, object]:
    device = _get_device()
    model, _, preprocess = open_clip.create_model_and_transforms(
        MODEL_NAME,
        pretrained=PRETRAINED,
        force_quick_gelu=True,
    )
    model = model.to(device)
    model.eval()
    tokenizer = open_clip.get_tokenizer(MODEL_NAME)
    return model, preprocess, device, tokenizer


def _normalize_batch(embeddings: torch.Tensor) -> list[list[float]]:
    vectors = embeddings / embeddings.norm(dim=-1, keepdim=True)
    return vectors.cpu().tolist()


def embed_text(query: str) -> list[float]:
    """Embed a search query with the CLIP text encoder."""
    model, _, device, tokenizer = _load_model()
    tokens = tokenizer([query]).to(device)
    with torch.no_grad():
        features = model.encode_text(tokens)
    return _normalize_batch(features.float())[0]


def embed_frame(jpeg_bytes: bytes) -> list[float]:
    """Embed a single JPEG frame with the CLIP image encoder."""
    return embed_frames_batch([jpeg_bytes])[0]


def embed_frames_batch(
    jpeg_batches: list[bytes],
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[list[float]]:
    """Embed multiple JPEG frames, processing in batches for throughput."""
    if not jpeg_batches:
        return []

    model, preprocess, device, _ = _load_model()
    all_vectors: list[list[float]] = []

    for offset in range(0, len(jpeg_batches), batch_size):
        chunk = jpeg_batches[offset : offset + batch_size]
        images = [
            preprocess(Image.open(io.BytesIO(data)).convert("RGB")) for data in chunk
        ]
        tensor = torch.stack(images).to(device)
        with torch.no_grad():
            features = model.encode_image(tensor)
        all_vectors.extend(_normalize_batch(features.float()))

    return all_vectors
