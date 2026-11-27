#!/usr/bin/env bash
# mermaid.sh — thin wrapper around _mermaid.js (requires bun)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec bun "${SCRIPT_DIR}/_mermaid.js" "$@"
