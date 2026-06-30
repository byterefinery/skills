#!/usr/bin/env bash
# infographic.sh — thin wrapper around _infographic.js (requires bun)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec bun "${SCRIPT_DIR}/_infographic.js" "$@"
