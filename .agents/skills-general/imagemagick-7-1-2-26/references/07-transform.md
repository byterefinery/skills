# ImageMagick 7.1.2-26 — Resize, Distort, Geometry, Transforms

## Table of Contents

- [Resize Operations](#resize-operations)
- [Geometry Syntax](#geometry-syntax)
- [Distortion Methods](#distortion-methods)
- [Sparse Color](#sparse-color)
- [Rotation and Flip](#rotation-and-flip)
- [Crop and Extract](#crop-and-extract)
- [Affine Transform](#affine-transform)

---

## Resize Operations

### `-resize`

General-purpose resize with filtering. Best quality for most cases.

```bash
magick convert input.jpg -resize 800x600 output.jpg          # fit within 800x600
magick convert input.jpg -resize 800x600\> output.jpg        # only shrink
magick convert input.jpg -resize 800x600\! output.jpg        # force exact (distorts)
magick convert input.jpg -resize 50% output.jpg              # half size
magick convert input.jpg -resize 200x output.jpg             # width 200, height auto
magick convert input.jpg -resize x300 output.jpg             # height 300, width auto
magick convert input.jpg -resize 800x600^ -gravity Center -crop 800x600+0+0 +repage output.jpg  # fill and crop
```

### `-sample`

Nearest-neighbor scaling. Fastest, lowest quality. Good for pixel art or integer scaling.

```bash
magick convert input.png -sample 200% output.png  # 2x nearest-neighbor
```

### `-scale`

Point sampling. Medium quality, faster than resize.

```bash
magick convert input.jpg -scale 50% output.jpg
```

### `-thumbnail`

Resize for thumbnails. Optimized for small output. Combines resize + quality reduction.

```bash
magick convert input.jpg -thumbnail 150x150 thumb.jpg
```

### `-interpolative-resize`

Resize using interpolation (similar to resize but with different algorithm).

```bash
magick convert input.jpg -interpolative-resize 800x600 output.jpg
```

### `-adaptive-resize`

Data-dependent triangulation resize. Preserves features better than uniform resize.

```bash
magick convert input.jpg -adaptive-resize 50% output.jpg
```

### `-liquid-rescale`

Seam-carving content-aware resize. Preserves important content while changing dimensions.

```bash
magick convert input.jpg -liquid-rescale 400x300 output.jpg
```

### Resample (DPI Change)

```bash
# Change resolution without changing pixel dimensions
magick convert input.jpg -resample 300 output.jpg

# Change resolution and pixel dimensions
magick convert input.jpg -resample 300x300 output.jpg
```

### Filter Types

Set with `-filter type`. Common choices:

| Filter | Use Case |
|---|---|
| `Lanczos` | Default, high quality |
| `Spline` | Smooth, slightly softer |
| `RobidouxSharp` | Sharp, good for photos |
| `Mitchell` | Balanced |
| `Catrom` | Slightly sharp |
| `Blackman` | Smooth |
| `Bessel` | Very smooth |
| `Sinc` | Sharp, may ring |
| `Point` | Nearest neighbor (same as -sample) |
| `Box` | Box filter |
| `Triangle` | Linear interpolation |

```bash
magick convert input.jpg -filter Lanczos -resize 50% output.jpg
magick convert input.png -filter Point -resize 200% output.png  # pixel art
```

---

## Geometry Syntax

```
WxH              # Target width x height (maintain aspect ratio)
WxH+X+Y          # With offset (for crop/position)
WxH-X-Y          # Negative offset
WxH%              # Percentage of original
WxH\>             # Only shrink if larger
WxH\<             # Only enlarge if smaller
WxH\!             # Ignore aspect ratio (force exact)
WxH^              # Fit within, may extend beyond (for crop)
```

---

## Distortion Methods

Applied via `-distort method args`. Args are coordinate mappings.

| Method | Description |
|---|---|
| `Undefined` | No distortion |
| `Affine` | 2-point affine transform (6 args) |
| `AffineProjection` | Affine with projection |
| `ScaleRotateTranslate` | Scale, rotate, translate (6 args) |
| `Perspective` | 4-point perspective (8 args) |
| `PerspectiveProjection` | Perspective with projection |
| `BilinearForward` | Bilinear forward mapping |
| `Bilinear` | Bilinear (alias for forward) |
| `BilinearReverse` | Bilinear reverse mapping |
| `Polynomial` | Polynomial distortion |
| `Arc` | Arc distortion |
| `Polar` | Cartesian to polar |
| `DePolar` | Polar to Cartesian |
| `Cylinder2Plane` | Cylinder to plane (unwrap) |
| `Plane2Cylinder` | Plane to cylinder (wrap) |
| `Barrel` | Barrel distortion |
| `BarrelInverse` | Inverse barrel (pincushion) |
| `Shepards` | Shepard's method |
| `Resize` | Resize via distortion |
| `RigidAffine` | Rigid affine (rotation + translation only) |

### Examples

```bash
# Perspective transform (4 corner points)
magick convert input.jpg \
  -distort Perspective '0,0,10,10 640,0,630,10 640,480,630,470 0,480,10,470' \
  output.jpg

# Polar coordinates
magick convert input.jpg -distort Polar "640,480,320,240" output.jpg

# Barrel distortion
magick convert input.jpg -distort Barrel "0.3,0,320,240" output.jpg

# Cylinder unwrap
magick convert panorama.jpg -distort Cylinder2Plane "640,0,0,320" output.jpg
```

---

## Sparse Color

Fill image based on a few color points. `-sparse-color method args`.

| Method | Description |
|---|---|
| `Barycentric` | Barycentric interpolation |
| `Bilinear` | Bilinear interpolation |
| `Polynomial` | Polynomial interpolation |
| `Shepards` | Shepard's method |
| `Voronoi` | Voronoi diagram |
| `Inverse` | Inverse distance |
| `Manhattan` | Manhattan distance |

```bash
# Gradient from corners
magick convert -size 400x200 xc:none \
  -sparse-color Bilinear "0,0 white 400,0 red 0,200 blue 400,200 yellow" \
  gradient.png

# Voronoi diagram
magick convert -size 400x400 xc:none \
  -sparse-color Voronoi "100,100 red 300,100 blue 200,300 green" \
  voronoi.png
```

---

## Rotation and Flip

```bash
# Rotate by degrees
magick convert input.jpg -rotate 45 output.jpg

# Flip vertically
magick convert input.jpg -flip output.jpg

# Flip horizontally
magick convert input.jpg -flop output.jpg

# Transpose (flip + rotate 90°)
magick convert input.jpg -transpose output.jpg

# Transverse (flop + rotate 270°)
magick convert input.jpg -transverse output.jpg

# Auto-orient from EXIF
magick convert input.jpg -auto-orient output.jpg

# Shear
magick convert input.jpg -shear 15x5 output.jpg
```

---

## Crop and Extract

```bash
# Crop to region
magick convert input.jpg -crop 200x200+50+50 output.jpg

# Crop and get first tile
magick convert input.jpg -crop 200x200+50+50[0] output.jpg

# Extract region
magick convert input.jpg -extract 200x200+50+50 output.jpg

# Trim edges (remove uniform border)
magick convert input.png -trim output.png

# Trim with fuzz
magick convert input.png -fuzz 5% -trim output.png

# Extend (pad to larger size)
magick convert input.jpg -extent 800x600 output.jpg

# Extend with gravity
magick convert input.jpg -gravity Center -extent 800x600 output.jpg

# Shave (remove from edges)
magick convert input.jpg -shave 10x10 output.jpg

# Chop (remove from interior)
magick convert input.jpg -chop 10x10+50+50 output.jpg

# Splice (insert background)
magick convert input.jpg -splice 10x0+0+100 output.jpg
```

### Don't Forget `+repage`

After crop/trim/extent, the virtual canvas offset remains. Reset it:

```bash
magick convert input.jpg -crop 200x200+0+0 +repage output.jpg
```

---

## Affine Transform

```bash
# Affine matrix (6 values: scaleX, skewY, skewX, scaleY, tx, ty)
magick convert input.jpg -affine "1,0.2,0,1,0,0" output.jpg

# Transform (applies current affine matrix)
magick convert input.jpg -affine "1,0.2,0,1,0,0" -transform output.jpg

# Rotate via affine
magick convert input.jpg -affine "0.707,0.707,-0.707,0.707,0,0" output.jpg
```
