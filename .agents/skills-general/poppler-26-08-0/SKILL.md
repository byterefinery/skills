---
name: poppler-26-08-0
description: Extract text, metadata, images, and pages from PDF files using poppler CLI tools (pdftotext, pdfinfo, pdfimages, pdftocairo, pdfseparate). Use when the user needs to parse, inspect, or convert PDFs from the command line.
license: GPL-2.0
compatibility: Requires poppler-utils 26.08.0 (pdftotext, pdfinfo, pdfimages, pdftocairo, pdfseparate, pdfunite). Install via `apt install poppler-utils`, `brew install poppler`, or your distro's package manager.
metadata:
  tags:
    - pdf
    - cli
    - text-extraction
    - conversion
---

# poppler 26.08.0

Poppler is a PDF rendering library based on the xpdf-3.0 code base. The `poppler-utils` package provides a suite of CLI tools for inspecting and converting PDFs. These tools are fast, reliable, and work entirely offline.

## Overview

| Tool | Purpose |
|------|---------|
| `pdftotext` | Extract plain text, XHTML with bounding boxes, or TSV |
| `pdfinfo` | Show metadata, page count, encryption, page sizes |
| `pdfimages` | List or extract embedded images (PNG, JPEG, TIFF, JBIG2) |
| `pdftocairo` | Render pages to PNG, JPEG, TIFF, SVG, PS, or PDF |
| `pdfseparate` | Split a multi-page PDF into individual page files |
| `pdfunite` | Merge multiple PDFs into one |
| `pdftohtml` | Convert PDF to HTML (with or without images) |

All tools accept `-f <n>` / `-l <n>` for page ranges, `-opw` / `-upw` for passwords, and `-q` for quiet mode. Exit code 0 = success, 1 = can't open PDF, 2 = can't open output, 3 = permission error, 99 = other.

## Usage

### Extract text with pdftotext

Basic extraction (reading order, columns reassembled):

```bash
pdftotext input.pdf output.txt
pdftotext input.pdf -          # stdout
pdftotext -f 3 -l 5 input.pdf output.txt   # pages 3-5
```

Keep physical layout (columns, positioning preserved):

```bash
pdftotext -layout input.pdf output.txt
```

Extract with word bounding boxes (XHTML or TSV):

```bash
pdftotext -bbox input.pdf output.html   # per-word boxes
pdftotext -bbox-layout input.pdf output.html   # block/line/word boxes
pdftotext -tsv input.pdf output.tsv     # TSV with boxes
```

Control hyphen handling:

```bash
pdftotext -remove-hyphens none input.pdf output.txt   # keep all hyphens
pdftotext -remove-hyphens soft input.pdf output.txt   # only remove soft hyphens
pdftotext -remove-hyphens all input.pdf output.txt    # remove all (default)
```

Skip diagonal text (watermarks):

```bash
pdftotext -nodiag input.pdf output.txt
```

Crop region (pixel coordinates):

```bash
pdftotext -x 100 -y 200 -W 500 -H 300 input.pdf output.txt
```

### Inspect metadata with pdfinfo

```bash
pdfinfo input.pdf
pdfinfo -meta input.pdf          # XMP metadata stream
pdfinfo -box input.pdf           # MediaBox, CropBox, etc.
pdfinfo -isodates input.pdf      # ISO-8601 dates
pdfinfo -dests input.pdf         # named destinations (bookmarks)
pdfinfo -url input.pdf           # URLs in annotations
pdfinfo -js input.pdf            # embedded JavaScript
pdfinfo -f 1 -l 3 input.pdf      # per-page sizes for pages 1-3
```

### Extract images with pdfimages

List images without extracting:

```bash
pdfimages -list input.pdf
```

Extract all images as PNG:

```bash
pdfimages -png input.pdf output-prefix   # output-prefix-000.png, etc.
```

Extract as native formats (no re-encoding):

```bash
pdfimages -j input.pdf output-prefix     # JPEG images stay as JPEG
pdfimages -jp2 input.pdf output-prefix   # JPEG2000 → .jp2
pdfimages -jbig2 input.pdf output-prefix # JBIG2 → .jb2e + .jb2g
```

Extract only from specific pages:

```bash
pdfimages -f 2 -l 2 -png input.pdf page2-img
```

### Render pages with pdftocairo

One format flag is required. `-png` is most common:

```bash
pdftocairo -png input.pdf                    # one PNG per page
pdftocairo -png -singlefile input.pdf out    # first page only → out.png
pdftocairo -png -r 300 input.pdf out         # 300 DPI
pdftocairo -png -scale-to 1920 input.pdf out # long side = 1920px
pdftocairo -svg input.pdf output.svg         # vector SVG
pdftocairo -pdf input.pdf output.pdf         # PDF (re-render, flattens)
```

Transparency and color:

```bash
pdftocairo -png -transp input.pdf out        # transparent background (PNG/TIFF)
pdftocairo -png -mono input.pdf out          # monochrome (PNG/TIFF)
pdftocairo -png -gray input.pdf out          # grayscale
pdftocairo -jpeg -jpegopt quality=85,progressive=y input.pdf out
```

Odd/even pages:

```bash
pdftocairo -png -o input.pdf out   # odd pages only
pdftocairo -png -e input.pdf out   # even pages only
```

### Split and merge PDFs

Split into individual pages:

```bash
pdfseparate input.pdf page-%d.pdf   # page-1.pdf, page-2.pdf, ...
pdfseparate -f 3 -l 5 input.pdf part-%d.pdf
```

Merge PDFs:

```bash
pdfunite a.pdf b.pdf c.pdf combined.pdf
```

### HTML conversion

```bash
pdftohtml input.pdf                  # framed HTML + images
pdftohtml -s input.pdf               # single HTML file
pdftohtml -noframes input.pdf        # no frames
pdftohtml -i input.pdf               # ignore images (text only)
pdftohtml -xml input.pdf             # XML for post-processing
pdftohtml -stdout input.pdf > out.html
```

## Gotchas

- **`pdftotext` reading order vs layout** — default mode reassembles columns into reading order. Use `-layout` when you need to preserve visual positioning (e.g., forms, tables). Use `-nodiag` to skip watermarks drawn at angles.
- **`pdftotext` raw mode is deprecated** — `-raw` keeps content stream order, which is unpredictable. Prefer default mode or `-layout`.
- **Hyphen removal only works in default mode** — `-remove-hyphens` has no effect with `-layout` or `-raw`.
- **`pdftocairo` requires exactly one format flag** — you must specify one of `-png`, `-jpeg`, `-tiff`, `-pdf`, `-ps`, `-eps`, `-svg`, or `-print`. Omitting all fails silently on some versions.
- **`pdftocairo` default resolution is 150 DPI** — higher than `pdftotext`'s 72 DPI default. Use `-r 72` if you want screen-resolution previews.
- **`pdfimages -list` shows the real image data** — use this before extracting to see count, dimensions, color space, and whether images are already JPEG/PNG (avoid unnecessary re-encoding with `-j`, `-png`).
- **Encrypted PDFs need passwords** — pass `-upw "password"` for user password or `-opw "password"` for owner password. Owner password bypasses all restrictions.
- **`-f` and `-l` are 1-indexed** — page numbers start at 1, not 0.
- **`pdftotext` output to stdout** — use `-` as the output filename. Input from stdin also uses `-` as the input filename.
- **`pdfseparate` pattern uses `%d`** — the pattern string uses printf-style `%d` for page numbers, not `{}` or `%0`.
- **Some fonts are unrecoverable** — if a PDF has mangled font encodings, `pdftotext` will produce garbled output. There is no fix short of OCR.
- **`pdftocairo -svg` produces one file** — unlike image formats that produce one file per page, SVG output is a single file containing all pages unless `-f`/`-l` restricts to one page.
- **`pdftocairo -eps` only handles single pages** — you must specify `-f N -l N` for the same page, or it will fail on multi-page PDFs.
