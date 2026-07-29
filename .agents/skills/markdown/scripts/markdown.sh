#!/usr/bin/env bash
# markdown.sh — Convert documents to and from Markdown
#
# Usage:
#   markdown.sh to-md   <file> [options]     Convert to Markdown
#   markdown.sh to-pdf  <file> [-o output]   Convert Markdown to PDF
#   markdown.sh to-html <file> [-o output]   Convert Markdown to single-file HTML
#   markdown.sh --help
#
# to-md options:
#   -o, --output <file>          Output file path
#   --docling, --ocr             Use docling engine (best quality, supports images + OCR)
#   --pypdf                      Use pypdf engine (fast, text-only PDFs)
#   --poppler                    Use poppler/pdftotext engine
#   --ghostscript, --gs          Use ghostscript engine
#   --insert-page-number         Insert <!-- page N --> comments (default: on)
#   --no-insert-page-number      Suppress page comments
#   --insert-ocr-page-number     Insert <!-- ocr N --> comments (default: on)
#   --no-ocr-page-number         Suppress OCR comments
set -euo pipefail

# ── Helpers ──────────────────────────────────────────────────────────────────

die()  { printf 'error: %s\n' "$*" >&2; exit 1; }

# Strip trailing whitespace from every line (keeps newlines intact)
cleanup_md() {
    sed -i 's/[[:space:]]*$//' "$1"
}

usage() { cat <<EOF
Usage:
  markdown.sh to-md   <file> [options]     Convert to Markdown
  markdown.sh to-pdf  <file> [-o output]   Convert Markdown to PDF
  markdown.sh to-html <file> [-o output]   Convert Markdown to single-file HTML

to-md options:
  -o, --output <file>          Output file path (default: auto-derived from input)
  --docling, --ocr             Use docling engine (best quality, OCR, images)
  --pypdf                      Use pypdf engine (fast, text-layer only)
  --poppler                    Use poppler/pdftotext engine
  --ghostscript, --gs          Use ghostscript engine
  --insert-page-number         Insert <!-- page N --> comments (default: on)
  --no-insert-page-number      Suppress page comments
  --insert-ocr-page-number     Insert <!-- ocr N --> comments (default: on)
  --no-ocr-page-number         Suppress OCR comments
  --help                       Show this help message

Supported input formats for to-md:
  PDF (.pdf), Word (.docx), PowerPoint (.pptx),
  OpenDocument (.odt), Excel (.xlsx)
  Images (.png, .jpg, .jpeg, .bmp, .webp, .tiff) — requires --docling

PDF extraction fallback chain (when no engine flag given):
  docling → pypdf → poppler → ghostscript

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

# Check if a tool is available, skip message if not
check_tool() {
    local tool="$1" label="$2"
    if command -v "$tool" &>/dev/null; then
        return 0
    fi
    printf '  Skipping %s (%s not found)\n' "$label" "$tool" >&2
    return 1
}

# ── PDF Extraction Engines ──────────────────────────────────────────────────
# Each: extract_<engine> <input> <output> <insert_page> <insert_ocr> [<is_image>]
# Returns 0 on success, 1 on failure/skip.

extract_docling() {
    local input="$1" output="$2" insert_page="$3" insert_ocr="$4"
    local is_image="${5:-0}"

    if ! command -v uvx &>/dev/null; then
        printf '  Skipping docling (uvx not found)\n' >&2
        return 1
    fi

    printf '  Trying docling...\n' >&2

    # docling convert outputs to a directory, creating <basename>.md
    local _dl_tmpdir
    _dl_tmpdir="$(mktemp -d)"

    local base
    base="$(basename "$input")"
    local name="${base%.*}"

    # Run docling: convert to md first
    if ! uvx --from docling docling convert --to md --output "$_dl_tmpdir" --quiet "$input" &>/dev/null; then
        printf '  Skipping docling (conversion failed)\n' >&2
        rm -rf "$_dl_tmpdir"
        return 1
    fi

    local tmp_md="$_dl_tmpdir/${name}.md"
    if [[ ! -s "$tmp_md" ]]; then
        printf '  Skipping docling (empty output)\n' >&2
        rm -rf "$_dl_tmpdir"
        return 1
    fi

    # Also convert to json for page/OCR detection
    local tmp_json="$_dl_tmpdir/${name}.json"
    uvx --from docling docling convert --to json --output "$_dl_tmpdir" --quiet "$input" &>/dev/null

    if [[ "$is_image" == "1" ]]; then
        # Image input: single page, always OCR'd
        {
            [[ "$insert_page" == "1" ]] && printf '<!-- page 1 -->\n'
            [[ "$insert_ocr" == "1" ]] && printf '<!-- ocr 1 -->\n'
            cat "$tmp_md"
        } > "$output"
        printf '  → docling (image, 1 page, OCR)\n' >&2
        rm -rf "$_dl_tmpdir"
        return 0
    fi

    # PDF: try to get JSON for page/OCR detection
    if [[ -s "$tmp_json" ]]; then
        # Use Python to parse docling JSON and reconstruct markdown with page markers
        uvx --from docling python3 -c "
import json, sys

with open('$tmp_json', 'r') as f:
    data = json.load(f)

with open('$tmp_md', 'r') as f:
    md_lines = f.readlines()

insert_page = $insert_page
insert_ocr = $insert_ocr

# Get page count from pages dict
pages_info = data.get('pages', {})
total_pages = len(pages_info) if isinstance(pages_info, dict) else 0

# Collect text by page number from prov field
pages = {}       # page_num -> list of text
ocr_pages = set()

# Text elements
texts = data.get('texts', [])
for t in texts:
    prov = t.get('prov', [])
    text = t.get('text', '')
    for p in prov:
        pg = p.get('page_no')
        if pg and text:
            pages.setdefault(pg, []).append(text)

# Pictures indicate OCR'd pages
pics = data.get('pictures', [])
if isinstance(pics, list):
    for pic in pics:
        prov = pic.get('prov', [])
        for p in prov:
            pg = p.get('page_no')
            if pg:
                ocr_pages.add(pg)

# Output with markers
if pages:
    for pg in sorted(pages.keys()):
        if insert_page:
            print(f'<!-- page {pg} -->')
        if pg in ocr_pages and insert_ocr:
            print(f'<!-- ocr {pg} -->')
        for text in pages[pg]:
            print(text)
        print()  # blank line between pages
elif total_pages > 0:
    # Fallback: we know page count but couldn't parse text by page
    # Just output the raw markdown with a single page marker
    if insert_page:
        print('<!-- page 1 -->')
    print(''.join(md_lines), end='')
else:
    # No page info at all, just output raw markdown
    print(''.join(md_lines), end='')
" > "$output" 2>/dev/null

        if [[ -s "$output" ]]; then
            local page_count
            page_count="$(grep -c '^<!-- page' "$output" 2>/dev/null || echo "1")"
            local ocr_count
            ocr_count="$(grep -c '^<!-- ocr' "$output" 2>/dev/null || echo "0")"
            printf '  → docling (%s pages, %s OCR)\n' "$page_count" "$ocr_count" >&2
            rm -rf "$_dl_tmpdir"
            return 0
        fi
    fi

    # Fallback: just use raw markdown output
    cp "$tmp_md" "$output"
    printf '  → docling (raw output)\n' >&2
    rm -rf "$_dl_tmpdir"
    return 0
}

extract_pypdf() {
    local input="$1" output="$2" insert_page="$3" insert_ocr="$4"

    if ! command -v uvx &>/dev/null; then
        printf '  Skipping pypdf (uvx not found)\n' >&2
        return 1
    fi

    printf '  Trying pypdf...\n' >&2

    uvx --from pypdf python3 -c "
import sys
from pypdf import PdfReader

reader = PdfReader('$input')
pages = reader.pages
insert_page = $insert_page

for i, page in enumerate(pages, 1):
    if insert_page:
        print(f'<!-- page {i} -->')
    text = page.extract_text()
    if text:
        print(text)
    print()
" > "$output" 2>/dev/null

    if [[ -s "$output" ]]; then
        local page_count
        page_count="$(grep -c '^<!-- page' "$output" 2>/dev/null || echo "?")"
        printf '  → pypdf (%s pages)\n' "$page_count" >&2
        return 0
    fi

    printf '  Skipping pypdf (empty output)\n' >&2
    return 1
}

extract_poppler() {
    local input="$1" output="$2" insert_page="$3" insert_ocr="$4"

    check_tool pdftotext poppler || return 1
    check_tool pdfinfo pdfinfo || return 1

    printf '  Trying poppler (pdftotext -layout)...\n' >&2

    local pages
    pages="$(pdfinfo "$input" 2>/dev/null | grep '^Pages:' | awk '{print $2}')"
    [[ -n "$pages" ]] || { printf '  Skipping poppler (cannot determine page count)\n' >&2; return 1; }

    > "$output"
    local p
    for (( p=1; p<=pages; p++ )); do
        [[ "$insert_page" == "1" ]] && printf '<!-- page %d -->\n' "$p" >> "$output"
        pdftotext -layout -f "$p" -l "$p" "$input" - 2>/dev/null | tr -d '\f' >> "$output"
        printf '\n' >> "$output"
    done

    if [[ -s "$output" ]]; then
        printf '  → poppler (%s pages)\n' "$pages" >&2
        return 0
    fi

    printf '  Skipping poppler (empty output)\n' >&2
    return 1
}

extract_ghostscript() {
    local input="$1" output="$2" insert_page="$3" insert_ocr="$4"

    check_tool gs ghostscript || return 1

    printf '  Trying ghostscript...\n' >&2

    local pages
    if command -v pdfinfo &>/dev/null; then
        pages="$(pdfinfo "$input" 2>/dev/null | grep '^Pages:' | awk '{print $2}')"
    fi
    if [[ -z "$pages" || "$pages" -eq 0 ]] 2>/dev/null; then
        pages="$(gs -dBATCH -dNOPAUSE -sDEVICE=txtwrite -sOutputFile=/dev/null "$input" 2>&1 | grep -oP 'processing page \\K\\d+' | tail -1 || echo "0")"
    fi
    [[ "$pages" -gt 0 ]] 2>/dev/null || { printf '  Skipping ghostscript (cannot determine page count)\n' >&2; return 1; }

    # Ghostscript txtwrite needs a real file (not stdout) and must NOT use -dNODISPLAY
    local _gs_tmp
    _gs_tmp="$(mktemp --suffix=.txt)"

    > "$output"
    local p
    for (( p=1; p<=pages; p++ )); do
        [[ "$insert_page" == "1" ]] && printf '<!-- page %d -->\n' "$p" >> "$output"
        gs -sDEVICE=txtwrite -dFirstPage="$p" -dLastPage="$p" \
            -dSAFER -dBATCH -dNOPAUSE -sOutputFile="$_gs_tmp" "$input" >/dev/null 2>&1
        if [[ -s "$_gs_tmp" ]]; then
            tr -d '\f' < "$_gs_tmp" >> "$output"
        fi
        printf '\n' >> "$output"
    done
    rm -f "$_gs_tmp"

    # Check if we got any actual text content (beyond just page markers)
    local content_lines
    content_lines="$(grep -v '^<!-- page' "$output" | grep -v '^$' | wc -l)"
    if [[ "$content_lines" -gt 0 ]]; then
        printf '  → ghostscript (%s pages)\n' "$pages" >&2
        return 0
    fi

    printf '  Skipping ghostscript (empty text output)\n' >&2
    return 1
}

# ── Commands ─────────────────────────────────────────────────────────────────

cmd_to_md() {
    local input="" output=""
    local engine=""          # "" = auto fallback, or: docling|pypdf|poppler|ghostscript
    local insert_page=1      # default ON
    local insert_ocr=1       # default ON
    local engine_count=0

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -o|--output)                  output="$2"; shift 2 ;;
            --docling|--ocr)              engine="docling"; engine_count=$((engine_count+1)); shift ;;
            --pypdf)                      engine="pypdf"; engine_count=$((engine_count+1)); shift ;;
            --poppler)                    engine="poppler"; engine_count=$((engine_count+1)); shift ;;
            --ghostscript|--gs)           engine="ghostscript"; engine_count=$((engine_count+1)); shift ;;
            --insert-page-number)         insert_page=1; shift ;;
            --no-insert-page-number)      insert_page=0; shift ;;
            --insert-ocr-page-number)     insert_ocr=1; shift ;;
            --no-ocr-page-number)         insert_ocr=0; shift ;;
            -*)                           die "unknown option: $1" ;;
            *)                            [[ -n "$input" ]] && die "unexpected argument: $1"; input="$1"; shift ;;
        esac
    done

    [[ -n "$input" ]] || die "missing input file"
    [[ -f "$input" ]] || die "file not found: $input"
    [[ "$engine_count" -le 1 ]] || die "engine flags are mutually exclusive (use only one: --docling, --pypdf, --poppler, --gs)"

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
        pdf)
            if [[ -n "$engine" ]]; then
                extract_$engine "$input" "$output" "$insert_page" "$insert_ocr" || die "$engine extraction failed"
            else
                local extracted=0
                for try_engine in docling pypdf poppler ghostscript; do
                    if extract_$try_engine "$input" "$output" "$insert_page" "$insert_ocr"; then
                        extracted=1
                        break
                    fi
                done
                [[ "$extracted" -eq 1 ]] || die "no PDF engine available (tried: docling, pypdf, poppler, ghostscript)"
            fi
            ;;
        png|jpg|jpeg|bmp|webp|tiff)
            [[ "$engine" == "docling" || -z "$engine" ]] || die "image conversion requires --docling"
            if [[ "$engine" == "docling" ]]; then
                extract_docling "$input" "$output" "$insert_page" "$insert_ocr" 1 || die "docling image extraction failed"
            else
                if ! extract_docling "$input" "$output" "$insert_page" "$insert_ocr" 1; then
                    die "image conversion requires docling (not available or failed)"
                fi
            fi
            ;;
        docx|pptx|odt)
            pandoc -f "$ext" -t markdown "$input" -o "$output"
            ;;
        *)
            pandoc -t markdown "$input" -o "$output"
            ;;
    esac
    cleanup_md "$output"
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
