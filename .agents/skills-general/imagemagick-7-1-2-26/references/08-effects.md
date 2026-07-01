# ImageMagick 7.1.2-26 — Visual Effects and Filters

## Table of Contents

- [Blur Effects](#blur-effects)
- [Sharpen Effects](#sharpen-effects)
- [Artistic Effects](#artistic-effects)
- [Noise](#noise)
- [Color Adjustments](#color-adjustments)
- [Threshold and Quantization](#threshold-and-quantization)
- [Fourier Transform](#fourier-transform)
- [Image Evaluation](#image-evaluation)
- [Fx Expressions](#fx-expressions)
- [Region Operations](#region-operations)

---

## Blur Effects

```bash
# Standard blur
magick convert input.jpg -blur 0x5 output.jpg

# Adaptive blur (less near edges)
magick convert input.jpg -adaptive-blur 0x5 output.jpg

# Gaussian blur
magick convert input.jpg -gaussian-blur 0x5 output.jpg

# Selective blur (within contrast threshold)
magick convert input.jpg -selective-blur 0x5 output.jpg

# Bilateral blur (edge-preserving)
magick convert input.jpg -bilateral-blur 0x5 output.jpg

# Motion blur
magick convert input.jpg -motion-blur 0x5 output.jpg

# Radial blur
magick convert input.jpg -radial-blur 45 output.jpg
```

Geometry for blur: `radiusxsigma`. Radius 0 lets ImageMagick choose.

---

## Sharpen Effects

```bash
# Standard sharpen
magick convert input.jpg -sharpen 0x5 output.jpg

# Adaptive sharpen (more near edges)
magick convert input.jpg -adaptive-sharpen 0x5 output.jpg

# Unsharp mask
magick convert input.jpg -unsharp 0x5 output.jpg
```

---

## Artistic Effects

```bash
# Charcoal drawing
magick convert input.jpg -charcoal 2 output.jpg

# Oil painting
magick convert input.jpg -paint 3 output.jpg

# Pencil sketch
magick convert input.jpg -sketch 0x1 output.jpg

# Emboss
magick convert input.jpg -emboss 3 output.jpg

# Edge detection
magick convert input.jpg -edge 3 output.jpg

# Canny edge detection
magick convert input.jpg -canny 0x1 output.jpg

# Implosion
magick convert input.jpg -implode 0.5 output.jpg

# Swirl
magick convert input.jpg -swirl 45 output.jpg

# Wave
magick convert input.jpg -wave 15x26 output.jpg

# Vignette
magick convert input.jpg -vignette 0x0 output.jpg

# Shadow
magick convert input.jpg -shadow 60x4+6+6 output.jpg

# 3D raise
magick convert input.jpg -raise 5x5 output.jpg

# Polaroid
magick convert input.jpg -polaroid 5 output.jpg

# Sepia tone
magick convert input.jpg -sepia-tone 50% output.jpg

# Blue shift (nighttime)
magick convert input.jpg -blue-shift 0.5 output.jpg

# Solarize
magick convert input.jpg -solarize 50% output.jpg

# Negate
magick convert input.jpg -negate output.jpg

# Monochrome
magick convert input.jpg -monochrome output.jpg

# Grayscale
magick convert input.jpg -grayscale output.jpg

# Colorize
magick convert input.jpg -fill red -colorize 50% output.jpg

# Tint
magick convert input.jpg -fill blue -tint 50% output.jpg

# Modulate (brightness, saturation, hue)
magick convert input.jpg -modulate 120,80,10 output.jpg

# Posterize
magick convert input.jpg -posterize 4 output.jpg

# Ordered dither
magick convert input.jpg -ordered-dither o2x2 output.jpg
```

---

## Noise

### Add Noise

```bash
magick convert input.jpg -noise 5% Gaussian output.jpg
```

Noise types: `Gaussian`, `Poisson`, `Impulse`, `Clip`, `MultiplicativeImpulse`, `Uniform`, `Random`, `HighPass`, `HighPassIM`, `Gradient`, `Laplacian`, `PM`, `FF`.

### Reduce Noise

```bash
# Despeckle
magick convert input.jpg -despeckle output.jpg

# Median filter
magick convert input.jpg -median 3x3 output.jpg

# Wavelet denoise
magick convert input.jpg -wavelet-denoise 0.5x0.5 output.jpg

# Enhance (noise reduction)
magick convert input.jpg -enhance output.jpg
```

---

## Color Adjustments

```bash
# Gamma correction
magick convert input.jpg -gamma 1.5 output.jpg

# Auto gamma
magick convert input.jpg -auto-gamma output.jpg

# Auto level
magick convert input.jpg -auto-level output.jpg

# Auto white balance
magick convert input.jpg -white-balance output.jpg

# Normalize (full range)
magick convert input.jpg -normalize output.jpg

# Level adjustment
magick convert input.jpg -level 0%,50%,100% output.jpg

# Level with colors
magick convert input.jpg -level-colors black,white output.jpg

# Contrast
magick convert input.jpg -contrast output.jpg
magick convert input.jpg +contrast output.jpg  # reduce

# Contrast stretch
magick convert input.jpg -contrast-stretch 0%x0% output.jpg

# Linear stretch (with saturation)
magick convert input.jpg -linear-stretch 0%x0% output.jpg

# Brightness/contrast
magick convert input.jpg -brightness-contrast 20x10 output.jpg

# Histogram equalization
magick convert input.jpg -equalize output.jpg

# CLAHE (contrast-limited adaptive histogram equalization)
magick convert input.jpg -clahe 2x2 output.jpg

# Sigmoidal contrast
magick convert input.jpg -sigmoidal-contrast 10x50% output.jpg

# Color matrix (3x3 or 4x4)
magick convert input.jpg \
  -color-matrix "1.2,0,0,0,0 0,1.2,0,0,0 0,0,1.2,0,0 0,0,0,1,0 0,0,0,0,1" \
  output.jpg

# Cycle colormap
magick convert input.jpg -cycle 50% output.jpg

# Desaturate to grayscale method
magick convert input.jpg -grayscale average output.jpg
```

Grayscale methods: `Average`, `Lightness`, `Luminosity`, `Saturation`.

---

## Threshold and Quantization

```bash
# Simple threshold
magick convert input.jpg -threshold 50% output.jpg

# Auto threshold
magick convert input.jpg -auto-threshold Otsu output.jpg

# Black threshold (below → black)
magick convert input.jpg -black-threshold 20% output.jpg

# White threshold (above → white)
magick convert input.jpg -white-threshold 80% output.jpg

# Random threshold
magick convert input.jpg -random-threshold 20%,80% output.jpg

# Range threshold
magick convert input.jpg -range-threshold 0.5,0.8,0.5 output.jpg

# Color threshold
magick convert input.jpg -color-threshold red-blue output.jpg

# Local adaptive threshold
magick convert input.jpg -lat 3x3+1 output.jpg

# Quantize (reduce colors)
magick convert input.jpg -quantize colors 64 output.jpg
magick convert input.jpg -quantize sRGB -colors 256 -dither FloydSteinberg output.gif
```

---

## Fourier Transform

```bash
# Forward DFT
magick convert input.jpg -fft dft.png

# Inverse DFT
magick convert dft.png -ift result.jpg

# Frequency domain filtering
magick convert input.jpg -fft \
  \( +clone -fx "exp(-0.0001*(u-320)^2-v-240)^2)" -compose Multiply -composite \) \
  -ift filtered.jpg
```

---

## Image Evaluation

```bash
# Arithmetic operations
magick convert input.jpg -evaluate Multiply 1.5 output.jpg
magick convert input.jpg -evaluate Add 20 output.jpg
magick convert input.jpg -evaluate Divide 2 output.jpg
magick convert input.jpg -evaluate Subtract 10 output.jpg
magick convert input.jpg -evaluate Exponentiate 1.5 output.jpg
magick convert input.jpg -evaluate Cos output.jpg
magick convert input.jpg -evaluate Sin output.jpg

# Logical operations
magick convert input.jpg -evaluate And 0xFF output.jpg
magick convert input.jpg -evaluate Or 0x0F output.jpg
magick convert input.jpg -evaluate Xor 0xFF output.jpg
magick convert input.jpg -evaluate LeftShift 2 output.jpg
magick convert input.jpg -evaluate RightShift 2 output.jpg

# Sequence operations
magick convert a.png b.png -evaluate-sequence Add sum.png
magick convert a.png b.png -evaluate-sequence Subtract diff.png
magick convert a.png b.png -evaluate-sequence Mean average.png
magick convert a.png b.png -evaluate-sequence Min minimum.png
magick convert a.png b.png -evaluate-sequence Max maximum.png
```

Operators: `Add`, `Subtract`, `Multiply`, `Divide`, `Modulus`, `Fmod`, `Exponentiate`, `Animate`, `Cosine`, `Sine`, `Tangent`, `ArcCosine`, `ArcSine`, `ArcTangent`, `Threshold`, `ThresholdIntensity`, `GaussianBlur`, `Log`, `Argument`, `Abs`, `Exp`, `Pow`, `Sqrt`, `Reciprocal`, `Conjugate`, `Real`, `Imaginary`, `Cascade`, `CascadeAdd`, `CascadeMultiply`, `Hashtag`, `And`, `Or`, `Xor`, `LeftShift`, `RightShift`, `And`, `Nand`, `Nor`, `Xnor`, `Not`.

---

## Fx Expressions

`-fx` applies mathematical expressions to image channels.

```bash
# Brighten
magick convert input.jpg -fx "i + 0.2" output.jpg

# Invert
magick convert input.jpg -fx "1 - i" output.jpg

# Channel swap (R↔B)
magick convert input.jpg -fx "b.g.a" output.jpg

# Desaturate
magick convert input.jpg -fx "(r+g+b)/3" output.jpg

# Edge detection (Sobel-like)
magick convert input.jpg -fx "sqrt((r-g)^2 + (g-b)^2)" output.jpg

# Per-channel expression
magick convert input.jpg -fx "r*1.2,g*0.8,b*1.0" output.jpg
```

Variables: `i` (current pixel), `r`, `g`, `b`, `a` (channels), `u`, `v` (coordinates), `w`, `h` (width/height), `o` (previous pixel in sequence).

---

## Region Operations

Apply options to a portion of the image:

```bash
# Apply blur to a region
magick convert input.jpg \
  -region 200x200+100+100 -blur 0x5 output.jpg

# Apply multiple regions
magick convert input.jpg \
  -region 100x100+0+0 -brightness-contrast 20x10 \
  -region 100x100+200+0 -brightness-contrast -20x-10 \
  output.jpg

# Region with complex operations
magick convert input.jpg \
  \( -region 200x200+0+0 -blur 0x5 \) \
  output.jpg
```
