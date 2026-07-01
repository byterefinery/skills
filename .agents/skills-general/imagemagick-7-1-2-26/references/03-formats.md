# ImageMagick 7.1.2-26 — Supported Formats

## Table of Contents

- [Common Formats](#common-formats)
- [All Coders](#all-coders)
- [Pseudo Formats](#pseudo-formats)
- [Delegate-Dependent Formats](#delegate-dependent-formats)
- [Format Selection](#format-selection)

---

## Common Formats

| Format | Extension | Read | Write | Notes |
|---|---|---|---|---|
| JPEG | `.jpg`, `.jpeg` | ✓ | ✓ | Most common photo format |
| PNG | `.png` | ✓ | ✓ | Lossless, transparency support |
| GIF | `.gif` | ✓ | ✓ | Animation, 256 colors |
| TIFF | `.tiff`, `.tif` | ✓ | ✓ | Lossless, multi-page |
| BMP | `.bmp` | ✓ | ✓ | Windows bitmap |
| WebP | `.webp` | ✓ | ✓ | Modern web format, lossy/lossless |
| SVG | `.svg` | ✓ | ✓ | Vector, requires RSVG delegate |
| PSD | `.psd` | ✓ | ✓ | Photoshop layers |
| PDF | `.pdf` | ✓ | ✓ | Requires Ghostscript delegate |
| ICO | `.ico` | ✓ | ✓ | Windows icon |
| RAW | `.raw` | ✓ | ✓ | Raw camera data (requires RAW delegate) |
| HEIC | `.heic` | ✓ | ✓ | Apple format (requires HEIC delegate) |
| JPEG XL | `.jxl` | ✓ | ✓ | Next-gen format (requires JXL delegate) |
| OpenEXR | `.exr` | ✓ | ✓ | HDR film (requires OpenEXR delegate) |

---

## All Coders

### Always Available (no delegate required)

AAI, ART, ASHLAR, AVS, BAYER, BGR, BMP, BRAILLE, CALS, CAPTION, CIN, CIP, CLIP, CMYK, CUBE, CUT, DCM, DDS, DEBUG, DIB, DNG, DPX, FARBFELD, FAX, FITS, FL32, FTXT, GIF, GRADIENT, GRAY, HALD, HDR, HISTOGRAM, HRZ, HTML, ICON, INFO, INLINE, IPL, JNX, JSON, LABEL, MAC, MAGICK, MAP, MASK, MAT, MATTE, META, MIFF, MONO, MPC, MPR, MSL, MTV, MVG, NULL, ORA, OTB, PALM, PATTERN, PCD, PCL, PCX, PDB, PES, PGX, PICT, PIX, PLASMA, PNM, PS, PS2, PS3, PSD, PWP, QOI, RAW, RGB, RGF, RLA, RLE, SCR, SCREENSHOT, SCT, SF3, SFW, SGI, SIXEL, STEGANO, STRIMG, SUN, SVG, TGA, THUMBNAIL, TILE, TIM, TIM2, TTF, TXT, UIL, URL, UYVY, VICAR, VID, VIDEO, VIFF, VIPS, WBMP, WPG, XBM, XC, XCF, XPM, XPS, YCBCR, YUV

### Delegate-Dependent

| Coder | Delegate(s) |
|---|---|
| CLIPBOARD | Windows (MAGICKCORE_WINGDI32) |
| DJVU | djvu library |
| DOT | Graphviz (gvc) |
| DPS | DPS delegate |
| EMF | Windows (MAGICKCORE_WINGDI32) |
| EPT | TIFF delegate |
| EXR | OpenEXR |
| FLIF | FLIF library |
| FPX | FlashPIX |
| HEIC | HEIC library |
| JBIG | JBIG library |
| JP2 | JP2 or OpenJP2 |
| JPEG | JPEG library |
| JXL | JPEG XL library |
| PNG | PNG library |
| TIFF | TIFF library |
| UHDR | UHDR library |
| WEBP | WebP library |
| WMF | WMF or WMFlite |
| X | X11 |
| XWD | X11 |

---

## Pseudo Formats

These generate or consume special data rather than image files.

| Format | Description |
|---|---|
| `caption:` | Render text as image |
| `label:` | Simple text label |
| `gradient:` | Color gradient image |
| `plasma:` | Plasma fractal |
| `pattern:` | Named pattern |
| `tile:` | Tiled image |
| `xc:` | Solid color (e.g., `xc:white 200x100`) |
| `xc:` | Single pixel color |
| `rgb:` | Raw RGB data |
| `bgr:` | Raw BGR data |
| `gray:` | Raw grayscale data |
| `rgba:` | Raw RGBA data |
| `cmyk:` | Raw CMYK data |
| `yuv:` | Raw YUV data |
| `ycbcr:` | Raw YCbCr data |
| `null:` | Null (discard) output |
| `mvg:` | Magick Vector Graphics |
| `mpr:` | Memory pre-register (shared memory) |
| `mpc:` | Memory pre-cache |
| `msl:` | Magick Scripting Language |
| `url:` | URL reference |
| `inline:` | Base64-encoded image |
| `json:` | JSON metadata |
| `yaml:` | YAML metadata |
| `info:` | Text info output |
| `debug:` | Debug output |
| `histogram:` | Histogram image |
| `mask:` | Mask image |
| `matte:` | Matte channel |
| `meta:` | Metadata image |
| `otb:` | OpenType bitmap |
| `sct:` | Magick Script |
| `tim:` | TIM image |
| `tim2:` | TIM2 image |
| `vid:` | Video frame |
| `video:` | Video sequence |
| `viff:` | VIFF format |
| `vips:` | VIPS format |

---

## Delegate-Dependent Formats

Formats that require external libraries (delegates) to be built. Common delegates:

| Delegate | Purpose |
|---|---|
| `JPEG` | JPEG read/write |
| `PNG` | PNG read/write |
| `TIFF` | TIFF read/write |
| `WEBP` | WebP read/write |
| `Ghostscript` | PDF, EPS, PS processing |
| `FreeType` | Font rendering |
| `FontConfig` | Font discovery |
| `Pango` | Complex text layout |
| `RAQM` | Arabic/complex script shaping |
| `LCMS` | ICC color management |
| `OpenEXR` | EXR HDR format |
| `HEIC` | HEIC/HEIF format |
| `JXL` | JPEG XL format |
| `OpenJP2` | JPEG 2000 |
| `RSVG` | SVG rendering |
| `ZLIB` | Deflate compression |
| `ZSTD` | Zstandard compression |
| `BZLIB` | BZIP2 compression |
| `LZMA` | LZMA compression |
| `XML` | XML parsing |
| `FFTW` | Fast Fourier transform |
| `DJVU` | DjVu format |
| `FLIF` | Free Lossless Image Format |
| `RAW` | Camera RAW (dcraw) |
| `WMF` | Windows Metafile |
| `X11` | X11 display/screen capture |

Check available delegates: `magick identify -list delegate`

---

## Format Selection

Force a specific format by prefixing the filename:

```bash
magick convert input.png png32:output.png     # PNG with 32-bit
magick convert input.png jpeg:output.jpg      # JPEG
magick convert input.png pdf:- > output.pdf   # PDF to stdout
magick convert input.png svg:output.svg       # SVG vector
magick convert input.png json:-               # JSON metadata to stdout
```

Or by extension:

```bash
magick convert input.png output.jpg           # auto-detect from .jpg
magick convert input.jpg output.png            # auto-detect from .png
```

For stdin/stdout, use format prefix or `-`:

```bash
magick convert input.png - > output.jpg       # stdout
magick convert png:- output.jpg < input.png   # stdin
```
