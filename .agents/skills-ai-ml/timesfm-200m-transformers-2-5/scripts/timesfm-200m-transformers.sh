#!/usr/bin/env bash
# timesfm-200m-transformers — Forecast time series with Google's TimesFM-2.5 200M transformer model via HuggingFace transformers
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -B "$SCRIPT_DIR/_timesfm-200m-transformers.py" "$@"
