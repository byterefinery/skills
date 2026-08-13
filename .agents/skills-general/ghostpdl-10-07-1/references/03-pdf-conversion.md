# PDF Conversion

## pdfwrite Device

The `pdfwrite` device is Ghostscript's PDF output engine. It converts PostScript, PDF, PCL, XPS, and raster images into PDF. It is the most feature-rich device and supports extensive configuration.

### Basic Usage

```bash
# PostScript to PDF
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=out.pdf input.ps

# PDF to PDF (reprocess/repair)
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=fixed.pdf input.pdf

# Images to PDF
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=images.pdf *.jpg

# Mixed input to PDF
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=combined.pdf image.jpg doc.ps photo.png
```

### PDF Version Targeting

```bash
# Target specific PDF version
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -dCompatibilityLevel=1.4 \
   -sOutputFile=out.pdf input.ps

# Valid versions: 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 2.0
```

### Quality Presets (-dPDFSETTINGS)

```bash
# Lowest quality, smallest file
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dPDFSETTINGS=/screen -sOutputFile=out.pdf input.pdf

# Medium quality (recommended for ebooks)
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -sOutputFile=out.pdf input.pdf

# Good quality (recommended for printing)
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dPDFSETTINGS=/printer -sOutputFile=out.pdf input.pdf

# Highest quality, color-preserving
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -sOutputFile=out.pdf input.pdf

# No image downsampling
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dPDFSETTINGS=/default -sOutputFile=out.pdf input.pdf
```

Each preset sets multiple parameters:

| Preset | Resolution | Image Filter | Downsampling |
|--------|-----------|--------------|--------------|
| `/screen` | 72 dpi | JPEG | Aggressive |
| `/ebook` | 150 dpi | JPEG | Moderate |
| `/printer` | 300 dpi | JPEG | Conservative |
| `/prepress` | 300 dpi | JPEG/Lossless | Conservative |
| `/default` | Original | Pass-through | None |

### Distiller Parameters

Fine-grained control via `setdistillerparams`:

```bash
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -c "<<
     /NeverEmbed []
     /AlwaysEmbed [/Helvetica /Times-Roman /Courier]
     /EmbedAllFonts true
     /SubsetFonts true
     /MaxSubsetPct 100
     /CanonifyFonts true
     /Optimize true
     /CompressPages true
     /UseFlateCompression true
     /CompressImages true
     /ConvertImagesToJPEG true
     /JPEGQ 85
     /ColorImageDownsampleType /Bicubic
     /ColorImageDownsampleThreshold 1.5
     /ColorImageResolution 300
     /GrayImageDownsampleType /Bicubic
     /GrayImageDownsampleThreshold 1.5
     /GrayImageResolution 300
     /MonoImageDownsampleType /Subsample
     /MonoImageDownsampleThreshold 1.5
     /MonoImageResolution 300
     /AutoFilterColorImages true
     /AutoFilterGrayImages true
     /DownsampleColorImages true
     /DownsampleGrayImages true
     /DownsampleMonoImages true
     /ColorConversionStrategy /LeaveColorUnchanged
     /DetectBlends true
     /PreserveCopyPage true
     /PassThroughJPEGImages true
     /PassThroughJPXImages true
     /CreateJobTicket false
     /OffOptimizations 0
     /PDFXSetBleedBoxToMediaBox true
     /PDFAcroForm false
     /PDFAFormUseUserLevel false
     /OPM 0
   >> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf
```

### Font Handling

```bash
# Embed all fonts
gs -sDEVICE=pdfwrite -c "<< /EmbedAllFonts true >> setdistillerparams" -f input.ps -sOutputFile=out.pdf

# Never embed specific fonts
gs -sDEVICE=pdfwrite -c "<< /NeverEmbed [/Helvetica /Times-Roman] >> setdistillerparams" -f input.ps -sOutputFile=out.pdf

# Always embed specific fonts
gs -sDEVICE=pdfwrite -c "<< /AlwaysEmbed [/CustomFont] >> setdistillerparams" -f input.ps -sOutputFile=out.pdf

# Subset fonts (only used glyphs)
gs -sDEVICE=pdfwrite -c "<< /SubsetFonts true /MaxSubsetPct 100 >> setdistillerparams" -f input.ps -sOutputFile=out.pdf

# Don't subset fonts
gs -sDEVICE=pdfwrite -c "<< /SubsetFonts false >> setdistillerparams" -f input.ps -sOutputFile=out.pdf

# Canonify font names (standardize to base 14)
gs -sDEVICE=pdfwrite -c "<< /CanonifyFonts true >> setdistillerparams" -f input.ps -sOutputFile=out.pdf
```

### Image Handling

```bash
# JPEG quality
gs -sDEVICE=pdfwrite -c "<< /JPEGQ 90 >> setdistillerparams" -f input.ps -sOutputFile=out.pdf

# Don't re-encode existing JPEGs
gs -sDEVICE=pdfwrite -c "<< /PassThroughJPEGImages true >> setdistillerparams" -f input.ps -sOutputFile=out.pdf

# Don't re-encode existing JPEG 2000
gs -sDEVICE=pdfwrite -c "<< /PassThroughJPXImages true >> setdistillerparams" -f input.ps -sOutputFile=out.pdf

# Color image downsampling
gs -sDEVICE=pdfwrite -c "<<
  /ColorImageDownsampleType /Bicubic
  /ColorImageDownsampleThreshold 1.1
  /ColorImageResolution 150
>> setdistillerparams" -f input.ps -sOutputFile=out.pdf

# Downsampling types:
#   /Bicubic   — Bicubic interpolation (best quality)
#   /Bilinear  — Bilinear interpolation
#   /Average   — Average downsampling (fastest)
#   /Subsample — Subsampling (fastest, lowest quality)
```

### Compression

```bash
# Enable page stream compression
gs -sDEVICE=pdfwrite -c "<< /CompressPages true >> setdistillerparams" -f input.ps -sOutputFile=out.pdf

# Use Flate compression
gs -sDEVICE=pdfwrite -c "<< /UseFlateCompression true >> setdistillerparams" -f input.ps -sOutputFile=out.pdf

# ASCII85 encode pages
gs -sDEVICE=pdfwrite -c "<< /ASCII85EncodePages true >> setdistillerparams" -f input.ps -sOutputFile=out.pdf

# Enable optimization
gs -sDEVICE=pdfwrite -c "<< /Optimize true >> setdistillerparams" -f input.ps -sOutputFile=out.pdf
```

### Color Management

```bash
# Convert to specific color space
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -c "<< /ColorConversionStrategy /RGB >> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf

# Strategies:
#   /LeaveColorUnchanged — keep source color spaces
#   /CMYK               — convert to CMYK
#   /Gray               — convert to grayscale
#   /RGB                — convert to RGB

# With ICC profile
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputProfile=sRGB.icc \
   -c "<< /ColorConversionStrategy /RGB >> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf
```

### N-Up Imposition

```bash
# 2x2 imposition
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -c "[/PerPage << /NumPagesAcross 2 /NumPagesDown 2 >> /setpagedevice pdfmark]" \
   -f input.pdf -sOutputFile=imposed.pdf

# 4x2 imposition with landscape
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -c "[/PerPage << /NumPagesAcross 4 /NumPagesDown 2 /Landscape true >> /setpagedevice pdfmark]" \
   -f input.pdf -sOutputFile=imposed.pdf
```

### Booklet Mode

```bash
# Saddle-stitch booklet
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -c "[/Duplex /DuplexFlipShortEdge /PageSize [612 792] >> /setpagedevice pdfmark]" \
   -f input.pdf -sOutputFile=booklet.pdf
```

### Linearization (Web Optimization)

```bash
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -c "<< /Linearize true >> setdistillerparams" \
   -f input.pdf -sOutputFile=web.pdf
```

### PDF/X Output

```bash
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -dPDFX=true \
   -sOutputProfile=CoatedFOGRA39.icc \
   -c "<< /ColorConversionStrategy /CMYK >> setdistillerparams" \
   -f input.ps -sOutputFile=pdfx.pdf
```

### PDF/A Output

```bash
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -dPDFA=true \
   -dPDFAPart=2 \
   -dPDFAUsage=true \
   -sOutputProfile=sRGB.icc \
   -c "<< /ColorConversionStrategy /RGB >> setdistillerparams" \
   -f input.ps -sOutputFile=pdfa.pdf
```

### Password Protection

```bash
# Add user password
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -c "<<
     /UserPassword (userpass) def
     /OwnerPassword (ownerpass) def
     /DoEncrypt true
   >> setdistillerparams" \
   -f input.ps -sOutputFile=encrypted.pdf

# Read password-protected PDF
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sPDFPassword=secret \
   -sOutputFile=out.pdf input.pdf
```

### Page Selection and Ordering

```bash
# Extract pages 5-10
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -dFirstPage=5 -dLastPage=10 \
   -sOutputFile=pages5-10.pdf input.pdf

# Reverse page order (PostScript approach)
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -c "{ counttomark {pop} repeat } bind /popall def" \
   -f input.pdf -sOutputFile=reversed.pdf
```

### Convenience Wrappers

| Command | Description |
|---------|-------------|
| `ps2pdf` | PS to PDF (default: PDF 1.4) |
| `ps2pdf14` | PS to PDF 1.4 (Acrobat 5+) |
| `ps2pdf13` | PS to PDF 1.3 (Acrobat 4+) |
| `ps2pdf12` | PS to PDF 1.2 (Acrobat 3+) |
| `pdf2ps` | PDF to PostScript |
| `eps2eps` | EPS to EPS (reprocess) |
| `ps2ps` | PS to PS (level conversion) |
| `ps2ascii` | PS to ASCII-encoded PS |

```bash
# Use wrappers for simple conversions
ps2pdf input.ps output.pdf
ps2pdf14 input.ps output.pdf
pdf2ps input.pdf output.ps
```

### Merging PDFs

Ghostscript doesn't have a built-in merge command, but you can concatenate:

```bash
# Merge multiple PDFs
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=merged.pdf \
   -f part1.pdf part2.pdf part3.pdf
```

### Repairing Corrupt PDFs

```bash
# Reprocess through pdfwrite (can fix structural issues)
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -dPDFSETTINGS=/default \
   -sOutputFile=repaired.pdf corrupt.pdf
```
