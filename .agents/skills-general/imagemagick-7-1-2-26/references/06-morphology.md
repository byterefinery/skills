# ImageMagick 7.1.2-26 — Morphology and Kernels

## Table of Contents

- [Morphology Methods](#morphology-methods)
- [Kernel Types](#kernel-types)
- [Custom Kernels](#custom-kernels)
- [Convolution](#convolution)
- [Examples](#examples)

---

## Morphology Methods

Applied via `-morphology method kernel`.

### Convolve / Correlate

| Method | Description |
|---|---|
| `Convolve` | Weighted sum with reflected kernel |
| `Correlate` | Weighted sum using sliding window |

### Low-Level (Structuring Element)

| Method | Description |
|---|---|
| `Erode` | Minimum value in neighborhood |
| `Dilate` | Maximum value in neighborhood |
| `ErodeIntensity` | Pixel pick using grayscale erode |
| `DilateIntensity` | Pixel pick using grayscale dilate |
| `IterativeDistance` | Add kernel value, take minimum |

### Second-Level

| Method | Description |
|---|---|
| `Open` | Dilate then erode (removes small bright features) |
| `Close` | Erode then dilate (fills small dark holes) |
| `OpenIntensity` | Pixel pick using grayscale open |
| `CloseIntensity` | Pixel pick using grayscale close |
| `Smooth` | Open then close (noise removal) |

### Difference Methods

| Method | Description |
|---|---|
| `EdgeIn` | Dilate difference from original (inner edges) |
| `EdgeOut` | Erode difference from original (outer edges) |
| `Edge` | Dilate difference with erode (all edges) |
| `TopHat` | Close difference from original (bright spots) |
| `BottomHat` | Open difference from original (dark spots) |

### Recursive Methods

| Method | Description |
|---|---|
| `HitAndMiss` | Foreground/background pattern matching |
| `Thinning` | Remove matching pixels (skeletonize) |
| `Thicken` | Add matching pixels (bolden) |

### Directly Applied

| Method | Description |
|---|---|
| `Distance` | Add kernel value, take minimum |
| `Voronoi` | Distance matte, copy nearest color |

---

## Kernel Types

Built-in kernels specified by name.

### Gaussian-Based

| Kernel | Description |
|---|---|
| `Gaussian` | Gaussian blur kernel |
| `DoG` | Difference of Gaussians |
| `LoG` | Laplacian of Gaussians |
| `Blur` | Simple blur |
| `Comet` | Comet trail |
| `Binomial` | Binomial distribution |

### Named Convolution Kernels

| Kernel | Description |
|---|---|
| `Laplacian` | Edge detection |
| `Sobel` | Edge detection (gradient) |
| `FreiChen` | Frei-Chen operator |
| `Roberts` | Roberts cross operator |
| `Prewitt` | Prewitt operator |
| `Compass` | Compass gradient |
| `Kirsch` | Kirsch corner detection |

### Shape Kernels

| Kernel | Description |
|---|---|
| `Diamond` | Diamond shape |
| `Square` | Square shape |
| `Rectangle` | Rectangle shape |
| `Octagon` | Octagon shape |
| `Disk` | Disk/circle shape |
| `Plus` | Plus/cross shape |
| `Cross` | Cross shape |
| `Ring` | Ring shape |

### Hit-and-Miss Kernels

| Kernel | Description |
|---|---|
| `Peaks` | Peak detection |
| `Edges` | Edge detection |
| `Corners` | Corner detection |
| `Diagonals` | Diagonal detection |
| `LineEnds` | Line end detection |
| `LineJunctions` | Line junction detection |
| `Ridges` | Ridge detection |
| `ConvexHull` | Convex hull |
| `ThinSE` | Thinning structuring element |
| `Skeleton` | Skeleton extraction |

### Distance Measuring

| Kernel | Description |
|---|---|
| `Chebyshev` | Chebyshev distance |
| `Manhattan` | Manhattan (L1) distance |
| `Octagonal` | Octagonal distance |
| `Euclidean` | Euclidean (L2) distance |

### Special

| Kernel | Description |
|---|---|
| `Unity` | No-op (original image) |
| `UserDefined` | Custom kernel array |

---

## Custom Kernels

Define a custom kernel with a space-separated list of coefficients:

```bash
# 3x3 sharpening kernel
magick convert input.jpg \
  -morphology Convolve "0,-1,0,-1,5,-1,0,-1,0" output.jpg

# 5x5 box blur
magick convert input.jpg \
  -morphology Convolve "1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1" \
  output.jpg

# With explicit size
magick convert input.jpg \
  -morphology Convolve "3x3: 0,-1,0,-1,5,-1,0,-1,0" output.jpg
```

---

## Convolution

`-convolve` applies a kernel directly (simpler syntax than morphology):

```bash
# Edge detection
magick convert input.jpg -convolve "1,1,1,1,-8,1,1,1,1" edges.png

# Sharpening
magick convert input.jpg -convolve "0,-1,0,-1,5,-1,0,-1,0" sharp.png

# Blur
magick convert input.jpg -convolve "1,1,1,1,1,1,1,1,1" blur.png
```

---

## Examples

### Noise Removal

```bash
# Remove salt-and-pepper noise
magick convert noisy.jpg -morphology Open Diamond:1 -morphology Close Diamond:1 clean.jpg

# Smooth with disk kernel
magick convert noisy.jpg -morphology Smooth Disk:2 smooth.jpg
```

### Edge Detection

```bash
# Canny-style edges
magick convert input.jpg -morphology EdgeIn Disk:1 edges.png

# Sobel edges
magick convert input.jpg -morphology Convolve Sobel edges.png
```

### Feature Extraction

```bash
# Corner detection
magick convert input.jpg -morphology HitAndMiss Corners corners.png

# Line detection
magick convert input.jpg -morphology HitAndMiss LineEnds lines.png

# Skeleton (thinning)
magick convert input.jpg -threshold 50% -morphology Thinning Disk skeleton.png
```

### Text Enhancement

```bash
# Thicken text
magick convert text.png -morphology Thicken Disk:1 thick.png

# Thin text
magick convert text.png -morphology Thinning Disk:1 thin.png
```

### Connected Components

```bash
# Label connected regions
magick convert input.png -connected-components 8 labeled.png
```

### Distance Transform

```bash
# Euclidean distance
magick convert input.png -morphology Distance Euclidean distance.png
```

### Voronoi Diagram

```bash
# Voronoi from points
magick convert input.png -morphology Voronoi Disk voronoi.png
```
