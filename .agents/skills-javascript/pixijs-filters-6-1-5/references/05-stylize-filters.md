# Stylize Filters

Filters that transform the visual style of content.

## PixelateFilter

**Import:** `pixi-filters/pixelate`

Blocky pixel effect. Constructor takes a number or array, not an options object.

### Constructor

```ts
new PixelateFilter(10);           // square pixels, size 10
new PixelateFilter([8, 4]);       // rectangular pixels
new PixelateFilter({ x: 8, y: 4 }); // Point
```

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `size` | `number \| number[] \| Point` | `10` | Pixel size |
| `sizeX` | `number` | `10` | X-axis pixel size |
| `sizeY` | `number` | `10` | Y-axis pixel size |

### Usage

```ts
const f = new PixelateFilter(16);
sprite.filters = [f];

// Animate pixel size
app.ticker.add(() => {
    f.sizeX = 4 + Math.sin(Date.now() / 500) * 8;
});
```

## DotFilter

**Import:** `pixi-filters/dot`

Halftone dot screen effect, like old newspaper printing.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `scale` | `number` | `1` | Dot scale |
| `angle` | `number` | `5` | Dot angle |
| `grayscale` | `boolean` | `true` | Render as grayscale |

### Usage

```ts
const f = new DotFilter({ scale: 3, angle: 45, grayscale: true });
```

## AsciiFilter

**Import:** `pixi-filters/ascii`

Render image as ASCII characters.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `size` | `number` | `8` | Character cell size |
| `color` | `ColorSource` | `0xffffff` | Character color |
| `replaceColor` | `boolean` | `false` | Replace source colors |

### Usage

```ts
// White ASCII on original colors
const f = new AsciiFilter({ size: 8 });

// Black ASCII characters (replaces source colors)
const f = new AsciiFilter({
    size: 12,
    color: 0x000000,
    replaceColor: true,
});
```

## CrossHatchFilter

**Import:** `pixi-filters/cross-hatch`

Cross-hatch line effect. No parameters.

```ts
const f = new CrossHatchFilter();
```

## EmbossFilter

**Import:** `pixi-filters/emboss`

Emboss relief effect. Constructor takes a single number.

### Constructor

```ts
new EmbossFilter(5); // strength
```

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `strength` | `number` | `5` | Emboss strength |

### Usage

```ts
const f = new EmbossFilter(10);
```

## OutlineFilter

**Import:** `pixi-filters/outline`

Outline/stroke effect around non-transparent pixels.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `thickness` | `number` | `1` | Outline thickness |
| `color` | `ColorSource` | `0x000000` | Outline color |
| `alpha` | `number` | `1` | Outline opacity |
| `quality` | `number` | `0.1` | Quality (0-1); higher = more accurate, slower |
| `knockout` | `boolean` | `false` | Only render outline, hide content |

### Usage

```ts
// Black outline
const f = new OutlineFilter({ thickness: 3, color: 0x000000 });

// Green glow outline
const f = new OutlineFilter({
    thickness: 5,
    color: 0x99ff99,
    alpha: 0.8,
});

// Outline only (no content)
const f = new OutlineFilter({
    thickness: 2,
    color: 0xffffff,
    knockout: true,
});
```

## GlowFilter

**Import:** `pixi-filters/glow`

Inner and outer glow effect.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `distance` | `number` | `10` | Glow spread distance |
| `outerStrength` | `number` | `4` | Outer glow intensity |
| `innerStrength` | `number` | `0` | Inner glow intensity |
| `color` | `ColorSource` | `0xffffff` | Glow color |
| `alpha` | `number` | `1` | Glow opacity |
| `quality` | `number` | `0.1` | Quality (0-1); higher = smoother, slower |
| `knockout` | `boolean` | `false` | Only render glow, hide content |

### Usage

```ts
// White outer glow
const f = new GlowFilter({ distance: 15, outerStrength: 2 });

// Colored glow
const f = new GlowFilter({
    distance: 10,
    outerStrength: 4,
    innerStrength: 1,
    color: 0x00ff00,
    alpha: 0.8,
});

// Glow only (no content)
const f = new GlowFilter({
    distance: 20,
    outerStrength: 3,
    knockout: true,
});
```

## BevelFilter

**Import:** `pixi-filters/bevel`

3D bevel edge effect with light and shadow.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `rotation` | `number` | `45` | Light angle in degrees |
| `thickness` | `number` | `2` | Bevel thickness |
| `lightColor` | `ColorSource` | `0xffffff` | Light color (top/left) |
| `lightAlpha` | `number` | `0.7` | Light opacity |
| `shadowColor` | `ColorSource` | `0x000000` | Shadow color (bottom/right) |
| `shadowAlpha` | `number` | `0.7` | Shadow opacity |

### Usage

```ts
const f = new BevelFilter({
    rotation: 45,
    thickness: 3,
    lightColor: 0xffffff,
    shadowColor: 0x333333,
});
```

## ConvolutionFilter

**Import:** `pixi-filters/convolution`

Matrix convolution — apply any 3x3 kernel for custom effects (blur, sharpen, edge detection, emboss).

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `matrix` | `Float32Array \| number[9]` | `[0,0,0,0,0,0,0,0,0]` | 3x3 kernel matrix |
| `width` | `number` | `200` | Target width |
| `height` | `number` | `200` | Target height |

### Common Kernels

```ts
// Sharpen
const sharpen = new ConvolutionFilter({
    matrix: [0, -1, 0, -1, 5, -1, 0, -1, 0],
    width: sprite.width,
    height: sprite.height,
});

// Edge detection
const edge = new ConvolutionFilter({
    matrix: [-1, -1, -1, -1, 8, -1, -1, -1, -1],
    width: sprite.width,
    height: sprite.height,
});

// Blur (box)
const boxBlur = new ConvolutionFilter({
    matrix: [1, 1, 1, 1, 1, 1, 1, 1, 1],
    width: sprite.width,
    height: sprite.height,
});

// Emboss
const emboss = new ConvolutionFilter({
    matrix: [-2, -1, 0, -1, 1, 1, 0, 1, 2],
    width: sprite.width,
    height: sprite.height,
});
```

### Gotchas

- `width` and `height` must be set to the actual target dimensions for correct texel sampling
- The matrix values should typically sum to 1 for brightness-preserving effects
- For blur kernels, divide by the sum of all values (e.g., 9 for a 3x3 box blur)
