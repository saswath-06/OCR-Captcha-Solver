## API (FastAPI) — Run & Test

Python 3.9 with TensorFlow 2.10 environment recommended.

1. Install deps (prefer venv):
```
cd api
pip install -r requirements.txt
```

2. Ensure you have a model run with ONNX and configs.yaml, e.g. `Captcha Solver/Results/<run>/model.onnx` and `configs.yaml`.
   - To choose a run: set env `MODEL_RUN_PATH` to the run directory path.

3. Start API:
```
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

4. Health check:
```
curl http://localhost:8000/health
```

5. Prediction test (PNG/JPG):
```
curl -F "file=@Captcha\ Solver/Datasets/samples/7dgc2.png" http://localhost:8000/api/predict
```

If running the Next.js app, it will call `http://localhost:8000/api/predict` by default. Configure CORS or change `NEXT_PUBLIC_API_BASE` if needed.



