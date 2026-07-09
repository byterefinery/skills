# Complete Filter API Reference

All 38 filters with constructor options, properties, and defaults.

## AdjustmentFilter

**Import:** `pixi-filters/adjustment`

Adjust gamma, contrast, saturation, brightness, alpha, and per-channel color multipliers.

| Property | Type | Default |
|---|---|---|
| `gamma` | `number` | `1` |
| `contrast` | `number` | `1` |
| `saturation` | `number` | `1` |
| `brightness` | `number` | `1` |
| `red` | `number` | `1` |
| `green` | `number` | `1` |
| `blue` | `number` | `1` |
| `alpha` | `number` | `1` |

```ts
const f = new AdjustmentFilter({ brightness: 1.2, contrast: 1.1, saturation: 0.8 });
```

## AdvancedBloomFilter

**Import:** `pixi-filters/advanced-bloom`

Bloom with threshold extraction and Kawase blur. Slower than BloomFilter.

| Property | Type | Default |
|---|---|---|
| `threshold` | `number` | `0.5` |
| `bloomScale` | `number` | `1` |
| `brightness` | `number` | `1` |
| `blur` | `number` | `8` |
| `quality` | `number` | `4` |
| `kernels` | `number[]` | — |
| `pixelSize` | `PointData` | `{ x: 1, y: 1 }` |

## AsciiFilter

**Import:** `pixi-filters/ascii`

ASCII character rendering.

| Property | Type | Default |
|---|---|---|
| `size` | `number` | `8` |
| `color` | `ColorSource` | `0xffffff` |
| `replaceColor` | `boolean` | `false` |

## BackdropBlurFilter

**Import:** `pixi-filters/backdrop-blur`

Blurs everything behind the object. Extends `BlurFilter`.

| Property | Type | Default |
|---|---|---|
| (inherits all `BlurFilter` options) | | |

## BevelFilter

**Import:** `pixi-filters/bevel`

3D bevel edge effect.

| Property | Type | Default |
|---|---|---|
| `rotation` | `number` (degrees) | `45` |
| `thickness` | `number` | `2` |
| `lightColor` | `ColorSource` | `0xffffff` |
| `lightAlpha` | `number` | `0.7` |
| `shadowColor` | `ColorSource` | `0x000000` |
| `shadowAlpha` | `number` | `0.7` |

## BloomFilter

**Import:** `pixi-filters/bloom`

Gaussian bloom using two-pass horizontal/vertical blur.

| Property | Type | Default |
|---|---|---|
| `strength` | `PointData \| number` | `{ x: 2, y: 2 }` |
| `quality` | `number` | `4` |
| `resolution` | `number` | `1` |
| `kernelSize` | `number` | `5` |

Also exposes `strengthX`, `strengthY` for per-axis control.

## BulgePinchFilter

**Import:** `pixi-filters/bulge-pinch`

Circular bulge or pinch distortion.

| Property | Type | Default |
|---|---|---|
| `center` | `PointData` | `{ x: 0.5, y: 0.5 }` |
| `radius` | `number` | `100` |
| `strength` | `number` | `1` |

`strength`: `-1` = strong pinch, `0` = no effect, `1` = strong bulge.

## ColorGradientFilter

**Import:** `pixi-filters/color-gradient`

Apply a gradient overlay (linear, radial, or conic).

| Property | Type | Default |
|---|---|---|
| `type` | `number` | `0` (LINEAR) |
| `stops` | `ColorStop[]` | 2 stops |
| `angle` | `number` (degrees) | `90` |
| `alpha` | `number` | `1` |
| `maxColors` | `number` | `0` (no limit) |
| `replace` | `boolean` | `false` |

Gradient types: `LINEAR = 0`, `RADIAL = 1`, `CONIC = 2`.

ColorStop: `{ offset: number, color: ColorSource, alpha: number }`.

Can also accept CSS gradient string: `{ css: 'linear-gradient(90deg, red, blue)' }`.

## ColorMapFilter

**Import:** `pixi-filters/color-map`

Map colors through a lookup texture (requires a color map image).

| Property | Type | Default |
|---|---|---|
| `colorMap` | `Texture \| TextureSource` | `Texture.WHITE` |
| `mix` | `number` | `1` |
| `nearest` | `boolean` | `false` |

Call `updateColorMap()` after modifying canvas-based color maps.

## ColorOverlayFilter

**Import:** `pixi-filters/color-overlay`

Overlay a solid color on the source.

| Property | Type | Default |
|---|---|---|
| `color` | `ColorSource` | `0x000000` |
| `alpha` | `number` | `1` |

## ColorReplaceFilter

**Import:** `pixi-filters/color-replace`

Replace one color with another.

| Property | Type | Default |
|---|---|---|
| `originalColor` | `ColorSource` | `0xff0000` |
| `targetColor` | `ColorSource` | `0x000000` |
| `tolerance` | `number` | `0.4` |

## ConvolutionFilter

**Import:** `pixi-filters/convolution`

Matrix convolution (blur, edge detection, sharpening, embossing).

| Property | Type | Default |
|---|---|---|
| `matrix` | `Float32Array \| number[9]` | `[0,0,0,0,0,0,0,0,0]` |
| `width` | `number` | `200` |
| `height` | `number` | `200` |

Set `width`/`height` to the actual target dimensions for correct texel sampling.

## CrossHatchFilter

**Import:** `pixi-filters/cross-hatch`

Cross-hatch line effect. No parameters.

```ts
const f = new CrossHatchFilter();
```

## CRTFilter

**Import:** `pixi-filters/crt`

CRT monitor effect: scanlines, noise, vignette.

| Property | Type | Default |
|---|---|---|
| `curvature` | `number` | `1` |
| `lineWidth` | `number` | `1` |
| `lineContrast` | `number` | `0.25` |
| `verticalLine` | `boolean` | `false` |
| `time` | `number` | `0` |
| `noise` | `number` | `0` |
| `noiseSize` | `number` | `1` |
| `seed` | `number` | `0` |
| `vignetting` | `number` | `0.3` |
| `vignettingAlpha` | `number` | `1` |
| `vignettingBlur` | `number` | `0.3` |

Animate `time` for moving scanlines.

## DotFilter

**Import:** `pixi-filters/dot`

Halftone dot screen effect.

| Property | Type | Default |
|---|---|---|
| `scale` | `number` | `1` |
| `angle` | `number` | `5` |
| `grayscale` | `boolean` | `true` |

## DropShadowFilter

**Import:** `pixi-filters/drop-shadow`

Drop shadow using Kawase blur.

| Property | Type | Default |
|---|---|---|
| `offset` | `PointData` | `{ x: 4, y: 4 }` |
| `color` | `ColorSource` | `0x000000` |
| `alpha` | `number` | `0.5` |
| `shadowOnly` | `boolean` | `false` |
| `blur` | `number` | `2` |
| `quality` | `number` | `3` |
| `pixelSize` | `PointData` | `{ x: 1, y: 1 }` |
| `resolution` | `number` | `1` |

Also exposes `offsetX`, `offsetY`, `pixelSizeX`, `pixelSizeY`.

## EmbossFilter

**Import:** `pixi-filters/emboss`

Emboss relief effect.

| Property | Type | Default |
|---|---|---|
| `strength` | `number` | `5` |

Constructor: `new EmbossFilter(strength)` — single number, not options object.

## GlitchFilter

**Import:** `pixi-filters/glitch`

Glitch/displacement effect with slice bands.

| Property | Type | Default |
|---|---|---|
| `slices` | `number` | `5` |
| `offset` | `number` | `100` |
| `direction` | `number` (degrees) | `0` |
| `fillMode` | `number` | `0` (TRANSPARENT) |
| `seed` | `number` | `0` |
| `average` | `boolean` | `false` |
| `minSize` | `number` | `8` |
| `sampleSize` | `number` | `512` |
| `red` | `PointData` | `{ x: 0, y: 0 }` |
| `green` | `PointData` | `{ x: 0, y: 0 }` |
| `blue` | `PointData` | `{ x: 0, y: 0 }` |

Fill modes: `TRANSPARENT = 0`, `ORIGINAL = 1`, `LOOP = 2`, `CLAMP = 3`, `MIRROR = 4`.

Methods: `refresh()` — randomize slices; `shuffle()` — shuffle slice order; `redraw()` — redraw displacement texture.

## GlowFilter

**Import:** `pixi-filters/glow`

Inner/outer glow effect.

| Property | Type | Default |
|---|---|---|
| `distance` | `number` | `10` |
| `outerStrength` | `number` | `4` |
| `innerStrength` | `number` | `0` |
| `color` | `ColorSource` | `0xffffff` |
| `alpha` | `number` | `1` |
| `quality` | `number` | `0.1` |
| `knockout` | `boolean` | `false` |

**Warning:** `distance` and `quality` are baked into the GLSL shader at construction time — runtime changes only work in WebGPU.

## GodrayFilter

**Import:** `pixi-filters/godray`

God rays / light shafts effect.

| Property | Type | Default |
|---|---|---|
| `angle` | `number` (degrees) | `30` |
| `parallel` | `boolean` | `true` |
| `center` | `PointData` | `{ x: 0, y: 0 }` |
| `gain` | `number` | `0.5` |
| `lacunarity` | `number` | `2.5` |
| `time` | `number` | `0` |
| `alpha` | `number` | `1` |

When `parallel` is `true`, `angle` controls ray direction. When `false`, `center` is the focal point.

## GrayscaleFilter

**Import:** `pixi-filters/grayscale`

Convert to grayscale. No parameters.

```ts
const f = new GrayscaleFilter();
```

## HslAdjustmentFilter

**Import:** `pixi-filters/hsl-adjustment`

HSL color adjustment.

| Property | Type | Default |
|---|---|---|
| `hue` | `number` (-180 to 180) | `0` |
| `saturation` | `number` (-1 to 1) | `0` |
| `lightness` | `number` (-1 to 1) | `0` |
| `colorize` | `boolean` | `false` |
| `alpha` | `number` (0 to 1) | `1` |

## KawaseBlurFilter

**Import:** `pixi-filters/kawase-blur`

Fast iterative blur (faster than Gaussian).

| Property | Type | Default |
|---|---|---|
| `strength` | `number \| [number, number]` | `4` |
| `quality` | `number` | `3` |
| `clamp` | `boolean` | `false` |
| `pixelSize` | `PointData` | `{ x: 1, y: 1 }` |

Also exposes `kernels`, `pixelSizeX`, `pixelSizeY`.

## MotionBlurFilter

**Import:** `pixi-filters/motion-blur`

Directional motion blur.

| Property | Type | Default |
|---|---|---|
| `velocity` | `PointData` | `{ x: 0, y: 0 }` |
| `kernelSize` | `number` (odd, >= 5) | `5` |
| `offset` | `number` | `0` |

Also exposes `velocityX`, `velocityY`.

## MultiColorReplaceFilter

**Import:** `pixi-filters/multi-color-replace`

Replace multiple colors simultaneously.

| Property | Type | Default |
|---|---|---|
| `replacements` | `Array<[ColorSource, ColorSource]>` | `[[0xff0000, 0x0000ff]]` |
| `tolerance` | `number` | `0.05` |
| `maxColors` | `number` | `replacements.length` |

Call `refresh()` after modifying the replacements array in place. `maxColors` is fixed at construction.

## OldFilmFilter

**Import:** `pixi-filters/old-film`

Vintage film effect: sepia, noise, scratches, vignette.

| Property | Type | Default |
|---|---|---|
| `sepia` | `number` | `0.3` |
| `noise` | `number` | `0.3` |
| `noiseSize` | `number` | `1` |
| `scratch` | `number` | `0.5` |
| `scratchDensity` | `number` | `0.3` |
| `scratchWidth` | `number` | `1` |
| `vignetting` | `number` | `0.3` |
| `vignettingAlpha` | `number` | `1` |
| `vignettingBlur` | `number` | `0.3` |
| `seed` | `number` | `0` |

## OutlineFilter

**Import:** `pixi-filters/outline`

Outline/stroke effect.

| Property | Type | Default |
|---|---|---|
| `thickness` | `number` | `1` |
| `color` | `ColorSource` | `0x000000` |
| `alpha` | `number` | `1` |
| `quality` | `number` (0 to 1) | `0.1` |
| `knockout` | `boolean` | `false` |

**Warning:** `quality` is baked into the GLSL shader at construction time.

## PixelateFilter

**Import:** `pixi-filters/pixelate`

Blocky pixel effect.

| Property | Type | Default |
|---|---|---|
| `size` | `number \| number[] \| Point` | `10` |

Constructor: `new PixelateFilter(10)` or `new PixelateFilter([8, 4])`.

Also exposes `sizeX`, `sizeY`.

## RadialBlurFilter

**Import:** `pixi-filters/radial-blur`

Radial/spinning blur.

| Property | Type | Default |
|---|---|---|
| `angle` | `number` (degrees) | `0` |
| `center` | `PointData` | `{ x: 0, y: 0 }` |
| `kernelSize` | `number` (odd, >= 3) | `5` |
| `radius` | `number` | `-1` (infinite) |

Also exposes `centerX`, `centerY`.

## ReflectionFilter

**Import:** `pixi-filters/reflection`

Water reflection with wave distortion.

| Property | Type | Default |
|---|---|---|
| `mirror` | `boolean` | `true` |
| `boundary` | `number` | `0.5` |
| `amplitude` | `[number, number]` | `[0, 20]` |
| `waveLength` | `[number, number]` | `[30, 100]` |
| `alpha` | `[number, number]` | `[1, 1]` |
| `time` | `number` | `0` |

Also exposes `amplitudeStart`, `amplitudeEnd`, `wavelengthStart`, `wavelengthEnd`, `alphaStart`, `alphaEnd`.

Animate `time` for moving waves.

## RGBSplitFilter

**Import:** `pixi-filters/rgb-split`

Chromatic aberration by offsetting RGB channels.

| Property | Type | Default |
|---|---|---|
| `red` | `PointData` | `{ x: -10, y: 0 }` |
| `green` | `PointData` | `{ x: 0, y: 10 }` |
| `blue` | `PointData` | `{ x: 0, y: 0 }` |

Also exposes `redX`, `redY`, `greenX`, `greenY`, `blueX`, `blueY`.

## ShockwaveFilter

**Import:** `pixi-filters/shockwave`

Pond ripple / blast wave effect.

| Property | Type | Default |
|---|---|---|
| `center` | `PointData` | `{ x: 0, y: 0 }` |
| `speed` | `number` (px/s) | `500` |
| `amplitude` | `number` | `30` |
| `wavelength` | `number` | `160` |
| `brightness` | `number` | `1` |
| `radius` | `number` | `-1` (infinite) |
| `time` | `number` | `0` |

Also exposes `centerX`, `centerY`. Animate `time` for expanding ripples.

## SimpleLightmapFilter

**Import:** `pixi-filters/simple-lightmap`

Lightmap overlay for dynamic lighting.

| Property | Type | Default |
|---|---|---|
| `lightMap` | `Texture` | `Texture.WHITE` |
| `color` | `ColorSource` | `0x000000` |
| `alpha` | `number` | `1` |

**Requires `filterArea`** on the target display object for correct coordinate mapping.

## SimplexNoiseFilter

**Import:** `pixi-filters/simplex-noise`

Simplex noise multiplication.

| Property | Type | Default |
|---|---|---|
| `strength` | `number` | `0.5` |
| `noiseScale` | `number` | `10` |
| `offsetX` | `number` | `0` |
| `offsetY` | `number` | `0` |
| `offsetZ` | `number` | `0` |
| `step` | `number` | `-1` |

`step > 0` creates a blocky/quantized noise effect.

## TiltShiftFilter

**Import:** `pixi-filters/tilt-shift`

Depth-of-field blur between two points.

| Property | Type | Default |
|---|---|---|
| `blur` | `number` | `100` |
| `gradientBlur` | `number` | `600` |
| `start` | `PointData` | `{ x: 0, y: height/2 }` |
| `end` | `PointData` | `{ x: width, y: height/2 }` |

Also exposes `startX`, `startY`, `endX`, `endY`.

## TwistFilter

**Import:** `pixi-filters/twist`

Circular twist distortion.

| Property | Type | Default |
|---|---|---|
| `padding` | `number` | `20` |
| `radius` | `number` | `200` |
| `angle` | `number` (radians) | `4` |
| `offset` | `PointData` | `{ x: 0, y: 0 }` |

Also exposes `offsetX`, `offsetY`.

## ZoomBlurFilter

**Import:** `pixi-filters/zoom-blur`

Zoom-in/zoom-out blur.

| Property | Type | Default |
|---|---|---|
| `strength` | `number` | `0.1` |
| `center` | `PointData` | `{ x: 0, y: 0 }` |
| `innerRadius` | `number` | `0` |
| `radius` | `number` | `-1` (infinite) |
| `maxKernelSize` | `number` | `32` |

Also exposes `centerX`, `centerY`.

**Warning:** `maxKernelSize` is baked into the shader at construction.
