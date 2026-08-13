---
name: ghostpdl-10-07-1
description: GhostPDL 10.07.1 — the unified Artifex document processing suite. Covers Ghostscript (PostScript Level 3 / PDF 1.0-2.0), GhostPDF (C-based PDF interpreter), GhostPCL (PCL5/PXL), GhostXPS (XPS), and GhostPDL (auto-detecting multi-language framework). Use for PDF conversion/optimization, PostScript rendering, format conversion (PS/PDF/PCL/XPS/images), rasterization, N-up imposition, OCR, color management, font handling, embedding via gsapi C/Python/Java/C# bindings, CUPS printing, and building from source.
license: AGPL-3.0 / Commercial
compatibility: Requires C compiler (GCC/Clang/MSVC), GNU make (Unix) or nmake (Windows). Runtime: Linux, macOS, Windows, BSD. Optional: Tesseract + Leptonica for OCR, CUPS for printing, Fontconfig for system fonts
metadata:
  tags:
    - document-processing
    - pdf
    - postscript
    - pcl
    - xps
    - rasterization
    - cli
---

# ghostpdl 10.07.1

## Overview

GhostPDL is the umbrella source distribution for the entire Ghostscript family of products. Each interpreter shares the same Ghostscript graphics library and can be compiled individually or together.

**Components:**

- **Ghostscript** — PostScript Level 3 and PDF 1.0-2.0 interpreter and renderer (`gs`)
- **GhostPDF** — Standalone C-based PDF interpreter, default since 9.55 (`gpdf`)
- **GhostPCL** — PCL5 and PCL/XL (PXL) interpreter (`gpcl6`)
- **GhostXPS** — XPS (XML Paper Specification) interpreter (`gxps`)
- **GhostPDL** — Multi-language framework; auto-detects PS, PDF, PCL, XPS, and image formats (`gpdl`)

When running as GhostPDL, the interpreter automatically detects input language using file signatures and heuristics — no flag needed for mixed-language job streams. PJL (Printer Job Language) framing is also supported.

## Usage

### Executables

```bash
gs          # Ghostscript (PostScript + PDF)
gpdf        # GhostPDF (PDF only, C-based interpreter)
gpcl6       # GhostPCL (PCL/PXL)
gxps        # GhostXPS (XPS)
gpdl        # GhostPDL (auto-detect language)
```

Windows executables: `gswin32c`, `gswin64c`, `gswin32`, `gswin64`.

### Core Flags

```bash
# Non-interactive batch mode (always use these for scripting)
gs -dBATCH -dNOPAUSE -sDEVICE=... -sOutputFile=out file

# List available devices and help
gs -h

# Version
gs --version

# Quiet mode (suppress non-error output to stdout)
gs -q

# Security-restricted mode (no file read/write except specified)
gs -dSAFER

# Parse DSC (Document Structuring Conventions) comments
gs -dPARANOIDSAFER    # Strictest security
```

### Output Devices

```bash
# Raster image output
gs -sDEVICE=png16m    # 24-bit color PNG
gs -sDEVICE=pngalpha  # 32-bit RGBA PNG
gs -sDEVICE=pnggray   # 8-bit grayscale PNG
gs -sDEVICE=png256    # 8-bit palette PNG
gs -sDEVICE=png16     # 4-bit palette PNG
gs -sDEVICE=jpeg      # JPEG
gs -sDEVICE=jpeggray  # Grayscale JPEG
gs -sDEVICE=tiff24nc  # 24-bit TIFF (no compression)
gs -sDEVICE=tiff32nc  # 32-bit TIFF (no compression)
gs -sDEVICE=tiffgray  # Grayscale TIFF
gs -sDEVICE=tiffg4    # Group 4 fax TIFF (1-bit)
gs -sDEVICE=tiffpack  # Packbits TIFF
gs -sDEVICE=bmp16m    # 24-bit BMP
gs -sDEVICE=bmp256    # 8-bit palette BMP
gs -sDEVICE=bmpgray   # Grayscale BMP
gs -sDEVICE=pcx16m    # 24-bit PCX
gs -sDEVICE=pam       # Netpbm PAM (portable anymap)
gs -sDEVICE=ppmraw    # Raw PPM
gs -sDEVICE=pgm       # PGM (grayscale)
gs -sDEVICE=pbmraw    # Raw PBM (1-bit)
gs -sDEVICE=psd       # Adobe Photoshop PSD
gs -sDEVICE=psd2      # PSD version 2 (with alpha)

# Vector/document output
gs -sDEVICE=pdfwrite  # PDF output (convert PS/PDF/images to PDF)
gs -sDEVICE=ps2write  # PostScript Level 2 output
gs -sDEVICE=ps3write  # PostScript Level 3 output
gs -sDEVICE=eps2write # EPS output
gs -sDEVICE=eps3write # EPS Level 3 output

# Printer drivers
gs -sDEVICE=cups      # CUPS (generates PPD-based output)
gs -sDEVICE=cupsated  # CUPS for AT&T devices
gs -sDEVICE=ljet4     # HP LaserJet 4
gs -sDEVICE=hp2600    # HP DeskJet 2600

# Special devices
gs -sDEVICE=bbox      # Calculate bounding box (EPS analysis)
gs -sDEVICE=nullpage  # Discard output (validation only)
gs -sDEVICE=textonly  # Extract text as PostScript comments
```

### Resolution

```bash
gs -r300              # 300 DPI (both axes)
gs -r300x150           # 300x150 DPI
gs -dNOPAUSE -dBATCH -sDEVICE=png16m -r600 -sOutputFile=out.png input.pdf
```

### Page Selection

```bash
gs -dFirstPage=1 -dLastPage=5 -sDEVICE=png16m -sOutputFile=p%d.png input.pdf
gs -dFirstPage=3 -dLastPage=3 -sDEVICE=png16m -sOutputFile=page3.png input.pdf
```

### PDF Conversion

```bash
# PostScript to PDF
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=out.pdf input.ps

# Or use the convenience wrapper (PDF 1.4 by default)
ps2pdf input.ps output.pdf

# PDF 1.4 (Acrobat 5+)
ps2pdf14 input.ps output.pdf

# PDF 1.3 (Acrobat 4+)
ps2pdf13 input.ps output.pdf

# PDF 1.2 (Acrobat 3+)
ps2pdf12 input.ps output.pdf

# PDF to PostScript
pdf2ps input.pdf output.ps

# PDF to PDF (reprocess/fix)
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=fixed.pdf input.pdf
```

### PDF Optimization / Compression

```bash
# Compress PDF with quality presets
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -dCompatibilityLevel=1.5 -dPDFSETTINGS=/ebook \
   -sOutputFile=compressed.pdf input.pdf

# PDFSETTINGS options:
#   /screen    — 72 dpi, lowest quality, smallest size
#   /ebook     — 150 dpi, medium quality
#   /printer   — 300 dpi, good quality
#   /prepress  — 300 dpi, color-preserving, largest
#   /default   — no image downsampling
```

### PDF to Images

```bash
# PDF to PNG (one file per page)
gs -dBATCH -dNOPAUSE -sDEVICE=png16m -r300 \
   -sOutputFile=page_%03d.png input.pdf

# PDF to JPEG (first page only)
gs -dBATCH -dNOPAUSE -dFirstPage=1 -dLastPage=1 \
   -sDEVICE=jpeg -r150 -sOutputFile=page1.jpg input.pdf

# PDF to grayscale PNG
gs -dBATCH -dNOPAUSE -sDEVICE=pnggray -r300 \
   -sOutputFile=page_%03d.png input.pdf

# PDF to PNG with alpha
gs -dBATCH -dNOPAUSE -sDEVICE=pngalpha -r300 \
   -sOutputFile=page_%03d.png input.pdf
```

### Password-Protected PDFs

```bash
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sPDFPassword=secret -sOutputFile=out.pdf input.pdf
```

### Image to PDF

```bash
# Single image to PDF
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=image.pdf photo.jpg

# Multiple images to multi-page PDF
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=combined.pdf *.jpg
```

### N-Up Imposition

```bash
# 2x2 imposition (4 pages per sheet)
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sPAPERSIZE=a4 -dPDFFitPage \
   -c "[/PerPage << /NumPagesAcross 2 /NumPagesDown 2 >> /setpagedevice pdfmark" \
   -f input.pdf -sOutputFile=imposed.pdf

# Or use the gsnup.ps wrapper for PostScript input
gs -dBATCH -dNOPAUSE -sDEVICE=ps2write \
   -c "save" -f /path/to/lib/gsnup.ps -c "restore" \
   -c ".Nx 3 def .Ny 2 def" -f input.ps -sOutputFile=out.ps
```

### OCR (Searchable PDF)

Requires build with Tesseract + Leptonica. Uses `ocrps` device.

```bash
# Convert scanned PDF to searchable PDF
gs -dBATCH -dNOPAUSE -sDEVICE=ocrps \
   -sOutputFile=searchable.pdf -sOCRLanguage=eng \
   -dFirstPage=1 -dLastPage=1 scanned.pdf

# OCR with specific language
gs -dBATCH -dNOPAUSE -sDEVICE=ocrps \
   -sOCRLanguage=eng+deu -sOutputFile=out.pdf scanned.pdf

# Extract OCR text only (no re-rendering)
gs -dBATCH -dNOPAUSE -sDEVICE=ocrqpdf \
   -sOutputFile=text.pdf scanned.pdf
```

### XPS Conversion (GhostXPS)

```bash
gxps -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
     -sOutputFile=output.pdf input.xps
```

### PCL Conversion (GhostPCL)

```bash
gpcl6 -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
      -sOutputFile=output.pdf input.pcl
```

### Color Management

```bash
# ICC-based color conversion
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputProfile=sRGB.icc \
   -sColorConversionStrategy=RGB \
   -sOutputFile=out.pdf input.pdf

# Color conversion strategies:
#   /LeaveColorUnchanged — keep source color spaces
#   /CMYK               — convert to CMYK
#   /Gray               — convert to grayscale
#   /RGB                — convert to RGB
```

### Font Handling

```bash
# Specify font directory
gs -I/usr/share/fonts -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=out.pdf input.ps

# Embed all fonts
gs -sDEVICE=pdfwrite -c "<</EmbedAllFonts true>> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf

# Subset fonts (only embed used glyphs)
gs -sDEVICE=pdfwrite -c "<</SubsetFonts true /MaxSubsetPct 100>> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf

# List available fonts
gs -q -c "FontForAllFonts = { exch pop (=) print dup /FontName knownoget { exch pop ( ) print (</FontName >) print /FontMatrix get matrix defaultmatrix ne { (</FontMatrix >) print } if } if (>) print (\n) print } stop" -c "systemdict /FontDirectory get exch { exch exch exec } forall" -c quit
```

### Bounding Box Calculation

```bash
gs -sDEVICE=bbox input.eps
# Output: %%BoundingBox: 0 25 583 732
#         %%HiResBoundingBox: 0.808497 25.009496 582.994503 731.809445
```

### CUPS Printing

```bash
# List available CUPS printers
gs -sDEVICE=cups -sOutputFile=%stdout% -dBATCH -dNOPAUSE input.pdf | lp -d printer_name

# Or directly via cups device
gs -sDEVICE=cups -sOutputFile=/dev/usb/lp0 -dBATCH -dNOPAUSE input.pdf
```

### GhostPDL Auto-Detection

```bash
# GhostPDL auto-detects input format (PS, PDF, PCL, XPS, images)
gpdl -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=out.pdf input.any

# Mixed-language PJL job stream
gpdl -dBATCH -dNOPAUSE -sDEVICE=png16m -sOutputFile=p%d.png mixed_job.pjl
```

## Gotchas

- **Always use `-dBATCH -dNOPAUSE` for scripting** — without these, Ghostscript runs interactively and waits for user input between pages. Scripts will hang.

- **`-dSAFER` restricts file access** — in safer mode, Ghostscript cannot read/write arbitrary files. Use `-I` to specify allowed directories. Some PostScript files use disk operations that will fail under `-dSAFER`.

- **`-sDEVICE` must appear before the input file** — device selection only takes effect on first use. Place it before the filename, not after.

- **Output file numbering uses `%d`** — `-sOutputFile=page_%d.png` produces `page_1.png`, `page_2.png`, etc. Use `%03d` for zero-padded: `page_001.png`. On Windows, double the `%` to `%%d` to avoid shell interpretation.

- **`-sOutputFile=-` sends to stdout** — combine with `-q` to suppress other stdout messages. Useful for piping: `gs -q -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=- input.ps | ...`

- **`-sOutputFile=%stdout%` is the Windows-compatible form** — same as `-` but works on Windows where `-` alone may not.

- **`-sOutputFile=%pipe%command` pipes output** — e.g., `-sOutputFile=%pipe%lpr` sends directly to the printer. On Windows, use `%%pipe%%`.

- **Ghostscript is not thread-safe by default** — unless compiled with `--enable-threading`, only one instance may run at a time. The gsapi C interface enforces this with a global counter.

- **`ps2pdf` defaults to PDF 1.4** — use `ps2pdf14`, `ps2pdf13`, or `ps2pdf12` for specific versions, or pass `-dCompatibilityLevel=X.Y` to `ps2pdfwr`.

- **`-dPDFSETTINGS` only works with `pdfwrite`** — it's a convenience wrapper for many distiller parameters. It has no effect on raster devices.

- **Resolution (`-r`) is per-device** — some printer devices ignore `-r` and use their native resolution. Raster devices (png, jpeg, tiff) always respect it.

- **GhostPDF (C-based) is the default PDF interpreter since 9.55** — the older PostScript-based PDF interpreter is still available but requires explicit selection. GhostPDF is faster and more memory-efficient.

- **PCL/XL fonts use AFPL license** — the URW fonts bundled with GhostPCL are under the Arts and Crafts Public License, which prohibits commercial use in some contexts. Check `pcl/COPYING.AFPL` in source.

- **ICC profiles need `-sOutputProfile` path** — the path is relative to Ghostscript's search path. Use absolute paths or place profiles in a `-I` directory.

- **`gs -h` shows build-specific device list** — available devices depend on how Ghostscript was compiled. A minimal build may lack many devices.

- **`-c` executes PostScript before files, `-f` reads files** — the pattern `-c "setup code" -f input.ps` is common for pre-configuring the interpreter.

- **`setdistillerparams` is PostScript-level** — when using `pdfwrite`, you can configure it via PostScript dictionaries: `-c "<< /Key value >> setdistillerparams" -f file.ps`.

- **Memory limits for large documents** — Ghostscript uses virtual memory but very large PDFs or high-resolution rasterization can exhaust RAM. Use `-dMaxBitmap=...` to limit individual bitmap size.

- **`-dFirstPage`/`-dLastPage` are 1-indexed** — page 1 is the first page, not page 0.

- **EPS to PDF conversion needs care** — EPS files may not define a proper PageSize. Use `-sPAPERSIZE=a4` or let Ghostscript auto-detect via bounding box.

- **`gs_init.ps` revision must match binary** — mixing Resource files from different Ghostscript versions causes "Interpreter revision does not match" errors.

## References

- [01-command-line-reference](references/01-command-line-reference.md) — Full command-line switch reference
- [02-output-devices](references/02-output-devices.md) — Complete device catalog and parameters
- [03-pdf-conversion](references/03-pdf-conversion.md) — PDF writing, optimization, distiller parameters
- [04-embedding-gsapi](references/04-embedding-gsapi.md) — C, Python, Java, C# API integration
- [05-building-from-source](references/05-building-from-source.md) — Configure options, make targets, shared library
- [06-other-interpreters](references/06-other-interpreters.md) — GhostPDF, GhostPCL, GhostXPS, GhostPDL specifics
- [07-color-management](references/07-color-management.md) — ICC profiles, color spaces, conversion strategies
- [08-security](references/08-security.md) — -dSAFER, -dPARANOIDSAFER, sandboxing, trusted code
