---
name: pixijs-filters-6-1-5
description: >
  PixiJS Filters v6.1.5 — 38 GPU-accelerated shader filters for PixiJS v8.x.
  Use when applying visual effects (blur, glow, bloom, distortion, color correction,
  glitch, CRT, pixelate, outline, drop-shadow, etc.) to PixiJS sprites, containers,
  or the entire stage. Covers pixi-filters npm package API, constructor options,
  properties, and per-filter import paths.
---

# pixijs-filters 6.1.5

GPU-accelerated post-processing filters for PixiJS v8.x. All filters extend `PIXI.Filter` and use both WebGL (GLSL) and WebGPU (WGSL) shader programs.

## Overview

The `pixi-filters` package provides 38 filters organized into categories:

- **Blur** — KawaseBlur, MotionBlur, RadialBlur, ZoomBlur, BackdropBlur, Bloom, AdvancedBloom
- **Color** — Adjustment, ColorGradient, ColorMap, ColorOverlay, ColorReplace, MultiColorReplace, Grayscale, HslAdjustment
- **Distortion** — BulgePinch, Twist, TiltShift, RGBSplit, Shockwave, Reflection
- **Stylize** — Pixelate, Dot, Ascii, CrossHatch, Emboss, Outline, Glow, Bevel, Convolution
- **Atmospheric** — Godray, SimplexNoise, OldFilm, CRT, Glitch
- **Utility** — DropShadow, SimpleLightmap

### Installation

```bash
npm install pixi-filters
```

Requires `pixi.js >= 8.0.0` (peer dependency).

### Import Patterns

```ts
// Full bundle (all 38 filters)
import { BloomFilter, GlowFilter } from 'pixi-filters';

// Per-filter (tree-shakeable)
import { BloomFilter } from 'pixi-filters/bloom';
import { GlowFilter } from 'pixi-filters/glow';
```

### Applying Filters

```ts
// Single filter on a sprite
sprite.filters = [new BloomFilter({ strength: 4 })];
sprite.filterArea = sprite.bounds; // optional: limit filter region

// Multiple filters (applied in order)
sprite.filters = [
    new GlowFilter({ distance: 10, color: 0x00ff00 }),
    new BlurFilter({ blur: { x: 2, y: 2 } }),
];

// Container-level filter
container.filters = [new AdjustmentFilter({ brightness: 1.2, contrast: 1.1 })];

// Full-screen filter (on stage or a full-screen sprite)
app.stage.filters = [new CRTFilter({ curvature: 0.5 })];
```

## Usage

### Constructor Pattern

All filters accept an optional options object. Every property is optional with sensible defaults:

```ts
const filter = new GlowFilter({
    distance: 10,
    outerStrength: 4,
    innerStrength: 0,
    color: 0xffffff,
    alpha: 1,
    quality: 0.1,
    knockout: false,
});
```

### Runtime Property Updates

All filter properties are live-reactive — changing a property updates the GPU uniform immediately:

```ts
filter.distance = 20;
filter.color = 0xff0000;
filter.alpha = 0.5;
```

### Animation

For animated filters (Glitch, Shockwave, CRT, Godray, Reflection, OldFilm), update the `time` property each tick:

```ts
const filter = new ShockwaveFilter();

app.ticker.add(() => {
    filter.time = app.ticker.lastTime / 1000;
});
```

### FilterArea

By default, filters render over the entire display object bounds. Set `filterArea` to limit the region and improve performance:

```ts
sprite.filterArea = new Rectangle(0, 0, 200, 200);
```

### Performance Tips

- Blur filters (KawaseBlur, Bloom, MotionBlur) use multiple render passes — higher `quality` means more passes
- `filterArea` dramatically reduces cost for large sprites
- Chain filters sparingly; each filter adds a render pass
- `BackropBlurFilter` reads the background texture — it is more expensive than standard blur
- `AdvancedBloomFilter` is slower than `BloomFilter` but offers threshold control

## Gotchas

- **`filterArea` is required for `SimpleLightmapFilter`** — without it, the lightmap coordinates will be wrong
- **`GlowFilter` and `OutlineFilter` compile GLSL with hardcoded `distance`/`quality`** — changing these at runtime works in WebGPU but has no effect in WebGL (the fragment shader is compiled once with the constructor values)
- **`MultiColorReplaceFilter.maxColors` is fixed at construction** — the fragment shader is compiled with this count and cannot be changed later
- **`ColorMapFilter` requires a valid texture** — pass `colorMap` in the constructor or set the property; calling `updateColorMap()` after modifying the canvas content
- **`BackdropBlurFilter` must be applied to a container or stage** — it reads the background behind the object; on a single sprite it has nothing to blur
- **`ConvolutionFilter.width`/`height` must match the target** — set them to the actual display object dimensions for correct texel sampling
- **`ZoomBlurFilter.maxKernelSize` is baked into the shader** — changing it at runtime has no effect; recreate the filter instead
- **`PixelateFilter` takes a single number or array** — constructor is `new PixelateFilter(10)` or `new PixelateFilter([8, 4])`, not an options object
- **`EmbossFilter` takes a single number** — constructor is `new EmbossFilter(5)`, not an options object
- **`CrossHatchFilter` and `GrayscaleFilter` have no parameters** — just `new CrossHatchFilter()`
- **Deprecated positional constructors** — v6 migrated all filters to options objects. Old positional args (e.g., `new BloomFilter(4, 4, 1, 5)`) still work but emit deprecation warnings

## References

- [01-filter-list](references/01-filter-list.md) — Complete API reference for all 38 filters (constructor options, properties, defaults)
- [02-blur-filters](references/02-blur-filters.md) — Blur family: KawaseBlur, MotionBlur, RadialBlur, ZoomBlur, BackdropBlur, Bloom, AdvancedBloom
- [03-color-filters](references/03-color-filters.md) — Color manipulation: Adjustment, ColorGradient, ColorMap, ColorOverlay, ColorReplace, MultiColorReplace, Grayscale, HslAdjustment
- [04-distortion-filters](references/04-distortion-filters.md) — Distortion/warp: BulgePinch, Twist, TiltShift, RGBSplit, Shockwave, Reflection
- [05-stylize-filters](references/05-stylize-filters.md) — Stylize: Pixelate, Dot, Ascii, CrossHatch, Emboss, Outline, Glow, Bevel, Convolution
- [06-atmospheric-filters](references/06-atmospheric-filters.md) — Atmospheric: Godray, SimplexNoise, OldFilm, CRT, Glitch
- [07-utility-filters](references/07-utility-filters.md) — Utility: DropShadow, SimpleLightmap
- [08-pixi-core-filters](references/08-pixi-core-filters.md) — Built-in PixiJS core filters (Alpha, Blur, ColorMatrix, Displacement, Noise)
