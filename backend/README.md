# David and Trent Video Search

Search indexed videos by natural-language prompt using CLIP frame embeddings (default), Gemini segment embeddings, or a hybrid of both.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set `GEMINI_API_KEY` in `backend/.env` (required for indexing segments and optional search refinement).

## Index a video

```bash
cd backend
python index_video.py              # segments + CLIP frames (0.25s interval)
python index_video.py --frames-only  # CLIP frames only
```

## Run the API

```bash
cd backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Open interactive docs: http://localhost:8000/docs

## Search by prompt

**POST `/prompt`** (recommended)

```bash
curl -s -X POST http://localhost:8000/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show me the frame where the ball is caught",
    "top_k": 5,
    "backend": "clip",
    "refine": true
  }' | jq
```

**GET `/prompt`** (quick test)

```bash
curl -s "http://localhost:8000/prompt?prompt=ball%20caught&backend=clip&top_k=3" | jq
```

### Response shape

```json
{
  "prompt": "Show me the frame where the ball is caught",
  "backend": "clip",
  "results": [
    {
      "video_id": "my_video",
      "timestamp_sec": 9.0,
      "distance": 0.74,
      "confidence": "high",
      "description": "Player catches the pass",
      "frame_url": "/videos/my_video/frame?t=9.00"
    }
  ]
}
```

Fetch the frame image: `GET http://localhost:8000{videos/{video_id}/frame?t=9.0}`

### Backends

| `backend` | Description |
|-----------|-------------|
| `clip` | Local CLIP frame search (default) |
| `gemini` | Gemini Embedding 2 on 5s video segments |
| `hybrid` | Fuses CLIP frames + Gemini segments |

### Other endpoints

- `POST /videos/index` — index segments and/or CLIP frames
- `POST /search` — legacy response with segment fields
- `GET /health` — health check
