# ImageMagick 7.1.2-26 — Options Reference

## Table of Contents

- [Image Settings](#image-settings)
- [Image Operators](#image-operators)
- [Image Channel Operators](#image-channel-operators)
- [Image Sequence Operators](#image-sequence-operators)
- [Image Stack Operators](#image-stack-operators)
- [Miscellaneous Options](#miscellaneous-options)
- [Geometry Syntax](#geometry-syntax)
- [Define Options](#define-options)

---

## Image Settings

Settings that configure how images are read or written.

| Option | Description |
|---|---|
| `-adjoin` | Join images into single multi-image file |
| `-affine matrix` | Affine transform matrix |
| `-alpha option` | on, activate, off, deactivate, set, opaque, copy, transparent, extract, background, shape |
| `-antialias` | Remove pixel aliasing (for text/vector rendering) |
| `-authenticate value` | Decrypt image with password |
| `-background color` | Background color |
| `-bias value` | Add bias when convolving |
| `-black-point-compensation` | Use black point compensation |
| `-bordercolor color` | Border color |
| `-caption string` | Assign caption to image |
| `-cdl filename` | Color correct with Color Decision List |
| `-colors value` | Preferred number of colors |
| `-colorspace type` | Alternate image colorspace |
| `-comment string` | Annotate image with comment |
| `-compose operator` | Set composite operator |
| `-compress type` | Pixel compression when writing (None, B44A, B44, BI, Deflate, Fax, Group4, JPEG, LZW, LZMA, LZWF, RLE, WebP, Zip, ZipS) |
| `-decipher filename` | Decrypt pixels |
| `-define format:option` | Format-specific options |
| `-delay centiseconds` | Frame delay for animations |
| `-density geometry` | Horizontal/vertical density (DPI) |
| `-depth value` | Image depth (8, 16, 32) |
| `-direction type` | Text direction (LeftToRight, RightToLeft) |
| `-display server` | X server to get image/font from |
| `-dispose method` | Layer disposal (None, Background, Previous) |
| `-dither method` | Error diffusion (FloydSteinberg, Riemersma, Stucki, Sierra, TwoBlueSquares, SierraTwo, SierraTwoStrong, No) |
| `-encipher filename` | Encrypt pixels |
| `-encoding type` | Text encoding (ASCII, UTF8, GB18030, Japanese, Korean, SimplifiedChinese, TraditionalChinese) |
| `-endian type` | Endianness (MSB, LSB) |
| `-features distance` | Analyze image features (contrast, correlation) |
| `-family name` | Font family |
| `-fill color` | Fill color for drawing |
| `-filter type` | Resize filter (Point, Box, Triangle, Hermite, Hanning, Hamming, Blackman, Gaussian, Quadratic, Cubic, Catrom, Mitchell, Lagrange, Bessel, Spline, Lanczos, B-Spline, Robidoux, RobidouxSharp, Cosine, Sinc, Jinc, Spherical, Boomerang, TopHat, CosineSine, PeterElzas, SincCosine, SincSine, SincLanczos, SincSpline, SincQuadratic, SincBell, SincBessel, SincGauss, Kaiser, Welch, Parzen, Bohman, Sinc, Lagrange, Spline) |
| `-flatten` | Flatten image sequence |
| `-font name` | Font name |
| `-format "string"` | Output formatted characteristics |
| `-fuzz distance` | Color tolerance (e.g., `10%`, `0.1`) |
| `-gravity type` | Text placement (NorthWest, North, NorthEast, West, Center, East, SouthWest, South, SouthEast) |
| `-intensity method` | Intensity generation (AllChannels, Average, Lightness, Maximum, Rec601Luma, Rec709Luma, HCL, HCLp, HWB, Rec601Luma, sRGB) |
| `-intent type` | Rendering intent (Perceptual, RelativeColorimetric, Saturation, AbsoluteColorimetric) |
| `-interlace type` | Interlacing (None, Line, Plane, JPEG, GIF, PNG) |
| `-interpolate method` | Interpolation (Average, AverageHash, Barycentric, Bilinear, BlendAtten, Blend, Cubic, CubicB-Spline, CubicBlackman, CubicBox, CubicCatmullRom, CubicHermite, CubicICcubic, CubicMitchell, CubicPoly, CubicQuadratic, CubicSpline, Mesh, Nearest, Sinc, SincBessel, SincBoomerang, SincGaussian, SincLanczos, SincQuadratic, SincSpherical, SincBell, SincBessel, SincCosine, SincLanczos, SincQuadratic, SincSine, SincSpline, Tetrahedral, Triangle, Vickers) |
| `-interline-spacing value` | Space between text lines |
| `-interword-spacing value` | Space between words |
| `-kerning value` | Space between letters |
| `-label string` | Assign label |
| `-limit type value` | Resource limit (memory, map, area, disk, file, thread, time) |
| `-loop iterations` | GIF loop count (0 = infinite) |
| `-matte` | Store matte channel |
| `-mattecolor color` | Matte color |
| `-metric type` | Comparison metric (AE, FSSIM, MAE, ME, MSE, NCC, PHASH, RMSE, PSNR) |
| `-moments` | Report image moments |
| `-monitor` | Monitor progress |
| `-orient type` | Image orientation (TopLeft, TopRight, BottomRight, BottomLeft, LeftTop, RightTop, RightBottom, LeftBottom) |
| `-page geometry` | Canvas size/location (setting) |
| `-ping` | Efficient attribute detection (read headers only) |
| `-pointsize value` | Font point size |
| `-precision value` | Significant digits to print |
| `-preview type` | Preview type (Brighten, Contrast, Despeckle, Blur, Sharpen, Rotate, Hue, Saturation, Sharp, Gamma, Spiff, Dull, Edge, Raise, Segment, Sweep, Threshold, Shear, Jwt, Implode, Solarize, Distort, Oil, Crop, Raise, Segement, Swirl, Wave, Equalize, Profile, Blur, Sharpen, Threshold, Edge) |
| `-quality value` | JPEG/MIFF/PNG compression (1-100) |
| `-quiet` | Suppress warnings |
| `-read-mask filename` | Associate read mask |
| `-regard-warnings` | Pay attention to warnings |
| `-remap filename` | Transform colors to match reference |
| `-repage geometry` | Canvas size/location (operator) |
| `-respect-parentheses` | Settings persist within parentheses |
| `-sampling-factor geometry` | JPEG sampling factor |
| `-scene value` | Scene number |
| `-seed value` | Seed pseudo-random numbers |
| `-size geometry` | Image width x height |
| `-statistic type geometry` | Neighborhood statistic (Gradient, Mean, Median, Mode, NonPeak, Variance, StandardDeviation) |
| `-stretch type` | Font stretch (UltraCondensed, ExtraCondensed, Condensed, SemiCondensed, Normal, SemiExpanded, Expanded, ExtraExpanded, UltraExpanded) |
| `-stroke color` | Stroke color |
| `-strokewidth value` | Stroke width |
| `-style type` | Font style (Normal, Italic, Oblique) |
| `-support factor` | Resize support (>1.0 blurry, <1.0 sharp) |
| `-synchronize` | Sync to storage |
| `-taint` | Mark as modified |
| `-texture filename` | Texture to tile onto background |
| `-tile filename` | Tile image when filling |
| `-tile-offset geometry` | Tile offset |
| `-treedepth value` | Color tree depth |
| `-transparent-color color` | Transparent color |
| `-undercolor color` | Annotation bounding box color |
| `-units type` | Resolution units (None, PixelsPerInch, PixelsPerCentimeter) |
| `-verbose` | Print detailed information |
| `-view` | FlashPix viewing transforms |
| `-virtual-pixel method` | Virtual pixel access (Background, Constant, Edge, Mirror, Random, Tile, Transparent, Mask, Black, White, HorizontalTile, VerticalTile, HorizontalTileEdge, VerticalTileEdge, CheckerTile) |
| `-weight type` | Font weight (Thin, ExtraLight, Light, Normal, Medium, SemiBold, Bold, ExtraBold, Black, ExtraBlack) |
| `-write-mask filename` | Write mask |

---

## Image Operators

Operators that modify pixel data.

| Option | Description |
|---|---|
| `-adaptive-blur geometry` | Adaptive blur, less near edges |
| `-adaptive-resize geometry` | Data-dependent triangulation resize |
| `-adaptive-sharpen geometry` | Adaptive sharpen, more near edges |
| `-annotate geometry text` | Annotate with text |
| `-auto-gamma` | Auto-adjust gamma |
| `-auto-level` | Auto-adjust color levels |
| `-auto-orient` | Auto-orient from EXIF |
| `-auto-threshold method` | Auto threshold (Bayes, Kapur, Otsu, Renyi, Triangle, Yen) |
| `-bilateral-blur geometry` | Edge-preserving blur |
| `-black-threshold value` | Pixels below threshold → black |
| `-blue-shift factor` | Simulate nighttime scene |
| `-blur geometry` | Reduce noise and detail |
| `-border geometry` | Surround with border |
| `-brightness-contrast geometry` | Adjust brightness/contrast |
| `-canny geometry` | Canny edge detection |
| `-charcoal radius` | Simulate charcoal drawing |
| `-chop geometry` | Remove interior pixels |
| `-clahe geometry` | Contrast-limited adaptive histogram equalization |
| `-clamp` | Keep pixel values in range |
| `-clip` | Clip along 8BIM path |
| `-clip-mask filename` | Associate clip mask |
| `-clip-path id` | Clip along named 8BIM path |
| `-color-matrix matrix` | Apply color correction matrix |
| `-color-threshold start-stop` | Pixels in range → white, else black |
| `-colorize value` | Colorize with fill color |
| `-connected-component connectivity` | Label connected regions |
| `-contrast` | Enhance/reduce contrast |
| `-contrast-stretch geometry` | Stretch intensity range |
| `-convolve coefficients` | Apply convolution kernel |
| `-cycle amount` | Cycle colormap |
| `-deskew threshold` | Straighten image |
| `-despeckle` | Reduce speckles |
| `-distort method args` | Distort image |
| `-draw string` | Draw graphic primitive |
| `-edge radius` | Edge detection filter |
| `-emboss radius` | Emboss image |
| `-enhance` | Enhance noisy image |
| `-equalize` | Histogram equalization |
| `-evaluate operator value` | Arithmetic/logical expression |
| `-extent geometry` | Set image size (pad/crop) |
| `-extract geometry` | Extract area |
| `-fft` | Discrete Fourier transform |
| `-flip` | Flip vertically |
| `-floodfill geometry color` | Floodfill with color |
| `-flop` | Flip horizontally |
| `-frame geometry` | Ornamental border |
| `-function name` | Apply function (Polynomial, Sinusoidal) |
| `-gamma value` | Gamma correction |
| `-gaussian-blur geometry` | Gaussian blur |
| `-geometry geometry` | Preferred size/location |
| `-grayscale method` | Convert to grayscale |
| `-hough-lines geometry` | Identify lines |
| `-identify` | Identify format/characteristics |
| `-ift` | Inverse DFT |
| `-implode amount` | Implode pixels to center |
| `-integral` | Sum of pixel values |
| `-interpolative-resize geometry` | Interpolation resize |
| `-kmeans geometry` | K-means color reduction |
| `-lat geometry` | Local adaptive thresholding |
| `-layers method` | Optimize/compare layers (Optimize, OptimizePlus, OptimizeTrans, CompareAny, CompareDispose, CompareOverlapping, Merge, RemoveDuplicate, RemoveFirst, RemoveLast, Trim) |
| `-level value` | Adjust contrast levels |
| `-level-colors color,color` | Level with given colors |
| `-linear-stretch geometry` | Stretch with saturation |
| `-liquid-rescale geometry` | Seam-carving resize |
| `-mean-shift geometry` | Delineate clusters |
| `-median geometry` | Median filter |
| `-mode geometry` | Predominant color of neighborhood |
| `-modulate value` | Vary brightness, saturation, hue |
| `-monochrome` | Convert to black and white |
| `-morphology method kernel` | Morphology operation |
| `-motion-blur geometry` | Simulate motion blur |
| `-negate` | Complement colors |
| `-noise geometry` | Add/reduce noise |
| `-normalize` | Span full color range |
| `-opaque color` | Change color to fill color |
| `-ordered-dither NxN` | Ordered dither pattern |
| `-paint radius` | Oil painting effect |
| `-perceptible epsilon` | Make small values perceptible |
| `-polaroid angle` | Polaroid effect |
| `-posterize levels` | Reduce color levels |
| `-print string` | Print interpreted string |
| `-profile filename` | Add/delete/apply profile |
| `-quantize colorspace` | Reduce colors |
| `-radial-blur angle` | Radial blur |
| `-raise value` | 3-D edge effect |
| `-random-threshold low,high` | Random threshold |
| `-range-threshold values` | Hard/soft range threshold |
| `-region geometry` | Apply options to region |
| `-render` | Render vector graphics |
| `-resample geometry` | Change resolution |
| `-resize geometry` | Resize image |
| `-roll geometry` | Roll vertically/horizontally |
| `-rotate degrees` | Rotate image |
| `-sample geometry` | Pixel sampling scale |
| `-scale geometry` | Scale image |
| `-segment values` | Segment image |
| `-selective-blur geometry` | Selective blur by contrast |
| `-sepia-tone threshold` | Sepia effect |
| `-set property value` | Set property |
| `-shade degrees` | Shade with distant light |
| `-shadow geometry` | Simulate shadow |
| `-sharpen geometry` | Sharpen image |
| `-shave geometry` | Shave edge pixels |
| `-shear geometry` | Shear along X/Y axis |
| `-sigmoidal-contrast geometry` | Sigmoidal contrast enhancement |
| `-sketch geometry` | Pencil sketch effect |
| `-solarize threshold` | Solarize effect |
| `-sort-pixels` | Sort scanlines by intensity |
| `-sparse-color method args` | Fill from color points |
| `-splice geometry` | Splice background into image |
| `-spread amount` | Random pixel displacement |
| `-strip` | Remove all profiles and comments |
| `-swirl degrees` | Swirl pixels |
| `-threshold value` | Threshold image |
| `-thumbnail geometry` | Create thumbnail |
| `-tint value` | Tint with fill color |
| `-transform` | Affine transform |
| `-transparent color` | Make color transparent |
| `-transpose` | Flip + rotate 90° |
| `-transverse` | Flop + rotate 270° |
| `-trim` | Trim edges |
| `-type type` | Image type (Bilevel, Grayscale, GrayscaleMatte, Palette, PaletteMatte, TrueColor, TrueColorMatte, ColorSeparation, ColorSeparationMatte) |
| `-unique-colors` | Unique colors only |
| `-unsharp geometry` | Unsharp mask sharpen |
| `-vignette geometry` | Vignette effect |
| `-wave geometry` | Sine wave distortion |
| `-wavelet-denoise threshold` | Wavelet noise removal |
| `-white-balance` | Auto white balance |
| `-white-threshold value` | Pixels above threshold → white |

---

## Image Channel Operators

| Option | Description |
|---|---|
| `-channel mask` | Set channel mask (R, G, B, A, C, M, Y, K, Opacity, All, Red, Green, Blue, Alpha, Cyan, Magenta, Yellow, Black, Opacity, Index, Ignore) |
| `-channel-extract channels` | Extract channels in order |
| `-channel-inject channels` | Inject channels in order |
| `-channel-swap c,c` | Swap channels |
| `-channel-fx expression` | Exchange/extract/transfer channels |
| `-separate` | Separate channel to grayscale |

---

## Image Sequence Operators

| Option | Description |
|---|---|
| `-affinity filename` | Match colors to reference |
| `-append` | Append top-to-bottom (+append for left-to-right) |
| `-clut` | Apply color lookup table |
| `-coalesce` | Merge sequence (for GIF editing) |
| `-combine` | Combine images |
| `-complex operator` | Complex math (Add, Subtract, Divide, Multiply, Convolve, Correlate, Determinant, FFT, InverseFFT, Log, Phase, Real, Imaginary, Magnitude, Argument) |
| `-composite` | Composite image |
| `-copy geometry offset` | Copy pixel region |
| `-crop geometry` | Cut rectangular region |
| `-deconstruct` | Break into constituent frames |
| `-evaluate-sequence operator` | Sequence arithmetic (Add, And, Subtract, Divide, Exponentiate, LeftShift, Max, Min, Or, RightShift, Set, xor, Xor, Arithmetic, Geometric, Lightning) |
| `-flatten` | Flatten sequence |
| `-fx expression` | Math expression on channels |
| `-hald-clut` | Apply Hald CLUT |
| `-morph value` | Morph sequence |
| `-mosaic` | Create mosaic |
| `-poly terms` | Build polynomial from sequence |
| `-process arguments` | Custom filter |
| `-smush geometry` | Smush sequence together |
| `-write filename` | Write to file |

---

## Image Stack Operators

| Option | Description |
|---|---|
| `-clone indexes` | Clone image(s) |
| `-delete indexes` | Delete from sequence |
| `-duplicate count,indexes` | Duplicate image(s) |
| `-insert index` | Insert last image |
| `-reverse` | Reverse sequence |
| `-swap indexes` | Swap two images |

---

## Miscellaneous Options

| Option | Description |
|---|---|
| `-debug events` | Debug output |
| `-distribute-cache port` | Distributed pixel cache |
| `-help` | Print options |
| `-log format` | Debug log format |
| `-list type` | List Color, Configure, Delegate, Format, Magic, Module, Resource, Type |
| `-version` | Print version |

---

## Geometry Syntax

```
WxH        # width x height
WxH+X+Y    # with offset
WxH-X-Y    # with negative offset
WxH%       # percentage
WxH\>      # only shrink if larger
WxH\<      # only enlarge if smaller
WxH\!      # ignore aspect ratio
WxH^       # fit within (may crop)
```

---

## Define Options

Format-specific options via `-define format:option`.

### JPEG
```
-define jpeg:extent=500KB          # target file size
-define jpeg:fancy-upsampling=off  # disable fancy upsampling
-define jpeg:extent=200KB          # progressive quality adjustment
```

### PNG
```
-define png:compression-level=9    # max compression
-define png:compression-strategy=1 # Huffman only
-define png:exclude-chunks=tEXt   # exclude text chunks
```

### WebP
```
-define webp:lossless=true         # lossless mode
-define webp:method=5              # compression method 0-6
```

### TIFF
```
-define tiff:compression=lzma      # LZMA compression
-define tiff:resolution-unit=inch  # DPI unit
```

### GIF
```
-define gif:delay=10               # frame delay
-define gif:dispose=restore        # disposal method
```

### PDF
```
-define pdf:density=300            # render density
-define pdf:use-cmyk=true          # use CMYK
```
