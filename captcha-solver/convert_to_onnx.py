import argparse
from pathlib import Path

import tensorflow as tf
import tf2onnx


def find_latest_h5(results_dir: Path) -> Path:
    candidates = []
    for run in results_dir.iterdir():
        if not run.is_dir():
            continue
        h5 = run / "model.h5"
        if h5.exists():
            candidates.append(h5)
    if not candidates:
        raise FileNotFoundError(f"No model.h5 found under {results_dir}")
    candidates.sort(key=lambda p: p.parent.name, reverse=True)
    return candidates[0]


def convert(h5_path: Path, onnx_path: Path):
    print(f"Loading Keras model: {h5_path}")
    model = tf.keras.models.load_model(str(h5_path), compile=False)
    print("Converting to ONNX...")
    spec = (tf.TensorSpec(model.inputs[0].shape, tf.float32, name="input"),)
    model_proto, _ = tf2onnx.convert.from_keras(model, input_signature=spec, opset=13)
    onnx_path.parent.mkdir(parents=True, exist_ok=True)
    with open(onnx_path, "wb") as f:
        f.write(model_proto.SerializeToString())
    print(f"Saved ONNX: {onnx_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert model.h5 to model.onnx")
    parser.add_argument("--run", type=str, default="", help="Path to Results/<run> directory containing model.h5")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    results_dir = root / "Captcha Solver" / "Results"

    if args.run:
        run_path = Path(args.run)
        if not run_path.is_absolute():
            run_path = root / args.run
        h5_path = run_path / "model.h5"
        if not h5_path.exists():
            raise FileNotFoundError(f"{h5_path} not found")
    else:
        h5_path = find_latest_h5(results_dir)
        run_path = h5_path.parent

    onnx_path = run_path / "model.onnx"
    convert(h5_path, onnx_path)


if __name__ == "__main__":
    main()


