#!/usr/bin/env bash
# markdown.sh — Convert documents to and from Markdown
#
# Usage:
#   markdown.sh -i INPUT [-o OUTPUT] [options]   Convert document to/from Markdown
#   markdown.sh --help
#
# Format is auto-detected from input/output file extensions:
#   .pdf, .docx, .pptx, .odt, .xlsx, images → .md   (to Markdown)
#   .md → .pdf                                     (to PDF)
#   .md → .html                                    (to single-file HTML)
#
# Options:
#   -i, --input <file>           Input file (required)
#   -o, --output <file>          Output file path (default: auto-derived from input)
#   --layout                     Use docling standard pipeline with layout detection (Heron/ONNX)
#   --ocr                        Use docling standard pipeline with OCR (RapidOCR/ONNX)
#   --vlm                        Use docling VLM pipeline (Granite-Docling-258M)
#   --docling                    Use docling standard pipeline (default, fast, no OCR)
#   --pypdf                      Use pypdf engine (fast, text-layer only PDFs)
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
  markdown.sh -i <input> [-o <output>] [options]

Options:
  -i, --input <file>           Input file (required)
  -o, --output <file>          Output file path (default: auto-derived from input)
  --layout                     Docling standard pipeline with layout detection (Heron/ONNX)
  --ocr                        Docling standard pipeline + OCR (RapidOCR/ONNX)
  --vlm                        Docling VLM pipeline (Granite-Docling-258M)
  --docling                    Docling standard pipeline (default, fast, no OCR)
  --pypdf                      Use pypdf engine (fast, text-layer only PDFs)
  --poppler                    Use poppler/pdftotext engine
  --ghostscript, --gs          Use ghostscript engine
  --insert-page-number         Insert <!-- page N --> comments (default: on)
  --no-insert-page-number      Suppress page comments
  --insert-ocr-page-number     Insert <!-- ocr N --> comments (default: on)
  --no-ocr-page-number         Suppress OCR comments
  --help                       Show this help message

Format detection (from file extensions):
  To Markdown:  .pdf .docx .pptx .odt .xlsx .png .jpg .jpeg .bmp .webp .tiff → .md
  To PDF:       .md → .pdf
  To HTML:      .md → .html

PDF extraction engines:
  docling (default)  — Standard pipeline, Heron layout detection (ONNX),
    extracts text/tables from PDF text layer, fast and lightweight
  docling-layout (--layout) — Same as default, explicitly enables layout detection
  docling-ocr (--ocr)  — Standard pipeline + RapidOCR (ONNX), handles scanned
    pages via OCR, moderate speed
  docling-vlm (--vlm)  — VLM pipeline with Granite-Docling-258M, full visual
    understanding, handles scanned pages, slower but best quality
  pypdf — fast, extracts text layer only (empty for scanned pages)
  poppler — fast, preserves layout with -layout flag (empty for scanned pages)
  ghostscript — extracts text layer via txtwrite device (empty for scanned pages)

PDF extraction fallback chain (when no engine flag given):
  docling → pypdf → poppler → ghostscript

Note: --ocr and --vlm are mutually exclusive. --layout is optional.

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

# Lowercase extension (no dot)
lower_ext() {
    printf '%s' "${1##*.}" | tr '[:upper:]' '[:lower:]'
}

# Wall-clock timer (seconds with decimals)
_timer_start() { date +%s%N; }
_timer_elapsed() {
    local start="$1" end
    end="$(date +%s%N)"
    local diff=$(( end - start ))
    printf '%s.%02d' "$(( diff / 1000000000 ))" "$(( (diff % 1000000000) / 10000000 ))"
}

# ── PDF Extraction Engines ──────────────────────────────────────────────────
# Each: extract_<engine> <input> <output> <insert_page> <insert_ocr> [<is_image>]
# Returns 0 on success, 1 on failure/skip.

extract_docling() {
    local input="$1" output="$2" insert_page="$3" insert_ocr="$4"
    local is_image="${5:-0}"
    local mode="${6:-standard}"   # standard | layout | ocr | vlm

    if ! command -v uvx &>/dev/null; then
        printf '  Skipping docling (uvx not found)\n' >&2
        return 1
    fi

    local _script
    _script="$(dirname "$0")/docling_extract.py"

    # Build mode flags
    local _mode_flags=()
    case "$mode" in
        ocr)  _mode_flags+=(--ocr) ;;
        vlm)  _mode_flags+=(--vlm) ;;
        standard|layout) ;; # default: standard pipeline, ONNX layout, no OCR
    esac

    # Run Python helper (uses ONNX Runtime for layout by default)
    # OCR mode needs rapidocr-onnxruntime as extra dep
    local _uv_cmd
    if [[ "$mode" == "ocr" ]]; then
        _uv_cmd="uv run --with docling --with onnxruntime --with rapidocr-onnxruntime python3"
    elif [[ "$mode" == "vlm" ]]; then
        _uv_cmd="uv run --with docling python3"
    else
        _uv_cmd="uv run --with docling --with onnxruntime python3"
    fi

    if ! $_uv_cmd "$_script" "$input" -o "$output" "${_mode_flags[@]}" 2>&1; then
        printf '  Skipping docling (conversion failed)\n' >&2
        return 1
    fi

    if [[ ! -s "$output" ]]; then
        printf '  Skipping docling (empty output)\n' >&2
        return 1
    fi

    printf '  → docling (%s)\n' "$mode" >&2
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

    local content_lines
    content_lines="$(grep -v '^<!-- page' "$output" | grep -v '^$' | wc -l)"
    if [[ "$content_lines" -gt 0 ]]; then
        printf '  → ghostscript (%s pages)\n' "$pages" >&2
        return 0
    fi

    printf '  Skipping ghostscript (empty text output)\n' >&2
    return 1
}

# ── Conversion functions ────────────────────────────────────────────────────

_cmd_to_md() {
    local input="$1" output="$2" engine="$3" insert_page="$4" insert_ocr="$5"

    local ext
    ext="$(lower_ext "$input")"

    case "$ext" in
        xlsx)
            local tmp
            tmp="$(mktemp --suffix=.xlsx)"
            trap 'rm -f "$tmp"' EXIT
            printf '  Evaluating formulas...\n' >&2
            local step_start step_elapsed
            step_start=$(_timer_start)
            uvx formulas[all] calc "$input" \
                --output-format excel \
                --output-file "$tmp"
            step_elapsed=$(_timer_elapsed "$step_start")
            printf '  Formula evaluation: %s s\n' "$step_elapsed" >&2

            printf '  Converting to Markdown...\n' >&2
            step_start=$(_timer_start)
            pandoc -f xlsx -t markdown "$tmp" -o "$output"
            step_elapsed=$(_timer_elapsed "$step_start")
            printf '  Pandoc conversion: %s s\n' "$step_elapsed" >&2
            ;;
        pdf)
            if [[ -n "$engine" ]]; then
                local step_start step_elapsed
                step_start=$(_timer_start)
                case "$engine" in
                    docling)       extract_docling "$input" "$output" "$insert_page" "$insert_ocr" 0 standard || die "docling extraction failed" ;;
                    docling-layout) extract_docling "$input" "$output" "$insert_page" "$insert_ocr" 0 layout || die "docling-layout extraction failed" ;;
                    docling-ocr)   extract_docling "$input" "$output" "$insert_page" "$insert_ocr" 0 ocr || die "docling-ocr extraction failed" ;;
                    docling-vlm)   extract_docling "$input" "$output" "$insert_page" "$insert_ocr" 0 vlm || die "docling-vlm extraction failed" ;;
                    *)             extract_$engine "$input" "$output" "$insert_page" "$insert_ocr" || die "$engine extraction failed" ;;
                esac
                step_elapsed=$(_timer_elapsed "$step_start")
                printf '  Extraction time: %s s\n' "$step_elapsed" >&2
            else
                local extracted=0
                for try_engine in docling pypdf poppler ghostscript; do
                    local step_start step_elapsed
                    step_start=$(_timer_start)
                    case "$try_engine" in
                        docling) extract_docling "$input" "$output" "$insert_page" "$insert_ocr" 0 standard ;;
                        *)       extract_$try_engine "$input" "$output" "$insert_page" "$insert_ocr" ;;
                    esac && {
                        extracted=1
                        step_elapsed=$(_timer_elapsed "$step_start")
                        printf '  Extraction time (%s): %s s\n' "$try_engine" "$step_elapsed" >&2
                        break
                    }
                done
                [[ "$extracted" -eq 1 ]] || die "no PDF engine available (tried: docling, pypdf, poppler, ghostscript)"
            fi
            ;;
        png|jpg|jpeg|bmp|webp|tiff)
            [[ "$engine" == "docling" || "$engine" == "docling-ocr" || "$engine" == "docling-vlm" || -z "$engine" ]] || die "image conversion requires --docling, --ocr, or --vlm"
            local step_start step_elapsed
            step_start=$(_timer_start)
            local _img_mode=standard
            case "$engine" in
                docling-ocr) _img_mode=ocr ;;
                docling-vlm) _img_mode=vlm ;;
                docling|"")  _img_mode=standard ;;
            esac
            if ! extract_docling "$input" "$output" "$insert_page" "$insert_ocr" 1 "$_img_mode"; then
                die "image conversion requires docling (not available or failed)"
            fi
            step_elapsed=$(_timer_elapsed "$step_start")
            printf '  Extraction time: %s s\n' "$step_elapsed" >&2
            ;;
        docx|pptx|odt)
            local step_start step_elapsed
            step_start=$(_timer_start)
            pandoc -f "$ext" -t markdown "$input" -o "$output"
            step_elapsed=$(_timer_elapsed "$step_start")
            printf '  Pandoc conversion: %s s\n' "$step_elapsed" >&2
            ;;
        *)
            local step_start step_elapsed
            step_start=$(_timer_start)
            pandoc -t markdown "$input" -o "$output"
            step_elapsed=$(_timer_elapsed "$step_start")
            printf '  Pandoc conversion: %s s\n' "$step_elapsed" >&2
            ;;
    esac
    cleanup_md "$output"
    printf '  → %s\n' "$output" >&2
}

_cmd_to_pdf() {
    local input="$1" output="$2"
    pandoc "$input" -o "$output"
    printf '  → %s\n' "$output" >&2
}

_cmd_to_html() {
    local input="$1" output="$2"
    pandoc -t html --self-contained "$input" -o "$output"
    printf '  → %s\n' "$output" >&2
}

# ── Main ─────────────────────────────────────────────────────────────────────

[[ $# -gt 0 ]] || { usage; exit 0; }

# Parse arguments
input=""
output=""
engine=""          # "" = auto fallback, or: docling|docling-layout|docling-ocr|docling-vlm|pypdf|poppler|ghostscript
insert_page=1
insert_ocr=1
engine_count=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)    usage; exit 0 ;;
        -i|--input)   input="$2"; shift 2 ;;
        -o|--output)  output="$2"; shift 2 ;;
        --docling)    engine="docling"; engine_count=$((engine_count+1)); shift ;;
        --layout)     engine="docling-layout"; engine_count=$((engine_count+1)); shift ;;
        --ocr)        engine="docling-ocr"; engine_count=$((engine_count+1)); shift ;;
        --vlm)        engine="docling-vlm"; engine_count=$((engine_count+1)); shift ;;
        --pypdf)      engine="pypdf"; engine_count=$((engine_count+1)); shift ;;
        --poppler)    engine="poppler"; engine_count=$((engine_count+1)); shift ;;
        --ghostscript|--gs) engine="ghostscript"; engine_count=$((engine_count+1)); shift ;;
        --insert-page-number)      insert_page=1; shift ;;
        --no-insert-page-number)   insert_page=0; shift ;;
        --insert-ocr-page-number)  insert_ocr=1; shift ;;
        --no-ocr-page-number)      insert_ocr=0; shift ;;
        -*)              die "unknown option: $1" ;;
        *)              die "unexpected argument: $1" ;;
    esac
done

[[ -n "$input" ]] || die "missing input file (use -i <file>)"
[[ -f "$input" ]] || die "file not found: $input"
[[ "$engine_count" -le 1 ]] || die "engine flags are mutually exclusive"

# Detect conversion direction from extensions
input_ext="$(lower_ext "$input")"

case "$input_ext" in
    pdf|docx|pptx|odt|xlsx|png|jpg|jpeg|bmp|webp|tiff)
        # To Markdown
        [[ -n "$output" ]] || output="$(derive_output "$input" md)"
        out_ext="$(lower_ext "$output")"
        [[ "$out_ext" == "md" ]] || {
            # Auto-fix: if user gave wrong extension, use .md
            output="$(derive_output "$input" md)"
            printf '  Note: output extension changed to .md for to-Markdown conversion\n' >&2
        }
        ;;
    md)
        # From Markdown — detect target from output extension
        [[ -n "$output" ]] || die "output file required for Markdown source (use -o output.pdf or -o output.html)"
        out_ext="$(lower_ext "$output")"
        case "$out_ext" in
            pdf)  ;; # valid
            html) ;; # valid
            *)    die "unsupported output format .$out_ext from Markdown (use .pdf or .html)" ;;
        esac
        ;;
    *)
        # Unknown input — try to convert to Markdown via pandoc
        [[ -n "$output" ]] || output="$(derive_output "$input" md)"
        ;;
esac

# Execute conversion
total_start=$(_timer_start)

case "$input_ext" in
    pdf|docx|pptx|odt|xlsx|png|jpg|jpeg|bmp|webp|tiff)
        _cmd_to_md "$input" "$output" "$engine" "$insert_page" "$insert_ocr"
        ;;
    md)
        out_ext="$(lower_ext "$output")"
        case "$out_ext" in
            pdf)  _cmd_to_pdf "$input" "$output" ;;
            html) _cmd_to_html "$input" "$output" ;;
        esac
        ;;
    *)
        _cmd_to_md "$input" "$output" "" "$insert_page" "$insert_ocr"
        ;;
esac

total_elapsed=$(_timer_elapsed "$total_start")
printf '\n  Total time: %s s\n' "$total_elapsed" >&2
