import argparse
from pathlib import Path
import requests


def main():
    parser = argparse.ArgumentParser(description="Validate a model run via API over a few sample images")
    parser.add_argument("--api", default="http://127.0.0.1:8000", help="API base URL")
    parser.add_argument("--samples", default="Captcha Solver/Datasets/samples", help="Path to samples directory")
    args = parser.parse_args()

    base = args.api.rstrip('/')

    # Health check
    r = requests.get(f"{base}/health", timeout=10)
    r.raise_for_status()
    print("Health:", r.json())

    samples_dir = Path(args.samples)
    if not samples_dir.exists():
        raise SystemExit(f"Samples dir not found: {samples_dir}")

    ok, total = 0, 0
    for img in list(samples_dir.glob("*.png"))[:10]:
        total += 1
        with img.open('rb') as f:
            files = {"file": (img.name, f, "image/png")}
            resp = requests.post(f"{base}/api/predict", files=files, timeout=30)
            if resp.ok:
                data = resp.json()
                pred = data.get("text", "")
                print(f"{img.name} -> {pred}")
                # crude exact match check with filename stem
                if pred and pred.lower() == img.stem.lower():
                    ok += 1
            else:
                print(f"{img.name} -> HTTP {resp.status_code}: {resp.text}")

    print(f"Exact matches: {ok}/{total}")


if __name__ == "__main__":
    main()



