#!/usr/bin/env bash
# markdown.sh — Convert documents to and from Markdown
#
# Usage:
#   markdown.sh to-md   <file> [-o output]     Convert to Markdown
#   markdown.sh to-pdf  <file> [-o output]     Convert Markdown to PDF
#   markdown.sh to-html <file> [-o output]     Convert Markdown to single-file HTML
#   markdown.sh --help
set -euo pipefail

# ── Helpers ──────────────────────────────────────────────────────────────────

die()  { printf 'error: %s\n' "$*" >&2; exit 1; }
usage() { cat <<EOF
Usage:
  markdown.sh to-md   <file> [-o output]     Convert to Markdown
  markdown.sh to-pdf  <file> [-o output]     Convert Markdown to PDF
  markdown.sh to-html <file> [-o output]     Convert Markdown to single-file HTML

Options:
  -o, --output <file>   Output file path (default: auto-derived from input)
  --help                Show this help message

Supported input formats for to-md:
  PDF (.pdf), Word (.docx), PowerPoint (.pptx),
  OpenDocument (.odt), Excel (.xlsx)

Excel files are evaluated with 'uvx formulas[all] calc' before conversion
to ensure formula results appear as computed values.
EOF
}

# Derive output path from input and target extension
derive_output() {
    local input="$1" ext="$2"
    local dir base
    dir="$(dirname "$input")"
    base="$(basename "$input")"
    printf '%s/%s.%s' "$dir" "${base%.*}" "$ext"
}

# ── Commands ─────────────────────────────────────────────────────────────────

cmd_to_md() {
    local input="" output=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -o|--output) output="$2"; shift 2 ;;
            -*) die "unknown option: $1" ;;
            *) [[ -n "$input" ]] && die "unexpected argument: $1"; input="$1"; shift ;;
        esac
    done
    [[ -n "$input" ]] || die "missing input file"
    [[ -f "$input" ]] || die "file not found: $input"

    [[ -n "$output" ]] || output="$(derive_output "$input" md)"

    local ext="${input##*.}"
    ext="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"

    case "$ext" in
        xlsx)
            local tmp
            tmp="$(mktemp --suffix=.xlsx)"
            trap 'rm -f "$tmp"' EXIT
            printf '  Evaluating formulas...\n' >&2
            uvx formulas[all] calc "$input" \
                --output-format excel \
                --output-file "$tmp"
            printf '  Converting to Markdown...\n' >&2
            pandoc -f xlsx -t markdown "$tmp" -o "$output"
            ;;
        pdf|docx|pptx|odt)
            pandoc -f "$ext" -t markdown "$input" -o "$output"
            ;;
        *)
            # Let pandoc auto-detect
            pandoc -t markdown "$input" -o "$output"
            ;;
    esac
    printf '  → %s\n' "$output" >&2
}

cmd_to_pdf() {
    local input="" output=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -o|--output) output="$2"; shift 2 ;;
            -*) die "unknown option: $1" ;;
            *) [[ -n "$input" ]] && die "unexpected argument: $1"; input="$1"; shift ;;
        esac
    done
    [[ -n "$input" ]] || die "missing input file"
    [[ -f "$input" ]] || die "file not found: $input"

    [[ -n "$output" ]] || output="$(derive_output "$input" pdf)"

    pandoc "$input" -o "$output"
    printf '  → %s\n' "$output" >&2
}

cmd_to_html() {
    local input="" output=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -o|--output) output="$2"; shift 2 ;;
            -*) die "unknown option: $1" ;;
            *) [[ -n "$input" ]] && die "unexpected argument: $1"; input="$1"; shift ;;
        esac
    done
    [[ -n "$input" ]] || die "missing input file"
    [[ -f "$input" ]] || die "file not found: $input"

    [[ -n "$output" ]] || output="$(derive_output "$input" html)"

    pandoc -t html --self-contained "$input" -o "$output"
    printf '  → %s\n' "$output" >&2
}

# ── Main ─────────────────────────────────────────────────────────────────────

[[ $# -gt 0 ]] || { usage; exit 0; }

case "$1" in
    --help|-h) usage; exit 0 ;;
    to-md)   shift; cmd_to_md "$@" ;;
    to-pdf)  shift; cmd_to_pdf "$@" ;;
    to-html) shift; cmd_to_html "$@" ;;
    *)       die "unknown command: $1 — use 'markdown.sh --help'" ;;
esac
