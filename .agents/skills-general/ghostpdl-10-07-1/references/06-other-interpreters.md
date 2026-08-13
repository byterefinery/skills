# Other Interpreters — GhostPDF, GhostPCL, GhostXPS, GhostPDL

## GhostPDF (gpdf)

The C-based PDF interpreter, default since Ghostscript 9.55. Replaces the older PostScript-based PDF interpreter with a native C implementation.

### Characteristics

- **Faster** than the PS-based PDF interpreter
- **Lower memory usage** — doesn't need to run the full PostScript VM
- **PDF 1.0 through 2.0** support
- **Standalone executable** — `gpdf`
- **Can be disabled** at build time with `--with-pdf=none`

### Usage

```bash
# Render PDF to images
gpdf -dBATCH -dNOPAUSE -sDEVICE=png16m -r300 \
     -sOutputFile=page_%03d.png input.pdf

# Convert PDF to PDF (reprocess)
gpdf -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
     -sOutputFile=out.pdf input.pdf

# Convert PDF to PostScript
gpdf -dBATCH -dNOPAUSE -sDEVICE=ps2write \
     -sOutputFile=out.ps input.pdf
```

### GhostPDF vs Ghostscript for PDF

| Aspect | GhostPDF (gpdf) | Ghostscript (gs) |
|--------|-----------------|------------------|
| Speed | Faster | Slower (full PS VM) |
| Memory | Lower | Higher |
| PDF features | Core rendering | All (PS execution too) |
| JavaScript | Limited | Full (via PS) |
| Forms | Basic | Full |
| Use case | PDF rendering | PS + PDF processing |

## GhostPCL (gpcl6)

PCL5 and PCL/XL (PXL) interpreter. PCL (Printer Command Language) is HP's page description language, widely used in laser printers.

### Supported Languages

- **PCL5** — HP's standard printer language
- **PCL/XL (PXL)** — HP's XML-based PCL extension
- **PJL** — Printer Job Language (job framing)

### Usage

```bash
# PCL to PDF
gpcl6 -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
      -sOutputFile=output.pdf input.pcl

# PCL to PNG
gpcl6 -dBATCH -dNOPAUSE -sDEVICE=png16m -r300 \
      -sOutputFile=page_%03d.png input.pcl

# PXL to PDF
gpcl6 -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
      -sOutputFile=output.pdf input.pxl

# PCL to PostScript
gpcl6 -dBATCH -dNOPAUSE -sDEVICE=ps2write \
      -sOutputFile=output.ps input.pcl
```

### PCL Fonts

GhostPCL uses bundled URW fonts. These are distributed under the AFPL (Arts and Crafts Public License), which has commercial use restrictions. See `pcl/COPYING.AFPL` in the source tree.

```bash
# Specify additional font directories
gpcl6 -I/usr/share/fonts -dBATCH -dNOPAUSE \
      -sDEVICE=pdfwrite -sOutputFile=out.pdf input.pcl
```

### Build Options

```bash
# Include PCL
./configure --with-pcl=pcl6    # default

# Exclude PCL
./configure --without-pcl
```

## GhostXPS (gxps)

XPS (XML Paper Specification) interpreter. XPS is Microsoft's fixed-document format, similar to PDF but XML-based.

### Usage

```bash
# XPS to PDF
gxps -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
     -sOutputFile=output.pdf input.xps

# XPS to PNG
gxps -dBATCH -dNOPAUSE -sDEVICE=png16m -r300 \
     -sOutputFile=page_%03d.png input.xps

# XPS to PostScript
gxps -dBATCH -dNOPAUSE -sDEVICE=ps2write \
     -sOutputFile=output.ps input.xps
```

### XPS Features

- Renders XPS documents (`.xps`, `.oxps`)
- Supports XPS fonts, images, vectors, gradients
- Open XML packaging (ZIP container with XML parts)
- JPEG, PNG, TIFF, JPEG XR image support within XPS
- Font embedding (TrueType, CFF)

### Build Options

```bash
# Include XPS
./configure --with-xps=xps    # default

# Exclude XPS
./configure --without-xps
```

## GhostPDL (gpdl)

The auto-detecting multi-language framework. Automatically identifies the input format and routes to the appropriate interpreter.

### Supported Input Formats

| Format | Detection Method |
|--------|-----------------|
| PostScript | `%!` magic number |
| PDF | `%PDF-` magic number |
| PCL | ESC sequences |
| PXL | `%PXL` magic number |
| XPS | ZIP container with `.xps` manifest |
| JPEG | JFIF/EXIF headers |
| PNG | PNG signature |
| TIFF | TIFF magic number |
| PWG Raster | PWG header |

### Usage

```bash
# Auto-detect and convert
gpdl -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
     -sOutputFile=output.pdf input.any

# Mixed PJL job stream
gpdl -dBATCH -dNOPAUSE -sDEVICE=png16m -r300 \
     -sOutputFile=page_%03d.png mixed_job.pjl

# Auto-detect and render
gpdl -dBATCH -dNOPAUSE -sDEVICE=png16m \
     -sOutputFile=rendered.png document.any
```

### PJL Support

PJL (Printer Job Language) frames multiple jobs:

```
@PJL JOB NAME="job1"
%!PS-PostScript-content-here
@PJL EOJ

@PJL JOB NAME="job2"
%PDF-1.4
%PDF-content-here
@PJL EOJ
```

GhostPDL handles PJL framing automatically, separating and processing each job.

### Build Options

```bash
# Include GhostPDL
./configure --with-gpdl=gpdl    # default

# Exclude GhostPDL
./configure --without-gpdl
```

## Image Input

GhostPDL and Ghostscript can read image files directly:

```bash
# JPEG to PDF
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=image.pdf photo.jpg

# PNG to PDF
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=image.pdf graphic.png

# TIFF to PNG
gs -dBATCH -dNOPAUSE -sDEVICE=png16m \
   -sOutputFile=output.png scan.tiff

# Multiple images to multi-page PDF
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=album.pdf photo1.jpg photo2.png photo3.tiff
```

Supported input image formats:
- JPEG (JFIF, EXIF)
- PNG
- TIFF
- JBIG2
- JPEG 2000 (JP2)
- PWG Raster
- BMP
- GIF (limited)

## Interpreter Selection

### Command-Line Selection

```bash
# Use specific interpreter
gs   # PostScript + PDF (PostScript-based PDF interpreter)
gpdf # PDF only (C-based interpreter)
gpcl6 # PCL/PXL
gxps  # XPS
gpdl  # Auto-detect all
```

### Build-Time Selection

```bash
# All interpreters
./configure

# Ghostscript only
./configure --without-pcl --without-xps --without-pdf --without-gpdl

# Ghostscript + PCL
./configure --without-xps --without-gpdl

# Custom names
./configure --with-gs=mygs --with-pcl=mygpcl --with-xps=mygxps
```

## Gotchas

- **GhostPDF is faster for pure PDF rendering** — if you only need to render PDFs (not execute PostScript), use `gpdf` instead of `gs`.
- **PCL fonts have licensing restrictions** — the bundled URW fonts use AFPL, which may restrict commercial use. Check `pcl/COPYING.AFPL`.
- **GhostPDL auto-detection isn't perfect** — files with ambiguous headers may be misidentified. Use the specific interpreter (`gs`, `gpdf`, `gpcl6`, `gxps`) for reliable results.
- **XPS requires expat** — the XPS interpreter needs XML parsing. Expat is bundled, so no external dependency is needed.
- **PJL framing is transparent** — GhostPDL handles PJL job separation automatically. No special flags needed.
- **Image input quality** — when converting images to PDF, use `-dPDFSETTINGS=/prepress` to avoid quality loss from downsampling.
- **GhostPDF doesn't support PostScript** — it's PDF-only. Use `gs` for PostScript input, even if the output is PDF.
