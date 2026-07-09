# Atmospheric Filters

Filters that create ambient effects: light rays, noise, film grain, CRT, glitch.

## GodrayFilter

**Import:** `pixi-filters/godray`

God rays / light shafts using fractal noise. Simulates light streaming through openings.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `angle` | `number` | `30` | Ray angle in degrees (when parallel) |
| `parallel` | `boolean` | `true` | Use parallel rays (true) or focal point (false) |
| `center` | `PointData` | `{ x: 0, y: 0 }` | Focal point (when not parallel) |
| `centerX` | `number` | `0` | Focal point X |
| `centerY` | `number` | `0` | Focal point Y |
| `gain` | `number` | `0.5` | Effect intensity (0-1) |
| `lacunarity` | `number` | `2.5` | Noise density (more rays with higher values) |
| `time` | `number` | `0` | Animation time |
| `alpha` | `number` | `1` | Ray opacity |

### Usage

```ts
// Parallel rays from top-right
const f = new GodrayFilter({
    angle: 30,
    gain: 0.6,
    lacunarity: 3,
});

// Rays from a focal point
const f = new GodrayFilter({
    parallel: false,
    center: { x: 400, y: 100 },
    gain: 0.5,
});

// Animate
app.ticker.add((delta) => {
    f.time += delta / 1000;
});
```

## SimplexNoiseFilter

**Import:** `pixi-filters/simplex-noise`

Multiply simplex noise with texture data. Useful for organic textures, distortion, or grain.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `strength` | `number` | `0.5` | Noise strength |
| `noiseScale` | `number` | `10` | Noise scale (frequency) |
| `offsetX` | `number` | `0` | Horizontal noise offset |
| `offsetY` | `number` | `0` | Vertical noise offset |
| `offsetZ` | `number` | `0` | Depth offset (for animation) |
| `step` | `number` | `-1` | Threshold for blocky effect (> 0 enables) |

### Usage

```ts
// Subtle noise overlay
const f = new SimplexNoiseFilter({ strength: 0.3, noiseScale: 15 });

// Animated noise
app.ticker.add((delta) => {
    f.offsetZ += delta / 1000;
});

// Blocky/quantized noise
const f = new SimplexNoiseFilter({
    strength: 0.5,
    noiseScale: 8,
    step: 0.5,
});
```

## OldFilmFilter

**Import:** `pixi-filters/old-film`

Vintage film effect combining sepia, noise, scratches, and vignette.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `sepia` | `number` | `0.3` | Sepia saturation (0 = none, 1 = full) |
| `noise` | `number` | `0.3` | Film grain intensity (0-1) |
| `noiseSize` | `number` | `1` | Grain particle size |
| `scratch` | `number` | `0.5` | Scratch frequency |
| `scratchDensity` | `number` | `0.3` | Scratch density |
| `scratchWidth` | `number` | `1` | Scratch line width |
| `vignetting` | `number` | `0.3` | Vignette radius |
| `vignettingAlpha` | `number` | `1` | Vignette opacity |
| `vignettingBlur` | `number` | `0.3` | Vignette blur |
| `seed` | `number` | `0` | Random seed |

### Usage

```ts
// Classic old film
const f = new OldFilmFilter({
    sepia: 0.5,
    noise: 0.4,
    scratch: 0.3,
    vignetting: 0.4,
});

// Subtle vintage
const f = new OldFilmFilter({
    sepia: 0.2,
    noise: 0.1,
    scratch: 0.1,
});
```

## CRTFilter

**Import:** `pixi-filters/crt`

CRT monitor simulation: scanlines, curvature, noise, and vignette.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `curvature` | `number` | `1` | Screen curvature |
| `lineWidth` | `number` | `1` | Scanline width |
| `lineContrast` | `number` | `0.25` | Scanline contrast |
| `verticalLine` | `boolean` | `false` | Vertical (true) or horizontal (false) lines |
| `time` | `number` | `0` | Animation time |
| `noise` | `number` | `0` | Static noise intensity |
| `noiseSize` | `number` | `1` | Noise particle size |
| `seed` | `number` | `0` | Random seed |
| `vignetting` | `number` | `0.3` | Vignette radius |
| `vignettingAlpha` | `number` | `1` | Vignette opacity |
| `vignettingBlur` | `number` | `0.3` | Vignette blur |

### Usage

```ts
// Retro CRT
const f = new CRTFilter({
    curvature: 1.5,
    lineWidth: 2,
    lineContrast: 0.4,
    noise: 0.1,
    vignetting: 0.5,
});

// Scanlines only
const f = new CRTFilter({
    lineWidth: 2,
    lineContrast: 0.5,
    noise: 0,
    vignetting: 0,
});

// Animate scanlines
app.ticker.add((delta) => {
    f.time += delta / 1000;
});
```

## GlitchFilter

**Import:** `pixi-filters/glitch`

Digital glitch effect with displacement bands, RGB channel offset, and configurable fill modes.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `slices` | `number` | `5` | Number of horizontal bands |
| `offset` | `number` | `100` | Max displacement amount |
| `direction` | `number` | `0` | Displacement angle in degrees |
| `fillMode` | `number` | `0` | Fill mode for displaced areas |
| `seed` | `number` | `0` | Random seed |
| `average` | `boolean` | `false` | Equal band sizes (true) or varied (false) |
| `minSize` | `number` | `8` | Minimum band size |
| `sampleSize` | `number` | `512` | Displacement map height |
| `red` | `PointData` | `{ x: 0, y: 0 }` | Red channel offset |
| `green` | `PointData` | `{ x: 0, y: 0 }` | Green channel offset |
| `blue` | `PointData` | `{ x: 0, y: 0 }` | Blue channel offset |

### Fill Modes

```ts
TRANSPARENT = 0  // Transparent gaps
ORIGINAL = 1     // Fill with original pixels
LOOP = 2         // Wrap around
CLAMP = 3        // Clamp to edge
MIRROR = 4       // Mirror reflection
```

### Methods

- `refresh()` — randomize slice sizes and offsets
- `shuffle()` — shuffle slice order
- `redraw()` — redraw the displacement texture

### Usage

```ts
// Basic glitch
const f = new GlitchFilter({
    slices: 8,
    offset: 80,
    fillMode: 0, // TRANSPARENT
});

// RGB split glitch
const f = new GlitchFilter({
    slices: 5,
    offset: 50,
    red: { x: 5, y: 0 },
    green: { x: 0, y: 0 },
    blue: { x: -5, y: 0 },
});

// Periodic glitch (trigger refresh randomly)
setInterval(() => {
    if (Math.random() < 0.3) {
        f.refresh();
    }
}, 200);

// Continuous glitch animation
app.ticker.add(() => {
    f.seed = Math.random();
    f.refresh();
});
```
