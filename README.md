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

- **Frontend → Vercel**: set the build command to `npm run build`, output directory
  `dist`, and set `VITE_API_URL` in Vercel's environment variables to your deployed
  backend URL. Never hard-code it.
- **Backend → a separate host**: the FastAPI service is CPU-only and lightweight by
  design — it does not run the model itself in `remote` mode, it forwards requests to
  a GPU-hosted inference service. See `backend/Dockerfile` (build from the repo root:
  `docker build -f backend/Dockerfile -t agri-llava-backend .`).
- **Model inference (GPU)**: not yet built. This is the next major piece — see
  "Current Status" above.

## Known Limitations

- Model inference is currently mocked; predictions are not real until a trained
  Qwen2.5-VL + LoRA adapter is deployed and `INFERENCE_MODE=remote` is configured.
- No CV baseline (EfficientNet/ResNet) model yet — scaffolded in `ml/` but not built.
- Knowledge base currently covers 10 crop/disease combinations; expand
  `knowledge/crop_diseases.json` for broader coverage.
- No performance metrics are reported anywhere in this repo, because none have been
  measured yet — once the CV baseline or LoRA model is trained and evaluated, real
  accuracy/F1/confusion-matrix numbers belong here, not fabricated ones.

## License

MIT — see `LICENSE`.
