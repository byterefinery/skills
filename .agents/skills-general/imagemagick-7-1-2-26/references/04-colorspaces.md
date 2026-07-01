# ImageMagick 7.1.2-26 — Colorspaces, Compositing, Channels

## Table of Contents

- [Colorspaces](#colorspaces)
- [Composite Operators](#composite-operators)
- [Channel Operations](#channel-operations)
- [Alpha Channel](#alpha-channel)
- [Color Syntax](#color-syntax)

---

## Colorspaces

Set with `-colorspace type`. Conversion is lossy in some directions.

| Colorspace | Description |
|---|---|
| `sRGB` | Default: non-linear sRGB |
| `RGB` | Linear RGB |
| `GRAY` | Single-channel grayscale (non-linear) |
| `LinearGRAY` | Single-channel grayscale (linear) |
| `CMYK` | CMY with black separation |
| `CMY` | Negated linear RGB |
| `HSV` | Hue, Saturation, Value (alias for HSB) |
| `HSB` | Hue, Saturation, Brightness |
| `HSL` | Hue, Saturation, Lightness |
| `HSI` | Hue, Saturation, Intensity |
| `HWB` | Hue, Whiteness, Blackness |
| `Lab` | CIE L*a*b* |
| `LCHab` | Cylindrical (polar) Lab |
| `Luv` | CIE L*u*v* |
| `LCHuv` | Cylindrical (polar) Luv (alias: LCH) |
| `HCL` | Cylindrical Lab (different from LCHab) |
| `HCLp` | Cylindrical Lab with polar coordinates |
| `XYZ` | CIE XYZ (IEEE color reference) |
| `YCbCr` | Y with blue and red chroma |
| `Rec601YCbCr` | ITU-R BT.601 YCbCr |
| `Rec709YCbCr` | ITU-R BT.709 YCbCr |
| `YCC` | Y with chroma components |
| `YDbDr` | YDbDr color difference |
| `YIQ` | NTSC color space |
| `YPbPr` | Component video |
| `YUV` | Luma-chroma |
| `LMS` | LMS color space |
| `OHTA` | OHTA color space |
| `Log` | Log color space |
| `scRGB` | ScRGB |
| `xyY` | CIE xyY |
| `Transparent` | Transparent colorspace |
| `Jzazbz` | ICtCp-related |
| `DisplayP3` | Apple Display P3 |
| `Adobe98` | Adobe RGB (1998) |
| `ProPhoto` | ProPhoto RGB |
| `Oklab` | Oklab perceptual colorspace |
| `Oklch` | Oklch (cylindrical Oklab) |
| `CAT02LMS` | CAT02 LMS |

```bash
# Convert to grayscale
magick convert input.jpg -colorspace Gray output.png

# Convert to Lab for perceptual editing
magick convert input.jpg -colorspace Lab -channel a -negate -colorspace sRGB output.jpg

# CMYK for print
magick convert input.jpg -colorspace CMYK output.tif

# Display P3 for wide gamut
magick convert input.jpg -colorspace DisplayP3 output.png
```

---

## Composite Operators

Set with `-compose operator`. Used by `-composite`, `composite`, and within `-draw`.

### Standard Porter-Duff

| Operator | Description |
|---|---|
| `Over` | Source over destination (default) |
| `In` | Source clipped to destination |
| `Out` | Source outside destination |
| `Atop` | Source over, clipped to source alpha |
| `DstOver` | Destination over source |
| `DstIn` | Destination clipped to source |
| `DstOut` | Destination outside source |
| `DstAtop` | Destination over, clipped to dest alpha |
| `Xor` | XOR blend |
| `Plus` | Additive blend |
| `Clear` | Clear destination |
| `Copy` | Replace destination |
| `Replace` | Replace (same as Copy) |
| `Src` | Source only |
| `Dst` | Destination only |
| `NoOp` | No operation |

### Blend Modes

| Operator | Description |
|---|---|
| `Multiply` | Multiply colors (darken) |
| `Screen` | Screen blend (lighten) |
| `Overlay` | Multiply or screen based on base |
| `Darken` | Darker of source/dest |
| `Lighten` | Lighter of source/dest |
| `ColorDodge` | Brighten base by blend |
| `ColorBurn` | Darken base by blend |
| `HardLight` | Overlay with roles reversed |
| `SoftLight` | Subtle overlay |
| `Difference` | Absolute difference |
| `Exclusion` | Inverse difference |
| `LinearDodge` | Additive |
| `LinearBurn` | Subtract |
| `LinearLight` | Linear dodge/burn |
| `VividLight` | Color dodge/burn |
| `PinLight` | Replace darker/lighter |
| `HardMix` | Additive hard mix |
| `PegtopLight` | Pegtop light blend |

### Color/Hue/Saturation

| Operator | Description |
|---|---|
| `Colorize` | Colorize with fill color |
| `Hue` | Take hue from source |
| `Saturation` | Take saturation from source |
| `Luminize` | Take luminance from source |
| `ColorBurn` | Color burn |
| `ColorDodge` | Color dodge |

### Channel-Specific

| Operator | Description |
|---|---|
| `CopyRed` | Copy red channel |
| `CopyGreen` | Copy green channel |
| `CopyBlue` | Copy blue channel |
| `CopyAlpha` | Copy alpha channel |
| `CopyCyan` | Copy cyan channel |
| `CopyMagenta` | Copy magenta channel |
| `CopyYellow` | Copy yellow channel |
| `CopyBlack` | Copy black channel |

### Special

| Operator | Description |
|---|---|
| `Blur` | Blur composite |
| `Bumpmap` | Bump map |
| `Displace` | Displacement map |
| `Dissolve` | Random dissolve |
| `Distort` | Distortion composite |
| `Intensity` | Intensity-based |
| `Mathematics` | Math expression (requires -define) |
| `Modulate` | Modulate blend |
| `ModulusAdd` | Modulo add |
| `ModulusSubtract` | Modulo subtract |
| `Negate` | Negate where overlapping |
| `Saturate` | Saturate blend |
| `Stamp` | Stamp composite |
| `Stereo` | Stereo anaglyph |
| `Freeze` | Freeze composite |
| `Interpolate` | Interpolate composite |
| `Reflect` | Reflect composite |
| `SoftBurn` | Soft burn |
| `SoftDodge` | Soft dodge |
| `SaliencyBlend` | Saliency-based blend |
| `SeamlessBlend` | Seamless blend |
| `Threshold` | Threshold composite |
| `RMSE` | Root mean square error |
| `ChangeMask` | Change alpha mask |
| `DivideDst` | Divide by destination |
| `DivideSrc` | Divide by source |
| `MinusDst` | Minus destination |
| `MinusSrc` | Minus source |
| `DarkenIntensity` | Darken by intensity |
| `LightenIntensity` | Lighten by intensity |

---

## Channel Operations

### Channel Mask

```bash
# Apply operator to specific channels only
magick convert input.jpg -channel R -negate output.jpg

# Multiple channels
magick convert input.jpg -channel RGB -gamma 1.5 output.jpg

# Reset channel mask
magick convert input.jpg -channel Reset output.jpg
```

Channel names: `R`, `G`, `B`, `A`, `C`, `M`, `Y`, `K`, `Opacity`, `All`, `Red`, `Green`, `Blue`, `Alpha`, `Cyan`, `Magenta`, `Yellow`, `Black`, `Index`, `Ignore`.

### Channel Extraction/Separation

```bash
# Extract individual channels as grayscale
magick convert input.jpg -separate channel_r.png channel_g.png channel_b.png

# Extract and recombine
magick convert input.jpg -channel-extract RGB r.png g.png b.png
magick convert r.png g.png b.png -channel-inject RGB output.png

# Swap channels
magick convert input.jpg -channel-swap B,R output.jpg  # swap red and blue
```

---

## Alpha Channel

```bash
# Make a color transparent
magick convert input.jpg -fuzz 10% -transparent white output.png

# Remove alpha (flatten on background)
magick convert input.png -background white -flatten output.jpg

# Activate alpha channel
magick convert input.jpg -alpha on output.png

# Deactivate alpha
magick convert input.png -alpha off output.png

# Set alpha to opaque
magick convert input.png -alpha set output.png

# Extract alpha as grayscale
magick convert input.png -alpha extract alpha.png

# Use alpha as shape
magick convert input.png -alpha shape output.png

# Copy alpha from another image
magick convert input.png mask.png -alpha copy output.png

# Background alpha (replace transparent with background color)
magick convert input.png -alpha background output.png
```

---

## Color Syntax

ImageMagick accepts multiple color formats:

```bash
# Named colors
-fill white
-fill transparent
-fill navy

# Hex
-fill #FFFFFF
-fill #FFF
-fill #RRGGBBAA

# RGB
-fill rgb(255,255,255)
-fill rgb(100%,100%,100%)

# RGBA
-fill rgba(255,255,255,0.5)

# HSL
-fill hsl(0,0%,100%)

# CMYK
-fill cmyk(0%,0%,0%,0%)

# Color with opacity
-fill "white 50%"
-fill "rgba(255,0,0,0.5)"
```

List available color names: `magick convert -list color`
