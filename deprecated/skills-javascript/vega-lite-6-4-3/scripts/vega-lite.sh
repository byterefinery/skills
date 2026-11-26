#!/usr/bin/env bash
# vega-lite.sh — thin wrapper around _vega-lite.js (requires bun)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec bun "${SCRIPT_DIR}/_vega-lite.js" "$@"
