#!/usr/bin/env python3
"""timesfm-200m-transformers — Forecast time series with Google's TimesFM-2.5 200M transformer

Requires: torch, transformers

Usage:
    timesfm-200m-transformers.sh predict <input_file> [--horizon HORIZON] [--context-len LEN] [--device DEVICE] [--output OUTPUT]
    timesfm-200m-transformers.sh demo
    timesfm-200m-transformers.sh --help
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch


def check_deps():
    """Check that required packages are installed."""
    missing = []
    try:
        import torch  # noqa: F401
    except ImportError:
        missing.append("torch")
    try:
        import transformers  # noqa: F401
    except ImportError:
        missing.append("transformers")
    if missing:
        print(f"Error: missing required packages: {', '.join(missing)}", file=sys.stderr)
        print(f"Install with: pip install {' '.join(missing)}", file=sys.stderr)
        sys.exit(1)


def load_model(device="cpu"):
    """Load the TimesFM-2.5 model."""
    from transformers import TimesFm2_5ModelForPrediction

    print(f"Loading model on {device}...", file=sys.stderr)
    model = TimesFm2_5ModelForPrediction.from_pretrained(
        "google/timesfm-2.5-200m-transformers",
    ).to(device)
    model = model.to(torch.float32).eval()
    print("Model loaded.", file=sys.stderr)
    return model


def normalize_series(series: torch.Tensor) -> tuple:
    """Z-score normalize a series."""
    mean = series.mean()
    std = series.std()
    if std < 1e-8:
        std = 1.0
    return (series - mean) / std, mean, std


def denormalize(pred: torch.Tensor, mean: torch.Tensor, std: torch.Tensor) -> torch.Tensor:
    """Reverse z-score normalization."""
    return pred * std + mean


def read_csv_series(path: Path) -> dict:
    """Read a CSV file with columns: value (required), id (optional).

    Returns dict mapping id -> numpy array of values.
    If no 'id' column, returns {'default': array}.
    """
    import csv

    series = {}
    current_id = "default"

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []

        if "value" not in fields:
            print(f"Error: CSV must have a 'value' column. Found: {fields}", file=sys.stderr)
            sys.exit(1)

        has_id = "id" in fields

        for row in reader:
            val = float(row["value"])
            if has_id:
                current_id = str(row["id"])

            series.setdefault(current_id, []).append(val)

    return {k: np.array(v, dtype=np.float32) for k, v in series.items()}


def cmd_predict(args):
    """Run prediction on input data."""
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(device=device)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    series_data = read_csv_series(input_path)

    results = {}
    for series_id, values in series_data.items():
        tensor = torch.tensor(values, dtype=torch.float32)
        normalized, mean, std = normalize_series(tensor)

        with torch.no_grad():
            outputs = model(
                past_values=[normalized.to(device)],
                forecast_context_len=args.context_len,
                forecast_horizon=args.horizon,
            )

        # Denormalize
        mean_pred = denormalize(
            outputs.mean_predictions[0].cpu(), mean, std
        ).tolist()
        full_pred = denormalize(
            outputs.full_predictions[0].cpu(), mean, std
        ).tolist()

        results[series_id] = {
            "context_length": len(values),
            "horizon": args.horizon,
            "mean_forecast": mean_pred,
            "quantile_forecast": full_pred,
        }

    output_path = Path(args.output) if args.output else Path("forecast.json")
    output_path.write_text(json.dumps(results, indent=2))
    print(f"Wrote forecast to {output_path}")


def cmd_demo(args):
    """Run a quick demo with synthetic data."""
    check_deps()
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(device=device)

    # Generate synthetic series
    t = torch.linspace(0, 4 * np.pi, 100)
    series = torch.sin(t) + 0.1 * torch.randn(100)

    print(f"\nInput: synthetic sine wave + noise, length={len(series)}", file=sys.stderr)
    print(f"Horizon: {args.horizon} steps", file=sys.stderr)

    normalized, mean, std = normalize_series(series)

    with torch.no_grad():
        outputs = model(
            past_values=[normalized.to(device)],
            forecast_context_len=args.context_len,
            forecast_horizon=args.horizon,
        )

    mean_pred = denormalize(outputs.mean_predictions[0].cpu(), mean, std)
    q10 = denormalize(outputs.full_predictions[0, :, 1].cpu(), mean, std)
    q90 = denormalize(outputs.full_predictions[0, :, 9].cpu(), mean, std)

    print(f"\nMean forecast (first 5 steps): {mean_pred[:5].tolist()}")
    print(f"80% CI lower (first 5):        {q10[:5].tolist()}")
    print(f"80% CI upper (first 5):        {q90[:5].tolist()}")

    if args.output:
        result = {
            "mean_forecast": mean_pred.tolist(),
            "quantile_10": q10.tolist(),
            "quantile_90": q90.tolist(),
        }
        Path(args.output).write_text(json.dumps(result, indent=2))
        print(f"Wrote to {args.output}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        prog="timesfm-200m-transformers",
        description="Forecast time series with Google's TimesFM-2.5 200M transformer",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # predict
    predict_parser = subparsers.add_parser("predict", help="Forecast from CSV input")
    predict_parser.add_argument("input", help="Input CSV file (columns: value, id optional)")
    predict_parser.add_argument("--horizon", type=int, default=24, help="Forecast horizon (default: 24)")
    predict_parser.add_argument("--context-len", type=int, default=1024, help="Context length (default: 1024)")
    predict_parser.add_argument("--device", default=None, help="Device: cpu or cuda (default: auto)")
    predict_parser.add_argument("--output", default=None, help="Output JSON file (default: forecast.json)")

    # demo
    demo_parser = subparsers.add_parser("demo", help="Quick demo with synthetic data")
    demo_parser.add_argument("--horizon", type=int, default=24, help="Forecast horizon (default: 24)")
    demo_parser.add_argument("--context-len", type=int, default=1024, help="Context length (default: 1024)")
    demo_parser.add_argument("--device", default=None, help="Device: cpu or cuda (default: auto)")
    demo_parser.add_argument("--output", default=None, help="Output JSON file")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    check_deps()

    if args.command == "predict":
        cmd_predict(args)
    elif args.command == "demo":
        cmd_demo(args)


if __name__ == "__main__":
    main()
