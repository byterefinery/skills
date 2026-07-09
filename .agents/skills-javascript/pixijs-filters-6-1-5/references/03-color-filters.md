# Color Filters

Filters that manipulate, replace, or overlay colors.

## AdjustmentFilter

**Import:** `pixi-filters/adjustment`

Fast image adjustment: gamma, contrast, saturation, brightness, per-channel multipliers. Simpler and faster than `ColorMatrixFilter`.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `gamma` | `number` | `1` | Luminance adjustment |
| `contrast` | `number` | `1` | Contrast multiplier |
| `saturation` | `number` | `1` | Color saturation |
| `brightness` | `number` | `1` | Overall brightness |
| `red` | `number` | `1` | Red channel multiplier |
| `green` | `number` | `1` | Green channel multiplier |
| `blue` | `number` | `1` | Blue channel multiplier |
| `alpha` | `number` | `1` | Alpha multiplier |

### Usage

```ts
// Warm tone
const f = new AdjustmentFilter({ red: 1.1, blue: 0.9 });

// Desaturated and bright
const f = new AdjustmentFilter({ saturation: 0.5, brightness: 1.3 });

// High contrast
const f = new AdjustmentFilter({ contrast: 1.5, gamma: 0.9 });
```

## ColorGradientFilter

**Import:** `pixi-filters/color-gradient`

Apply a gradient overlay (linear, radial, or conic). Can replace or multiply with existing colors.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `type` | `number` | `0` | 0=LINEAR, 1=RADIAL, 2=CONIC |
| `stops` | `ColorStop[]` | 2 stops | Gradient stops (min 2) |
| `angle` | `number` | `90` | Angle in degrees (for linear/conic) |
| `alpha` | `number` | `1` | Gradient opacity |
| `maxColors` | `number` | `0` | Max colors to render (0 = no limit) |
| `replace` | `boolean` | `false` | Replace (true) or multiply (false) |

### Gradient Types

```ts
ColorGradientFilter.LINEAR = 0
ColorGradientFilter.RADIAL = 1
ColorGradientFilter.CONIC = 2
```

### ColorStop

```ts
interface ColorStop {
    offset: number;    // 0 to 1
    color: ColorSource;
    alpha: number;     // 0 to 1
}
```

### Usage

```ts
// Linear gradient overlay
const f = new ColorGradientFilter({
    type: ColorGradientFilter.LINEAR,
    angle: 90,
    stops: [
        { offset: 0, color: 0xff0000, alpha: 1 },
        { offset: 0.5, color: 0x00ff00, alpha: 0.5 },
        { offset: 1, color: 0x0000ff, alpha: 1 },
    ],
    alpha: 0.5,
});

// Radial gradient
const f = new ColorGradientFilter({
    type: ColorGradientFilter.RADIAL,
    stops: [
        { offset: 0, color: 0xffffff, alpha: 1 },
        { offset: 1, color: 0x000000, alpha: 0.8 },
    ],
});

// From CSS string
const f = new ColorGradientFilter({
    css: 'linear-gradient(90deg, red, blue)',
    alpha: 0.5,
});

// Replace existing colors entirely
const f = new ColorGradientFilter({
    type: ColorGradientFilter.LINEAR,
    stops: [
        { offset: 0, color: 0xff0000, alpha: 1 },
        { offset: 1, color: 0x0000ff, alpha: 1 },
    ],
    replace: true,
});
```

## ColorMapFilter

**Import:** `pixi-filters/color-map`

Map pixel colors through a lookup texture (LUT). The color map texture should be a vertical strip where each row maps input brightness to output color.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `colorMap` | `Texture \| TextureSource` | `Texture.WHITE` | The LUT texture |
| `mix` | `number` | `1` | Blend: 0=original, 1=fully mapped |
| `nearest` | `boolean` | `false` | Use nearest-neighbor sampling |
| `colorSize` | `number` | readonly | Height of color map (read-only) |

### Usage

```ts
// Load a color map texture
const colorMapTexture = await Texture.from('lut.png');

const f = new ColorMapFilter({
    colorMap: colorMapTexture,
    mix: 1,
    nearest: false,
});

// Partial effect
f.mix = 0.5;

// Canvas-based color map
const canvas = document.createElement('canvas');
// ... draw color map to canvas ...
const texture = Texture.from(canvas);
const f = new ColorMapFilter({ colorMap: texture });

// After modifying canvas content:
f.updateColorMap();
```

## ColorOverlayFilter

**Import:** `pixi-filters/color-overlay`

Overlay a solid color on top of the source image.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `color` | `ColorSource` | `0x000000` | Overlay color |
| `alpha` | `number` | `1` | Overlay opacity |

### Usage

```ts
// Red tint
const f = new ColorOverlayFilter({ color: 0xff0000, alpha: 0.3 });

// Semi-transparent white wash
const f = new ColorOverlayFilter({ color: 0xffffff, alpha: 0.5 });
```

## ColorReplaceFilter

**Import:** `pixi-filters/color-replace`

Replace one specific color with another, with tolerance for near-matches.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `originalColor` | `ColorSource` | `0xff0000` | Color to find |
| `targetColor` | `ColorSource` | `0x000000` | Replacement color |
| `tolerance` | `number` | `0.4` | Match tolerance (lower = exact, higher = inclusive) |

### Usage

```ts
// Replace red with blue
const f = new ColorReplaceFilter({
    originalColor: 0xff0000,
    targetColor: 0x0000ff,
    tolerance: 0.001,
});

// Replace using RGB arrays
const f = new ColorReplaceFilter({
    originalColor: [220 / 255, 220 / 255, 220 / 255],
    targetColor: [225 / 255, 200 / 255, 215 / 255],
    tolerance: 0.001,
});

// Hex shorthand
const f = new ColorReplaceFilter({
    originalColor: 0xdcdcdc,
    targetColor: 0xe1c8d7,
    tolerance: 0.001,
});
```

## MultiColorReplaceFilter

**Import:** `pixi-filters/multi-color-replace`

Replace multiple colors simultaneously. Extends ColorReplaceFilter concept.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `replacements` | `Array<[ColorSource, ColorSource]>` | `[[0xff0000, 0x0000ff]]` | Color pairs |
| `tolerance` | `number` | `0.05` | Match tolerance |
| `maxColors` | `number` | `replacements.length` | Max replacements (fixed at construction) |

### Methods

- `refresh()` — re-apply changes after modifying the replacements array in place

### Usage

```ts
// Replace red→blue and green→white
const f = new MultiColorReplaceFilter({
    replacements: [
        [0xff0000, 0x0000ff],
        [0x00ff00, 0xffffff],
    ],
    tolerance: 0.001,
});

// Using RGB arrays
const f = new MultiColorReplaceFilter({
    replacements: [
        [[1, 0, 0], [0, 0, 1]],
        [[0, 1, 0], [1, 1, 1]],
    ],
    tolerance: 0.001,
});

// Modify in place and refresh
f.replacements[0][1] = 0x00ff00; // change first target to green
f.refresh();
```

## GrayscaleFilter

**Import:** `pixi-filters/grayscale`

Convert image to grayscale. No parameters.

```ts
const f = new GrayscaleFilter();
sprite.filters = [f];
```

## HslAdjustmentFilter

**Import:** `pixi-filters/hsl-adjustment`

Adjust hue, saturation, and lightness in HSL color space.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `hue` | `number` | `0` | Hue shift in degrees (-180 to 180) |
| `saturation` | `number` | `0` | Saturation adjustment (-1 to 1) |
| `lightness` | `number` | `0` | Lightness adjustment (-1 to 1) |
| `colorize` | `boolean` | `false` | Colorize the image |
| `alpha` | `number` | `1` | Effect opacity (0 to 1) |

### Usage

```ts
// Shift hue by 90 degrees
const f = new HslAdjustmentFilter({ hue: 90 });

// Desaturate
const f = new HslAdjustmentFilter({ saturation: -1 });

// Darken and colorize
const f = new HslAdjustmentFilter({
    hue: 180,
    saturation: 0.5,
    lightness: -0.3,
    colorize: true,
});
```
