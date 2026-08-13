#!/usr/bin/env bash
# markdown.sh — Convert documents to and from Markdown
#
# Usage:
#   markdown.sh -i INPUT [-o OUTPUT] [options]   Convert document to/from Markdown
#   markdown.sh --help
#
# Format is auto-detected from input/output file extensions:
#   .pdf, .docx, .pptx, .odt, .xlsx → .md   (to Markdown)
#   .md → .pdf                                     (to PDF)
#   .md → .html                                    (to single-file HTML)
#
# Options:
#   -i, --input <file>           Input file (required)
#   -o, --output <file>          Output file path (default: auto-derived from input)
#   --pypdf                      Use pypdf engine (fast, text-layer only PDFs)
#   --poppler                    Use poppler/pdftotext engine
#   --ghostscript, --gs          Use ghostscript engine
#   --layout                     Preserve visual layout in PDF text (default: on)
#   --no-layout                  Disable layout preservation in PDF text
#   --insert-image-placeholder   Insert <!-- image --> on pages with images (default: on)
#   --no-insert-image-placeholder   Suppress image placeholders
#   --insert-page-number         Insert <!-- page N begin --> / <!-- page N end --> comments (default: on)
#   --no-insert-page-number      Suppress page comments
set -euo pipefail

# ── Helpers ──────────────────────────────────────────────────────────────────

die()  { printf 'error: %s\n' "$*" >&2; exit 1; }

# Strip leading and trailing whitespace from every line (keeps empty lines intact)
cleanup_md() {
    sed -i 's/^[[:space:]]*//;s/[[:space:]]*$//' "$1"
}

usage() { cat <<EOF
Usage:
  markdown.sh -i <input> [-o <output>] [options]

Options:
  -i, --input <file>           Input file (required)
  -o, --output <file>          Output file path (default: auto-derived from input)
  --pypdf                      Use pypdf engine (fast, text-layer only PDFs)
  --poppler                    Use poppler/pdftotext engine
  --ghostscript, --gs          Use ghostscript engine
  --layout                     Preserve visual layout in PDF text (default: on)
  --no-layout                  Disable layout preservation
  --insert-image-placeholder   Insert <!-- image --> on pages with images (default: on)
  --no-insert-image-placeholder   Suppress image placeholders
  --insert-page-number         Insert <!-- page N begin --> / <!-- page N end --> comments (default: on)
  --no-insert-page-number      Suppress page comments
  --help                       Show this help message

Format detection (from file extensions):
  To Markdown:  .pdf .docx .pptx .odt .xlsx → .md
  To PDF:       .md → .pdf
  To HTML:      .md → .html

PDF extraction engines:
  pypdf — fast, extracts text layer only (empty for scanned pages)
  poppler — fast, preserves visual layout (default) or raw text with --no-layout
  ghostscript — extracts text layer via txtwrite device (empty for scanned pages)

PDF extraction fallback chain (when no engine flag given):
  pypdf → poppler → ghostscript

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
# Each: extract_<engine> <input> <output> <insert_page> <images_file> <use_layout> <insert_image>
# Returns 0 on success, 1 on failure/skip.
#
# images_file: path to a file listing page numbers with images (one per line).
#              If the file exists and the current page is listed, <!-- image --> is inserted.
# use_layout:    1 = preserve visual layout (poppler: -layout), 0 = raw text
# insert_image:  1 = insert <!-- image --> markers, 0 = suppress

extract_pypdf() {
    local input="$1" output="$2" insert_page="$3" images_file="$4" use_layout="$5" insert_image="$6"

    if ! command -v uvx &>/dev/null; then
        printf '  Skipping pypdf (uvx not found)\n' >&2
        return 1
    fi

    printf '  Trying pypdf...\n' >&2

    # Build image page set for Python
    local _img_pages="[]"
    if [[ -s "$images_file" ]]; then
        _img_pages="$(awk 'BEGIN{printf "["} NR>1{printf ","} {printf "%d", $1} END{printf "]"}' "$images_file")"
    fi

    uvx --from pypdf python3 -c "
import sys
from pypdf import PdfReader

reader = PdfReader('$input')
pages = reader.pages
insert_page = $insert_page
insert_image = $insert_image
image_pages = set($_img_pages)

for i, page in enumerate(pages, 1):
    if insert_page:
        print(f'<!-- page {i} begin -->')
    has_image = i in image_pages
    # Also check page resources for embedded images
    if not has_image:
        resources = page.get('/Resources', {})
        if resources:
            xobjects = resources.get('/XObject', {})
            if xobjects:
                for xname in xobjects:
                    xobj = xobjects[xname]
                    if hasattr(xobj, 'get') and xobj.get('/Subtype') == '/Image':
                        has_image = True
                        break
    if has_image and insert_image:
        print('<!-- image -->')
    text = page.extract_text()
    if text:
        print(text)
    if insert_page:
        print(f'<!-- page {i} end -->')
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
    local input="$1" output="$2" insert_page="$3" images_file="$4" use_layout="$5" insert_image="$6"

    check_tool pdftotext poppler || return 1
    check_tool pdfinfo pdfinfo || return 1

    local _layout_flag="-layout"
    [[ "$use_layout" == "0" ]] && _layout_flag=""
    printf '  Trying poppler (pdftotext%s)...\n' " ${_layout_flag:-}" >&2

    local pages
    pages="$(pdfinfo "$input" 2>/dev/null | grep '^Pages:' | awk '{print $2}')"
    [[ -n "$pages" ]] || { printf '  Skipping poppler (cannot determine page count)\n' >&2; return 1; }

    > "$output"
    local p
    for (( p=1; p<=pages; p++ )); do
        [[ "$insert_page" == "1" ]] && printf '<!-- page %d begin -->\n' "$p" >> "$output"
        if [[ "$insert_image" == "1" ]] && [[ -s "$images_file" ]] && grep -qx "$p" "$images_file" 2>/dev/null; then
            printf '<!-- image -->\n' >> "$output"
        fi
        pdftotext ${_layout_flag:+-layout} -f "$p" -l "$p" "$input" - 2>/dev/null | tr -d '\f' >> "$output"
        [[ "$insert_page" == "1" ]] && printf '<!-- page %d end -->\n' "$p" >> "$output"
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
    local input="$1" output="$2" insert_page="$3" images_file="$4" use_layout="$5" insert_image="$6"

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
        [[ "$insert_page" == "1" ]] && printf '<!-- page %d begin -->\n' "$p" >> "$output"
        if [[ "$insert_image" == "1" ]] && [[ -s "$images_file" ]] && grep -qx "$p" "$images_file" 2>/dev/null; then
            printf '<!-- image -->\n' >> "$output"
        fi
        gs -sDEVICE=txtwrite -dFirstPage="$p" -dLastPage="$p" \
            -dSAFER -dBATCH -dNOPAUSE -sOutputFile="$_gs_tmp" "$input" >/dev/null 2>&1
        if [[ -s "$_gs_tmp" ]]; then
            tr -d '\f' < "$_gs_tmp" >> "$output"
        fi
        [[ "$insert_page" == "1" ]] && printf '<!-- page %d end -->\n' "$p" >> "$output"
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
    local input="$1" output="$2" engine="$3" insert_page="$4" use_layout="$5" insert_image="$6"

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
            # Detect pages with images (pdfimages lists: page num type width height ...
            local _images_file
            _images_file="$(mktemp --suffix=.img)"
            if command -v pdfimages &>/dev/null; then
                pdfimages -list "$input" 2>/dev/null | awk 'NR>1{print $1}' | sort -un > "$_images_file" || true
            fi
            if [[ -n "$engine" ]]; then
                local step_start step_elapsed
                step_start=$(_timer_start)
                extract_$engine "$input" "$output" "$insert_page" "$_images_file" "$use_layout" "$insert_image" || die "$engine extraction failed"
                step_elapsed=$(_timer_elapsed "$step_start")
                printf '  Extraction time: %s s\n' "$step_elapsed" >&2
            else
                local extracted=0
                for try_engine in pypdf poppler ghostscript; do
                    local step_start step_elapsed
                    step_start=$(_timer_start)
                    extract_$try_engine "$input" "$output" "$insert_page" "$_images_file" "$use_layout" "$insert_image" && {
                        extracted=1
                        step_elapsed=$(_timer_elapsed "$step_start")
                        printf '  Extraction time (%s): %s s\n' "$try_engine" "$step_elapsed" >&2
                        break
                    }
                done
                [[ "$extracted" -eq 1 ]] || die "no PDF engine available (tried: pypdf, poppler, ghostscript)"
            fi
            rm -f "$_images_file"
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
engine=""          # "" = auto fallback, or: pypdf|poppler|ghostscript
insert_page=1
use_layout=1
insert_image=1
engine_count=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)    usage; exit 0 ;;
        -i|--input)   input="$2"; shift 2 ;;
        -o|--output)  output="$2"; shift 2 ;;
        --pypdf)      engine="pypdf"; engine_count=$((engine_count+1)); shift ;;
        --poppler)    engine="poppler"; engine_count=$((engine_count+1)); shift ;;
        --ghostscript|--gs) engine="ghostscript"; engine_count=$((engine_count+1)); shift ;;
        --layout)                      use_layout=1; shift ;;
        --no-layout)                   use_layout=0; shift ;;
        --insert-image-placeholder)    insert_image=1; shift ;;
        --no-insert-image-placeholder) insert_image=0; shift ;;
        --insert-page-number)      insert_page=1; shift ;;
        --no-insert-page-number)   insert_page=0; shift ;;
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
    pdf|docx|pptx|odt|xlsx)
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
    pdf|docx|pptx|odt|xlsx)
        _cmd_to_md "$input" "$output" "$engine" "$insert_page" "$use_layout" "$insert_image"
        ;;
    md)
        out_ext="$(lower_ext "$output")"
        case "$out_ext" in
            pdf)  _cmd_to_pdf "$input" "$output" ;;
            html) _cmd_to_html "$input" "$output" ;;
        esac
        ;;
    *)
        _cmd_to_md "$input" "$output" "" "$insert_page" "$use_layout" "$insert_image"
        ;;
esac

total_elapsed=$(_timer_elapsed "$total_start")
printf '\n  Total time: %s s\n' "$total_elapsed" >&2
