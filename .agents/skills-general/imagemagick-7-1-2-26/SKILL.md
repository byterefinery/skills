---
name: imagemagick-7-1-2-26
description: ImageMagick 7.1.2-26 — create, edit, compose, convert, and analyze bitmap images. Covers all CLI commands (magick, convert, identify, compare, composite, mogrify, montage, animate, stream, conjure, import, display), 200+ format coders, colorspaces, morphology, drawing, distortions, compositing operators, security policies, and MagickWand/MagickCore/Magick++ APIs. Use for image processing tasks, format conversion, batch operations, and programmatic image manipulation.
metadata:
  tags:
    - image-processing
    - graphics
    - cli
---

# imagemagick 7.1.2.26

## Overview

ImageMagick is a free, open-source suite for creating, editing, composing, and converting bitmap images. Version 7 uses the unified `magick` command (with legacy aliases like `convert`, `identify`, `mogrify`). It supports 200+ formats, HDRI (high dynamic range), Q8/Q16/Q32 quantum depths, multispectral imagery up to 64 channels, and provides C/C++ APIs (MagickCore, MagickWand, Magick++).

Key capabilities: format conversion, resize/transform, color management, compositing, drawing/annotation, morphology, Fourier transforms, perceptual hashing, batch processing, and scripting via MSL (Magick Scripting Language).

## Usage

### Primary Command

```bash
# Unified magick command (IM7)
magick convert input.png -resize 800x output.jpg
magick identify image.png
magick compare a.png b.png diff.png
magick composite overlay.png base.png result.png
magick mogrify -resize 50% *.png
magick montage *.jpg -tile 4x -geometry 200x200 collage.png
```

### Legacy Aliases (still available)

- `convert` — format conversion and image manipulation
- `identify` — read-only image inspection
- `compare` — mathematical and visual image comparison
- `composite` — overlay one image on another
- `mogrify` — like convert but overwrites input files
- `montage` — tile thumbnails onto a canvas
- `animate` — play image sequences on X server
- `stream` — lightweight pixel streaming for large images
- `conjure` — execute MSL scripts
- `import` — capture X server screen/window
- `display` — view images on X server

### Quick Patterns

```bash
# Resize maintaining aspect ratio
magick convert input.jpg -resize 800x600\> output.jpg

# Resize only if larger (the \> flag)
magick convert input.jpg -resize 800x800\> output.jpg

# Resize only if smaller (the \< flag)
magick convert input.jpg -resize 100x100\< output.jpg

# Crop center
magick convert input.jpg -gravity Center -crop 400x400+0+0 +repage output.jpg

# Add text watermark
magick convert input.jpg -gravity SouthEast -fill white -pointsize 24 \
  -annotate +10+10 "© 2024" output.jpg

# Create thumbnail with quality
magick convert input.jpg -thumbnail 150x150 -quality 85 thumb.jpg

# Batch convert
magick mogrify -format png -resize 1024x1024\> *.jpg

# GIF animation
magick convert -delay 10 -loop 0 frame*.png animation.gif

# Composite with transparency
magick convert logo.png -background none -compose Over -composite base.jpg result.jpg

# Identify with verbose info
magick identify -verbose image.png

# Format-specific output
magick convert input.png png32:output.png
magick convert input.png pdf:- > output.pdf
```

### Parentheses for Selective Operations

Options between `( )` apply only to the images in that group:

```bash
magick convert \
  input1.png \
  \( input2.png -resize 50% \) \
  +append output.png
```

### Standard I/O

Use `-` for stdin/stdout:

```bash
magick convert - resize 50% - output.png < input.png
curl image.png | magick convert - -resize 50% - > output.png
```

## Gotchas

- **IM7 vs IM6 commands**: In ImageMagick 7, the unified `magick` command replaces legacy commands. `convert` still works but is actually `magick convert`. Use `magick` as the primary entry point.
- **Input vs output options**: Options placed before the input filename are input options; options after are output options. Only certain settings (density, define, font, pointsize, size, texture, antialias, caption, encoding) are valid as input options. Misplaced options silently apply to wrong images.
- **The `+repage` operator**: After crop, extent, or trim operations, the virtual canvas offset remains. Use `+repage` to reset it, otherwise subsequent compositing or appending will place the image at the wrong offset.
- **Geometry flags**: `800x600` (exact), `800x600\>` (only shrink), `800x600\<` (only enlarge), `800x600\!` (ignore aspect ratio), `800x600^` (fit within, may crop), `%` suffix for percentages like `200%`.
- **`-resize` vs `-sample` vs `-scale`**: `-resize` uses filtering (slower, higher quality). `-sample` uses nearest-neighbor (fast, blocky). `-scale` uses point sampling (medium quality). Use `-resize` for most cases.
- **`-quality` is write-time only**: The `-quality` option only affects output encoding. It is not stored as metadata and does not affect intermediate processing.
- **GIF animations**: Use `-delay` (centiseconds) and `-loop 0` for infinite loop. Always use `-coalesce` before editing animated GIFs to normalize frame offsets.
- **PDF processing requires Ghostscript**: Reading/writing PDFs depends on the Ghostscript delegate. Check with `magick identify -list delegate`. Policy may restrict PDF coders.
- **Security policy (policy.xml)**: Controls which coders, delegates, and paths are allowed. Web deployments should use websafe or secure policy. PDF, MSL, SVG, and URL coders are often restricted. Check restrictions with `magick identify -list policy`.
- **Quantum depth matters**: Q16 (default) gives 16-bit precision per channel. Q8 uses half the memory. Q32 gives 32-bit. HDRI mode uses floating point. Build configuration affects available precision.
- **`-channel` scoping**: `-channel RGB` applies subsequent operators only to specified channels. Reset with `-channel Reset` or use `-channel All`.
- **`-fuzz` for color matching**: Use `-fuzz 10%` before `-transparent` or `-opaque` to match similar colors within a tolerance.
- **Memory limits**: Large images or sequences can hit resource limits. Check with `magick identify -list resource`. Override with `-limit memory 2GiB -limit disk 10GiB`.
- **`-define` is format-specific**: Options like `-define jpeg:extent=500KB` or `-define png:compression-level=9` control encoder behavior. Format names vary (jpeg, png, webp, tiff, gif).
- **`-strip` removes all metadata**: Including EXIF, ICC profiles, and color profiles. Use before distribution to reduce file size and remove privacy data.
- **Color names vs hex**: ImageMagick accepts named colors (e.g., `white`, `transparent`), hex (`#FFFFFF`), RGB (`rgb(255,255,255)`), HSL, and CMYK formats.
- **`-auto-orient` reads EXIF**: Use to correct image orientation from camera EXIF data. Without it, images may appear rotated.
- **`-density` for PDF/SVG rendering**: Set before reading vector formats. `-density 300` gives 300 DPI rasterization.

## References

- [01-commands](references/01-commands.md) — All CLI commands with syntax and descriptions
- [02-options](references/02-options.md) — Image settings and operators reference
- [03-formats](references/03-formats.md) — Supported image formats and coders
- [04-colorspaces](references/04-colorspaces.md) — Colorspaces, composite operators, channel operations
- [05-draw](references/05-draw.md) — Drawing primitives, text annotation, fonts
- [06-morphology](references/06-morphology.md) — Morphology methods and kernel types
- [07-transform](references/07-transform.md) — Resize, distort, geometry, and transforms
- [08-effects](references/08-effects.md) — Visual effects, filters, and image enhancements
- [09-apis](references/09-apis.md) — MagickWand, MagickCore, and Magick++ APIs
- [10-security](references/10-security.md) — Security policies, delegates, and configuration
