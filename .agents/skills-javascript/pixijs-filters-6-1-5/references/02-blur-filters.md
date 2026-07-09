# Blur Filters

All blur filters use multi-pass rendering and GPU shaders.

## KawaseBlurFilter

**Import:** `pixi-filters/kawase-blur`

Fast iterative blur based on the Kawase algorithm. Significantly faster than Gaussian blur for comparable quality.

### Constructor

```ts
new KawaseBlurFilter({
    strength: 4,       // blur amount (> 0)
    quality: 3,        // iteration count (integer >= 1)
    clamp: false,      // clamp edges to prevent dark borders
    pixelSize: { x: 1, y: 1 },
});
```

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `strength` | `number` | `4` | Blur amount; higher = blurrier |
| `quality` | `number` | `3` | Number of passes; higher = smoother but slower |
| `clamp` | `boolean` | `false` | Clamp edges; prevents dark borders on fullscreen filters |
| `pixelSize` | `PointData` | `{ x: 1, y: 1 }` | Pixel step size; larger = blurrier |
| `pixelSizeX` | `number` | `1` | X-axis pixel step |
| `pixelSizeY` | `number` | `1` | Y-axis pixel step |
| `kernels` | `number[]` | auto-generated | Raw kernel values; set manually for advanced control |

### How It Works

Generates a descending kernel array from `strength` down to `strength - step * (quality - 1)`. Each kernel value is applied as a separate render pass, alternating between two render targets.

### Usage

```ts
// Basic blur
const blur = new KawaseBlurFilter({ strength: 8, quality: 4 });
sprite.filters = [blur];

// Custom kernels for precise control
const blur = new KawaseBlurFilter({
    strength: [4, 2, 1], // exact kernel values
});

// Clamp to avoid edge darkening
const blur = new KawaseBlurFilter({ strength: 4, clamp: true });
```

## MotionBlurFilter

**Import:** `pixi-filters/motion-blur`

Directional blur simulating motion along a velocity vector.

### Constructor

```ts
new MotionBlurFilter({
    velocity: { x: 0, y: 0 }, // direction and speed
    kernelSize: 5,            // must be odd, >= 5
    offset: 0,                // blur offset
});
```

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `velocity` | `PointData` | `{ x: 0, y: 0 }` | Motion direction and magnitude |
| `velocityX` | `number` | `0` | X-axis velocity |
| `velocityY` | `number` | `0` | Y-axis velocity |
| `kernelSize` | `number` | `5` | Kernel size (odd, >= 5) |
| `offset` | `number` | `0` | Blur offset |

### Usage

```ts
// Horizontal motion blur
const blur = new MotionBlurFilter({ velocity: { x: 50, y: 0 } });

// Diagonal motion blur
const blur = new MotionBlurFilter({ velocity: { x: 30, y: 30 } });

// Dynamic: update velocity based on object speed
app.ticker.add(() => {
    blur.velocityX = sprite.velocity.x;
    blur.velocityY = sprite.velocity.y;
});
```

## RadialBlurFilter

**Import:** `pixi-filters/radial-blur`

Rotational blur around a center point.

### Constructor

```ts
new RadialBlurFilter({
    angle: 0,          // rotation angle in degrees
    center: { x: 0, y: 0 },
    kernelSize: 5,     // odd, >= 3
    radius: -1,        // max blur radius; -1 = infinite
});
```

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `angle` | `number` | `0` | Rotation angle in degrees |
| `center` | `PointData` | `{ x: 0, y: 0 }` | Center of rotation |
| `centerX` | `number` | `0` | Center X |
| `centerY` | `number` | `0` | Center Y |
| `kernelSize` | `number` | `5` | Kernel size (odd, >= 3) |
| `radius` | `number` | `-1` | Max blur radius; negative = infinite |

### Usage

```ts
// Spinning wheel effect
const blur = new RadialBlurFilter({
    angle: 45,
    center: { x: 200, y: 200 },
    kernelSize: 11,
});
```

## ZoomBlurFilter

**Import:** `pixi-filters/zoom-blur`

Zoom-in/zoom-out blur from a center point.

### Constructor

```ts
new ZoomBlurFilter({
    strength: 0.1,           // blur intensity
    center: { x: 0, y: 0 },
    innerRadius: 0,          // inner circle exempt from blur
    radius: -1,              // outer radius; -1 = infinite
    maxKernelSize: 32,       // max samples (baked into shader)
});
```

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `strength` | `number` | `0.1` | Blur intensity |
| `center` | `PointData` | `{ x: 0, y: 0 }` | Zoom center |
| `centerX` | `number` | `0` | Center X |
| `centerY` | `number` | `0` | Center Y |
| `innerRadius` | `number` | `0` | Inner radius (no blur inside) |
| `radius` | `number` | `-1` | Outer radius; negative = infinite |
| `maxKernelSize` | `number` | `32` | Max kernel size (baked into shader) |

### Usage

```ts
// Zoom blur from center
const blur = new ZoomBlurFilter({
    strength: 0.3,
    center: { x: 400, y: 300 },
});

// Inner circle stays sharp
const blur = new ZoomBlurFilter({
    strength: 0.2,
    innerRadius: 50,
});
```

## BackdropBlurFilter

**Import:** `pixi-filters/backdrop-blur`

Blurs everything behind the target object. Extends `BlurFilter` from PixiJS core.

### Constructor

```ts
new BackdropBlurFilter({
    // inherits all BlurFilter options:
    strength: { x: 2, y: 2 },
    quality: 4,
    resolution: 1,
    kernelSize: 5,
});
```

### Usage

```ts
// Apply to a container — background behind it gets blurred
container.filters = [new BackdropBlurFilter({ strength: 4 })];

// Frosted glass effect on a semi-transparent overlay
const overlay = new Graphics().rect(0, 0, 400, 300).fill(0xffffff, 0.3);
overlay.filters = [new BackdropBlurFilter({ strength: 8 })];
```

### Gotchas

- Must be applied to a container or an object with content behind it
- On a single sprite with no siblings behind it, there is nothing to blur
- More expensive than standard blur (reads background texture)

## BloomFilter

**Import:** `pixi-filters/bloom`

Gaussian bloom using separable horizontal + vertical blur passes with screen blending.

### Constructor

```ts
new BloomFilter({
    strength: { x: 2, y: 2 },
    quality: 4,
    resolution: 1,
    kernelSize: 5,
});
```

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `strength` | `PointData \| number` | `{ x: 2, y: 2 }` | Blur strength |
| `strengthX` | `number` | `2` | X-axis strength |
| `strengthY` | `number` | `2` | Y-axis strength |
| `quality` | `number` | `4` | Blur quality |
| `resolution` | `number` | `1` | Render resolution |
| `kernelSize` | `number` | `5` | Kernel size (5-15, odd) |

### Usage

```ts
// Soft bloom
const bloom = new BloomFilter({ strength: 4, quality: 4 });

// Strong bloom
const bloom = new BloomFilter({ strength: { x: 8, y: 8 }, quality: 6 });
```

## AdvancedBloomFilter

**Import:** `pixi-filters/advanced-bloom`

Bloom with brightness threshold extraction. Only pixels above `threshold` contribute to bloom. Slower than `BloomFilter`.

### Constructor

```ts
new AdvancedBloomFilter({
    threshold: 0.5,     // brightness threshold (0-1)
    bloomScale: 1,      // bloom intensity
    brightness: 1,      // brightness multiplier
    blur: 8,            // blur strength
    quality: 4,         // blur quality
    pixelSize: { x: 1, y: 1 },
});
```

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `threshold` | `number` | `0.5` | Min brightness to bloom (0-1) |
| `bloomScale` | `number` | `1` | Bloom intensity multiplier |
| `brightness` | `number` | `1` | Brightness of bloom layer |
| `blur` | `number` | `8` | Kawase blur strength |
| `quality` | `number` | `4` | Kawase blur quality |
| `kernels` | `number[]` | — | Custom blur kernels |
| `pixelSize` | `PointData` | `{ x: 1, y: 1 }` | Pixel step size |

### Usage

```ts
// Bloom only very bright pixels
const bloom = new AdvancedBloomFilter({
    threshold: 0.8,
    bloomScale: 1.5,
    blur: 12,
});

// Subtle bloom
const bloom = new AdvancedBloomFilter({
    threshold: 0.3,
    bloomScale: 0.5,
    brightness: 0.8,
});
```
