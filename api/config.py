import os
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "captcha-solver" / "Results"


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    return value if value is not None else default


def find_latest_run_with_model() -> Optional[Path]:
    if not RESULTS_DIR.exists():
        return None
    candidates = []
    for child in RESULTS_DIR.iterdir():
        if not child.is_dir():
            continue
        onnx = child / "model.onnx"
        if onnx.exists():
            candidates.append(child)
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.name, reverse=True)
    return candidates[0]


def resolve_model_run_path() -> Path:
    env_path = get_env("MODEL_RUN_PATH")
    if env_path:
        path = Path(env_path)
        if path.is_dir():
            return path
        # Allow relative to ROOT
        alt = ROOT / env_path
        if alt.is_dir():
            return alt
    latest = find_latest_run_with_model()
    if latest:
        return latest
    # Fallback to latest directory even without onnx (will error later)
    if RESULTS_DIR.exists():
        dirs = [d for d in RESULTS_DIR.iterdir() if d.is_dir()]
        if dirs:
            dirs.sort(key=lambda p: p.name, reverse=True)
            return dirs[0]
    raise FileNotFoundError("No model run directory found. Ensure you have a Results/<run>/ with model.onnx")



