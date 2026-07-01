# ImageMagick 7.1.2-26 — CLI Commands

## Table of Contents

- [magick](#magick)
- [convert](#convert)
- [identify](#identify)
- [compare](#compare)
- [composite](#composite)
- [mogrify](#mogrify)
- [montage](#montage)
- [animate](#animate)
- [stream](#stream)
- [conjure](#conjure)
- [import](#import)
- [display](#display)
- [magick-script](#magick-script)

---

## magick

Unified ImageMagick 7 command. Accepts a subcommand or operates as `convert` when no subcommand is given.

```bash
magick [subcommand] [options] input output
magick [options] input output          # defaults to convert behavior
magick --version                       # show version
magick -list type                      # list Color, Configure, Delegate, Format, Magic, Module, Resource, Type
```

Subcommands: `convert`, `identify`, `compare`, `composite`, `mogrify`, `montage`, `animate`, `stream`, `conjure`, `import`, `display`.

---

## convert

Convert between image formats and apply transformations.

```bash
magick convert [input-options] input [output-options] output
```

Reads one or more images, applies operators, writes result. Supports image sequences, parentheses grouping, and stack operations.

Key operators: resize, crop, rotate, blur, sharpen, draw, annotate, composite, morphology, distort, evaluate, fx, quantize, separate, append, flatten, coalesce.

---

## identify

Describe format and characteristics of image files. Read-only.

```bash
magick identify [options] input-file
magick identify -verbose input-file    # full metadata
magick identify -format "%wx%h\n" *.jpg  # formatted output
magick identify -ping input-file        # fast, reads only headers
```

Format specifiers for `-format`: `%w` (width), `%h` (height), `%b` (file size), `%k` (colors), `%m` (format), `%z` (scenes), `%[exif:*]` (EXIF tags), `%[filename]`, `%[datetime]`.

---

## compare

Mathematically and visually compare two images.

```bash
magick compare input1 input2 [options] output-diff
```

Exit codes: `0` = images similar, `0-1` = difference metric, `2` = error.

Metrics: `AE` (absolute error), `FSSIM` (feature similarity), `MAE` (mean absolute), `ME` (mean error), `MSE` (mean squared), `NCC` (normalized cross-correlation, default), `PHASH` (perceptual hash), `RMSE` (root mean squared), `PSNR` (peak signal-to-noise).

```bash
magick compare -metric AE a.png b.png diff.png
magick compare -metric RMSE -fuzz 5% a.png b.png diff.png
magick compare -subimage-search a.png b.png diff.png  # find a within b
```

---

## composite

Overlap one image on another.

```bash
magick composite [options] overlay base [mask] output
```

Uses `-compose` operator (default `Over`). Position controlled by `-geometry` or `-define`.

```bash
magick composite -compose Multiply overlay.png base.png result.png
magick composite -geometry +10+20 logo.png photo.png result.png
magick composite -tile pattern.png base.png result.png
```

---

## mogrify

Like convert but overwrites the original file(s).

```bash
magick mogrify [options] input-files
magick mogrify -format png -resize 800x *.jpg   # convert to PNG, overwrite
magick mogrify -strip -quality 85 *.jpg          # strip metadata, reduce quality
```

Useful for batch processing. Dangerous — always test with convert first.

---

## montage

Create a composite image by tiling thumbnails.

```bash
magick montage input-files [options] output
```

```bash
magick montage *.jpg -tile 4x3 -geometry 200x200+5+5 \
  -border 2 -bordercolor black -label "%f" collage.png
```

Options: `-tile WxH`, `-geometry WxH+dx+dy`, `-frame`, `-border`, `-label`, `-pointsize`, `-font`, `-background`, `-shadow`.

---

## animate

Animate image sequence on X server.

```bash
magick animate [options] input-file
```

X11-dependent. Supports `-delay`, `-display`, `-page`.

---

## stream

Lightweight pixel streaming for large images.

```bash
magick stream [options] input output
```

Reads pixel components row by row without full image caching. Useful for raw pixel data, very large images, or when only certain channels are needed.

```bash
magick stream -size 1920x1080 -separate gray:input.png raw:output.raw
```

---

## conjure

Execute Magick Scripting Language (MSL) scripts.

```bash
magick conjure [options] script.msl
```

MSL is XML-based. Supports read, write, transform, annotate, composite, flood-fill, and more operations.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MRM>
  <read filename="input.png"/>
  <transform scale="0.5"/>
  <write filename="output.png"/>
</MRM>
```

---

## import

Capture X server screen or window.

```bash
magick import [options] output-file
magick import -window root screenshot.png      # full screen
magick import -window 0 window.png             # click to select window
magick import -delay 5 screenshot.png          # wait 5 seconds
```

---

## display

Display image on X server.

```bash
magick display [options] input-file
```

X11-dependent image viewer with annotation tools.

---

## magick-script

Execute Magick Script (SCT) files — a compact scripting format.

```bash
magick magick-script script.sct
```

SCT format provides procedural image processing scripts with variables, loops, and conditionals.
