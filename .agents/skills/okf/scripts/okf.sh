#!/usr/bin/env bash
# okf.sh — Open Knowledge Format (OKF v0.2) bundle tooling
# Delegates to _okf.py for deterministic operations.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "${SCRIPT_DIR}/_okf.py" "$@"
