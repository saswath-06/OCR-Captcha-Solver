## OCR Captcha Solver — Web Frontend + Inference API Specification

### 1) Goal
- **Add a minimal, user-friendly web UI** where a user uploads a CAPTCHA image and receives the decoded text.
- **Serve the trained model via a lightweight HTTP API** that performs inference using the existing ONNX runtime flow.

### 2) Non-goals
- Training UI or dataset management.
- Multi-tenant auth, advanced user roles.
- CAPTCHA solving at scale (batch jobs, queues). Initial scope is single-image, low QPS.

### 3) Current state recap (from codebase)
- Model training is orchestrated via `Captcha Solver/training.py` using TensorFlow/Keras with CTCLoss and exports ONNX via `Model2onnx` callback.
- Inference helper exists in `Captcha Solver/interferenceModel.py` as `ImageToWordModel`, which subclasses `mltu.inferenceModel.OnnxInferenceModel` and decodes outputs to text via `ctc_decoder`.
- Configs (`Captcha Solver/configs.py`) define image size (200×50), batch size, learning rate, vocab, and a timestamped `model_path` under `Captcha Solver/Results/YYYYMMDDHHMM`.

### 4) Target architecture
- **Frontend (static, single page)**
  - File input (PNG/JPG) + submit button.
  - Shows preview and decoded text.
  - Basic validation and error display.

- **Backend API (Python, FastAPI recommended)**
  - Loads latest/selected ONNX model into memory on startup using `ImageToWordModel`.
  - POST `/api/predict` accepts an image (multipart/form-data), returns JSON: `{ text: string, timing_ms: number }`.
  - Health endpoint GET `/health` returns app and model readiness.

- **Model artifact**
  - Use ONNX exported by training (`Model2onnx`). Expected location: `Captcha Solver/Results/<run>/model.onnx` and `configs.yaml` for vocab/size.
  - If multiple runs exist, allow configuring which run to use via env var or startup CLI arg.

### 5) Detailed requirements

#### 5.1 Frontend
- **UI elements**
  - File uploader (accept: `.png,.jpg,.jpeg`), drag-and-drop optional.
  - Button: “Solve CAPTCHA”.
  - Image preview area.
  - Result area to show decoded text and latency.
  - Error banner for API or validation errors.

- **Client-side validation**
  - Enforce max size (default 2 MB) and allowed mime types.
  - Disable button while uploading/inferencing.

- **Accessibility**
  - Labels for inputs, keyboard navigable, sufficient contrast.

- **Tech choice**
  - Keep simple: vanilla HTML/CSS + minimal JS, or React if preferred. Static assets can be served by the backend for simplicity.

#### 5.2 Backend API
- **Framework**: FastAPI (uvicorn), or Flask as alternative. FastAPI is preferred for pydantic validation and automatic OpenAPI docs.
- **Endpoints**
  - `GET /health` → `{ status: "ok", model_loaded: boolean, model_run_path: string }`
  - `POST /api/predict` (multipart/form-data)
    - form field `file`: image
    - returns 200 JSON `{ text: string, timing_ms: number }`
    - errors: 400 invalid input; 415 unsupported media type; 500 inference failures.

- **Model loading**
  - On app startup, locate `model.onnx` and `configs.yaml` under a chosen run directory (env: `MODEL_RUN_PATH`, default to latest directory under `Captcha Solver/Results`).
  - Load `configs.yaml` using `mltu.configs.BaseModelConfigs.load(path)` to get `vocab`, `width`, `height`.
  - Initialize `ImageToWordModel(model_path=<run path>, char_list=configs.vocab)`.

- **Inference flow**
  1. Receive image bytes (PNG/JPG).
  2. Decode to `numpy` image via OpenCV.
  3. Resize to `configs.width×configs.height` (the `ImageToWordModel` already resizes, but ensure consistent color mode BGR->RGB if needed).
  4. Call `model.predict(image)` → text string.
  5. Return JSON with text and elapsed time.

- **Validation and limits**
  - Max payload size: 2–5 MB (configurable via env `MAX_UPLOAD_MB`).
  - Allowed content types: `image/png`, `image/jpeg`.
  - Optional: Basic rate limiting (e.g., 30 req/min/IP) if deploying publicly.

- **Logging & observability**
  - Structured logs for request id, latency, image size.
  - Prometheus-ready metrics (optional): request count, errors, p95 latency.

#### 5.3 Configuration
- Environment variables:
  - `MODEL_RUN_PATH` (e.g., `Captcha Solver/Results/202509041848`)
  - `PORT` (default 8000)
  - `MAX_UPLOAD_MB` (default 2)
  - `ALLOWED_ORIGINS` for CORS, if frontend hosted on different origin.

#### 5.4 Security
- Validate and constrain uploads (size/type).
- Strip EXIF and metadata; no saving uploads by default.
- Disable directory listing. Do not log full image contents.
- CORS restricted to known frontend origins in production.

### 6) Project changes (files to add)

- `web/`
  - `index.html` — simple upload UI.
  - `styles.css` — basic styling.
  - `app.js` — handles file selection, calls API, renders result.

- `api/`
  - `main.py` — FastAPI app, model bootstrap, endpoints.
  - `requirements.txt` — API dependencies: `fastapi`, `uvicorn[standard]`, `opencv-python`, `onnxruntime`, `pydantic`, plus existing `mltu` dependency.
  - `config.py` — env parsing and model path discovery helper.

- Optional deployment assets
  - `Dockerfile`
  - `docker-compose.yml`

### 7) Example API contracts

- `GET /health` 200
```json
{ "status": "ok", "model_loaded": true, "model_run_path": "Captcha Solver/Results/202509041848" }
```

- `POST /api/predict` 200
Request: multipart/form-data with field `file`.
Response:
```json
{ "text": "7dgc2", "timing_ms": 34 }
```

- Error (unsupported type) 415
```json
{ "error": "Unsupported media type" }
```

### 8) Frontend behavior (vanilla JS outline)
- On file select, show preview.
- On submit, build `FormData` with `file` and `fetch('/api/predict')`.
- Show spinner while awaiting; then render `text` and `timing_ms`.
- Handle errors: show message, allow retry without reload.

### 9) Performance considerations
- Model loads once at startup; keep a singleton instance.
- Convert images to the exact input size to avoid repeated allocations.
- Enforce upload size; reject huge files.
- If necessary later: queue requests, process sequentially when running on CPU.

### 10) Testing
- Unit tests
  - `api/tests/test_health.py` — health returns 200.
  - `api/tests/test_predict.py` — valid image returns 200 and non-empty text.
  - Edge cases: bad mime type, oversized file, corrupted image bytes.

- Manual QA
  - Try PNG/JPG with known labels from `Captcha Solver/Datasets/samples`.
  - Non-image upload → error.

### 11) Local development workflow
1. Ensure an ONNX model exists under `Captcha Solver/Results/<run>/model.onnx` with `configs.yaml`.
2. `cd api && pip install -r requirements.txt` (use a separate venv from `myenv` if desired).
3. `uvicorn main:app --reload --port 8000`.
4. Serve `web/` statically via FastAPI or run a simple static server. If served by FastAPI, mount at `/`.
5. Open `http://localhost:8000` and test with images.

### 12) Deployment
- **Option A: Single container** serving both API and static assets (recommended for simplicity).
  - `Dockerfile` installs runtime (no training deps), copies `api/` and `web/`, starts `uvicorn`.
  - Provide model via bind mount or baked into image (prefer mount for updates).

- **Option B: Separate static hosting and API**
  - Host `web/` on CDN or object storage with a public URL.
  - Host API on a VM/container with CORS enabled for the web origin.

### 13) Minimal FastAPI sketch (reference only)
```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import cv2, numpy as np, time, os
from mltu.configs import BaseModelConfigs
from pathlib import Path
from interferenceModel import ImageToWordModel

app = FastAPI()

MODEL_RUN_PATH = os.getenv("MODEL_RUN_PATH", "Captcha Solver/Results/202509041848")

@app.on_event("startup")
def load_model():
    run_path = Path(MODEL_RUN_PATH)
    cfg = BaseModelConfigs.load(str(run_path / "configs.yaml"))
    app.state.model = ImageToWordModel(model_path=str(run_path), char_list=cfg.vocab)
    app.state.ready = True

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": bool(getattr(app.state, "ready", False)), "model_run_path": MODEL_RUN_PATH}

@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    if file.content_type not in ("image/png", "image/jpeg"):
        raise HTTPException(415, "Unsupported media type")
    raw = await file.read()
    image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(400, "Invalid image")
    t0 = time.time()
    text = app.state.model.predict(image)
    dt = int((time.time() - t0) * 1000)
    return JSONResponse({"text": text, "timing_ms": dt})
```

### 14) Risks & mitigations
- Missing ONNX file: document how to export (ensure `Model2onnx` ran; otherwise convert manually).
- Environment mismatch (CPU/GPU): use `onnxruntime` (CPU) by default for portability.
- CORS issues: configure `ALLOWED_ORIGINS` properly.

### 15) Acceptance criteria
- User can open the web page, upload a CAPTCHA, and see decoded text within ~1 second on CPU for small images.
- Health endpoint reports ready state and correct run path.
- API validates inputs and returns helpful errors.


