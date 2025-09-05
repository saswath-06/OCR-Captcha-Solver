import time
import logging
import traceback
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from mltu.configs import BaseModelConfigs

try:
    # When running from repo root: uvicorn api.main:app
    from api.config import resolve_model_run_path
except Exception:
    # When running from inside api folder: uvicorn main:app
    from config import resolve_model_run_path

# Import inference model from existing codebase
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "captcha-solver"))
from interferenceModel import ImageToWordModel  # noqa: E402


app = FastAPI(title="OCR Captcha Solver API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ocr-captcha-solver.vercel.app","http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    logging.basicConfig(level=logging.INFO)
    run_path = resolve_model_run_path()
    cfg_path = str(run_path / "configs.yaml")
    try:
        configs = BaseModelConfigs.load(cfg_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load configs.yaml at {cfg_path}: {e}")
    model = ImageToWordModel(model_path=str(run_path), char_list=configs.vocab)
    app.state.model = model
    app.state.run_path = str(run_path)
    app.state.ready = True


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": bool(getattr(app.state, "ready", False)),
        "model_run_path": getattr(app.state, "run_path", None),
    }


@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    try:
        if file.content_type not in ("image/png", "image/jpeg"):
            raise HTTPException(status_code=415, detail="Unsupported media type")
        raw = await file.read()
        image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        if not getattr(app.state, "ready", False):
            raise HTTPException(status_code=503, detail="Model not ready")
        t0 = time.time()
        text = app.state.model.predict(image)
        dt = int((time.time() - t0) * 1000)
        return JSONResponse({"text": text, "timing_ms": dt})
    except HTTPException:
        raise
    except Exception as e:
        logging.error("Inference error: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=False)


