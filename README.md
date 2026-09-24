# Agri-LLaVA

Multimodal AI system for crop disease detection — upload a leaf photo, get a grounded,
structured explanation of the disease, its causes, and treatment options, in English,
Hindi, or Telugu.

## Overview

Agri-LLaVA is a full-stack application built for farmers and non-technical users. It pairs
a React frontend with a FastAPI backend that validates images, runs model inference, and
grounds the result in a curated agricultural knowledge base (RAG) before returning it.

## Current Status

- ✅ Backend: fully working, tested (`pytest`, 9/9 passing), runs in **mock inference mode**
  by default so it's usable without a GPU or trained model.
- ✅ Frontend: fully working, builds clean (`npm run build`), connects to the backend over
  `VITE_API_URL`.
- ⏳ Real model (Qwen2.5-VL-7B-Instruct + LoRA adapter): not yet plugged in. The backend's
  `ModelInferenceService` abstraction is ready for it — see `backend/app/services/model_service.py`.
  Once you have a trained adapter and a deployed GPU inference endpoint, set `INFERENCE_MODE=remote`
  and `MODEL_API_URL` and no other code changes are needed.

## Project Structure

```
agri-llava/
├── frontend/       React + TypeScript + Vite + Tailwind UI
├── backend/        FastAPI inference API (mock mode by default)
├── knowledge/      crop_diseases.json — the grounded knowledge base
├── ml/             (scaffolded — dataset prep / training / inference, not yet built)
├── docs/           (scaffolded — architecture, deployment, interview notes)
└── scripts/
```

## Quick Start (Windows)

### 1. Backend

Requires **Python 3.11** specifically (not 3.13/3.14 — newer versions don't yet have
prebuilt wheels for some dependencies here). If you don't have 3.11, install it from
https://www.python.org/downloads/release/python-3119/ ("Windows installer (64-bit)").

```cmd
cd backend
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Visit `http://127.0.0.1:8000/docs` to confirm it's running.

### 2. Frontend

Requires Node.js 18+ (any recent LTS is fine).

```cmd
cd frontend
copy .env.example .env
npm install
npm run dev
```

Visit `http://localhost:5173`. Upload any JPEG/PNG/WEBP image, optionally type or speak a
question, pick a language, and click "Analyze Crop." You'll get a structured result —
currently from the mock inference service (clearly labeled in the UI), since the real
model isn't plugged in yet.

### macOS/Linux

Same steps, but activate the venv with `source venv/bin/activate` and use `python3`
instead of `py -3.11` if you don't have multiple Python versions installed.

## Environment Variables

**backend/.env**
| Variable | Purpose |
|---|---|
| `ENVIRONMENT` | `development` or `production`. Mock inference is blocked in production. |
| `INFERENCE_MODE` | `mock` (default, fake responses), `remote` (calls a GPU service), `local` (not yet implemented). |
| `MODEL_API_URL` | Required if `INFERENCE_MODE=remote`. |
| `ALLOWED_ORIGINS` | Comma-separated frontend origins allowed by CORS. |
| `MAX_IMAGE_SIZE_MB` | Upload size limit. |

**frontend/.env**
| Variable | Purpose |
|---|---|
| `VITE_API_URL` | Base URL of the backend, e.g. `http://localhost:8000`. |

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/api/v1/analyze` (alias `/api/v1/predict`) | Image + text + language → structured analysis |
| GET | `/api/v1/diseases` | Lists all known crop/disease entries in the knowledge base |
| POST | `/api/v1/feedback` | Accepts user feedback (logged, not stored) |

## Testing

```cmd
cd backend
venv\Scripts\activate
pytest -v
```

9 tests cover health, valid analysis (English + Hindi), and every required error case
(missing image, unsupported language, non-image file, corrupted image).

## Deployment

### Frontend → Vercel

Create a Vercel project with **Root Directory = `frontend`**. Build command
`npm run build` and output directory `dist` are auto-detected from
`package.json`/Vite — no `vercel.json` needed. Set `VITE_API_URL` in the
project's Environment Variables to your deployed backend URL. Never hard-code it.

### Backend → Vercel (or any host that runs a standard ASGI app)

The backend is CPU-only and lightweight by design — in `INFERENCE_MODE=remote`
it doesn't run the model itself, it forwards requests to a separately-deployed
GPU inference service. This makes it deployable on Vercel as its own project:

1. Create a **second, separate** Vercel project from the same repo, with
   **Root Directory = `backend`**.
2. Vercel auto-detects the FastAPI app at `app/main.py` (zero-config — no
   `vercel.json` required for a basic deploy).
3. Set environment variables in that project's dashboard:
   - `INFERENCE_MODE=mock` for now (until a real GPU inference service exists).
   - **Do not set `ENVIRONMENT=production` until `INFERENCE_MODE` is `remote`**
     — the app deliberately refuses to start with `ENVIRONMENT=production` +
     `INFERENCE_MODE=mock`, to stop fake predictions from accidentally
     shipping. Leave `ENVIRONMENT` unset (defaults to `development`) while
     using mock mode.
   - `ALLOWED_ORIGINS` = your frontend's Vercel URL.
4. Redeploy, then point the frontend project's `VITE_API_URL` at this
   backend's URL (e.g. `https://your-backend.vercel.app`).

**Important — a real cause of "Application startup failed" on Vercel:** the
backend loads `knowledge/crop_diseases.json` during startup and deliberately
crashes if that file is missing, rather than silently returning ungrounded
answers. Vercel only bundles files inside the project's Root Directory, so a
copy of the knowledge base is kept at `backend/knowledge/crop_diseases.json`
(self-contained within the backend project) — the top-level `/knowledge/`
copy is for documentation and future dataset tooling only. If you ever add
new entries, update both copies, or wire up a small sync check.

### Alternative: Docker, or any non-Vercel host

`backend/Dockerfile` builds a self-contained image (build from the repo root:
`docker build -f backend/Dockerfile -t agri-llava-backend .`). Use this for
Render, Railway, Fly.io, or any other host if you'd rather not use Vercel for
the backend.

### Model inference (GPU)

Not yet built. This is the next major piece — see "Current Status" above.

## Known Limitations

- Model inference is currently mocked; predictions are not real until a trained
  Qwen2.5-VL + LoRA adapter is deployed and `INFERENCE_MODE=remote` is configured.
- No CV baseline (EfficientNet/ResNet) model yet — scaffolded in `ml/` but not built.
- Knowledge base currently covers 10 crop/disease combinations; expand
  `knowledge/crop_diseases.json` (and re-run `scripts/add_translations.py`'s
  data) for broader coverage.
- **Hindi/Telugu translations of agricultural content need expert review.**
  Crop names, symptoms, causes, and prevention were translated using standard
  agricultural vocabulary, but **treatment instructions are safety-relevant**
  and should be reviewed by a native speaker with agricultural expertise
  before this app is used by real farmers making real treatment decisions.
  See `scripts/add_translations.py` for the full translated content.
- No performance metrics are reported anywhere in this repo, because none have been
  measured yet — once the CV baseline or LoRA model is trained and evaluated, real
  accuracy/F1/confusion-matrix numbers belong here, not fabricated ones.

## License

MIT — see `LICENSE`.
