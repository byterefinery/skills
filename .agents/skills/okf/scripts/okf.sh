#!/usr/bin/env bash
# okf.sh — Open Knowledge Format (OKF) bundle management
# Delegates to _okf.py for parsing, validation, and document I/O.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "${SCRIPT_DIR}/_okf.py" "$@"
