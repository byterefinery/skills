#!/usr/bin/env bash
# formulas — Excel formula evaluation, workbook calculation, and export.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "${SCRIPT_DIR}/_formulas-1-3-4.py" "$@"
