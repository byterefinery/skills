#!/usr/bin/env bash
# example.sh — demo script for the `example` skill.
# Echoes a fixed line; extra CLI parameters are accepted but ignored.
set -euo pipefail

case "${1:-}" in
  -h|--help)
    echo "Usage: example.sh [text...]"
    echo "Echoes a fixed example line. Parameters are accepted but ignored."
    exit 0
    ;;
esac

echo "This is example.sh output."
