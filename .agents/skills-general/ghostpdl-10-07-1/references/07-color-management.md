# Color Management

## Overview

Ghostscript supports ICC-based color management through its color management module. It handles RGB, CMYK, grayscale, and DeviceN color spaces, with ICC profile-based conversion between them.

## ICC Profiles

### Built-in Profiles

Ghostscript ships with bundled ICC profiles in `iccprofiles/`:

| Profile | Description |
|---------|-------------|
| `sRGB.icc` | sRGB IEC61966-2.1 (standard RGB) |
| `USWebUncoated.icc` | U.S. Web Uncoated (SWOP) |
| `DotGain10percent.icc` | 10% dot gain |
| `DotGain15percent.icc` | 15% dot gain |
| `DotGain20percent.icc` | 20% dot gain |
| `FOGRA27.icc` | FOGRA27 (ISO Coated v2) |
| `FOGRA39.icc` | FOGRA39 (ISO Coated v2 1) |
| `CoatedFOGRA39.icc` | Same as FOGRA39 |
| `ISOcoated_v2_300_2006.icc` | ISO Coated v2 |
| `ISOuncoated_v2_300_2006.icc` | ISO Uncoated v2 |
| `ISOwebcoated_v2_300_2006.icc` | ISO Web Coated v2 |
| `sGray.icc` | sGray (standard grayscale) |

### Using Custom Profiles

```bash
# Place profile in GS search path or use absolute path
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -I/usr/share/icc \
   -sOutputProfile=sRGB.icc \
   -c "<< /ColorConversionStrategy /RGB >> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf

# Absolute path
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputProfile=/path/to/profile.icc \
   -c "<< /ColorConversionStrategy /RGB >> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf
```

## Color Conversion Strategies

Set via `ColorConversionStrategy` distiller parameter:

```bash
# Leave color spaces unchanged (default)
gs -sDEVICE=pdfwrite \
   -c "<< /ColorConversionStrategy /LeaveColorUnchanged >> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf

# Convert to RGB
gs -sDEVICE=pdfwrite \
   -c "<< /ColorConversionStrategy /RGB >> setdistillerparams" \
   -sOutputProfile=sRGB.icc \
   -f input.ps -sOutputFile=out.pdf

# Convert to CMYK
gs -sDEVICE=pdfwrite \
   -c "<< /ColorConversionStrategy /CMYK >> setdistillerparams" \
   -sOutputProfile=CoatedFOGRA39.icc \
   -f input.ps -sOutputFile=out.pdf

# Convert to Grayscale
gs -sDEVICE=pdfwrite \
   -c "<< /ColorConversionStrategy /Gray >> setdistillerparams" \
   -sOutputProfile=sGray.icc \
   -f input.ps -sOutputFile=out.pdf
```

## Rendering Intents

```bash
# Default rendering intent
gs -sDEVICE=pdfwrite \
   -c "<< /DefaultRenderingIntent /Default >> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf

# Rendering intents:
#   /Default     — use the default intent from the ICC profile
#   /Perceptual  — preserve overall visual appearance (best for photos)
#   /RelativeColorimetric — preserve spot colors, adapt white point
#   /Saturation  — preserve color saturation (best for business graphics)
#   /AbsoluteColorimetric — preserve exact colors, no white point adaptation
```

## Per-Color-Space Profiles

Fine-grained control with separate profiles for each color space:

```bash
gs -sDEVICE=pdfwrite \
   -c "<<
     /CalRGBProfile (sRGB.icc)
     /CalGrayProfile (sGray.icc)
     /CalCMYKProfile (CoatedFOGRA39.icc)
     /ColorConversionStrategy /LeaveColorUnchanged
   >> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf
```

## PDF/X Color Output

PDF/X requires specific color management:

```bash
# PDF/X-1a (CMYK, no spot colors)
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -dPDFX=true \
   -dPDFXPart=1 \
   -dPDFXSubset=1A \
   -sOutputProfile=CoatedFOGRA39.icc \
   -c "<<
     /ColorConversionStrategy /CMYK
     /DefaultRenderingIntent /RelativeColorimetric
   >> setdistillerparams" \
   -f input.ps -sOutputFile=pdfx.pdf

# PDF/X-4 (CMYK, transparency allowed)
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -dPDFX=true \
   -dPDFXPart=4 \
   -sOutputProfile=CoatedFOGRA39.icc \
   -c "<<
     /ColorConversionStrategy /CMYK
     /DetectBlends true
   >> setdistillerparams" \
   -f input.ps -sOutputFile=pdfx4.pdf
```

## PDF/A Color Output

```bash
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -dPDFA=true \
   -dPDFAPart=2 \
   -dPDFAUsage=true \
   -sOutputProfile=sRGB.icc \
   -c "<<
     /ColorConversionStrategy /RGB
     /DefaultRenderingIntent /RelativeColorimetric
   >> setdistillerparams" \
   -f input.ps -sOutputFile=pdfa.pdf
```

## Raster Device Color

For raster output devices, color management works differently:

```bash
# RGB to grayscale PNG
gs -dBATCH -dNOPAUSE -sDEVICE=pnggray -r300 \
   -sOutputFile=gray.png input.pdf

# Force color output device
gs -dBATCH -dNOPAUSE -sDEVICE=png16m -r300 \
   -sOutputFile=color.png input.pdf

# CMYK separation (4 separate files)
gs -dBATCH -dNOPAUSE -sDEVICE=bmp16m -r300 \
   -sOutputFile=separation_%d.bmp \
   -c "setcmykcolor" \
   -f input.pdf
```

## DeviceN and Spot Colors

```bash
# Preserve DeviceN colors
gs -sDEVICE=pdfwrite \
   -c "<<
     /ColorConversionStrategy /LeaveColorUnchanged
     /PreserveDeviceN true
   >> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf

# Convert spot colors to process
gs -sDEVICE=pdfwrite \
   -c "<<
     /ColorConversionStrategy /CMYK
     /ConvertDeviceN true
   >> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf
```

## Output Intent

```bash
# Set output intent in PDF
gs -sDEVICE=pdfwrite \
   -c "<<
     /OutputIntent [
       /OutputIntent<<
         /Info << /Title (FOGRA39) >>
         /DestOutputProfile (CoatedFOGRA39.icc)
         /OutputCondition (FOGRA39)
         /OutputConditionIdentifier (FOGRA39)
         /RegistryName (http://www.color.org)
       >>
     ]
   >> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf
```

## ICC Profile Commands (PostScript)

```postscript
% Load an ICC profile
/srgb (sRGB.icc) (r) file .makeiccbased

% Create ICC-based color space
[/ICCBased srgb] setcolorspace

% Use the color space
[/ICCBased srgb] setcolorspace
0.2 0.4 0.8 setrgbcolor

% Set default RGB profile
systemdict /ColorSpaceResources get
/DefaultRGB [ /ICCBased srgb ] put
```

## Color Debugging

```bash
# Show color management info
gs -dBATCH -dNOPAUSE -sDEVICE=nullpage \
   -c "currentsystemparams /ColorManagement known { true } { false } if" \
   -c quit

# Debug color conversion
GS_DEBUG=-d128 gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -c "<< /ColorConversionStrategy /RGB >> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf
```

## Gotchas

- **Profile paths are relative to GS search path** — use `-I` to add directories or absolute paths.
- **`/LeaveColorUnchanged` is the default** — Ghostscript doesn't convert colors unless you explicitly set a strategy.
- **PDF/X requires CMYK** — PDF/X-1a and PDF/X-3 require all content in CMYK or Gray. Use `/CMYK` conversion strategy.
- **PDF/A requires an output intent** — always specify `-sOutputProfile` when creating PDF/A.
- **Raster devices don't use distiller params** — color conversion for raster output is controlled by device selection (e.g., `pnggray` for grayscale).
- **ICC profiles need LanguageLevel 2+** — ICC-based color spaces require PostScript Level 2 or higher.
- **`DetectBlends` needed for transparency** — enable `/DetectBlends true` for proper handling of blend modes in PDF output.
- **Built-in profiles are minimal** — for professional color work, use industry-standard profiles (FOGRA, GRACoL, ISO Coated).
