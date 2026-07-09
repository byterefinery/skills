# Distortion Filters

Filters that warp, bend, or displace pixels.

## BulgePinchFilter

**Import:** `pixi-filters/bulge-pinch`

Circular bulge (magnify) or pinch (shrink) distortion.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `center` | `PointData` | `{ x: 0.5, y: 0.5 }` | Center in normalized coords (0-1) |
| `centerX` | `number` | `0.5` | Center X |
| `centerY` | `number` | `0.5` | Center Y |
| `radius` | `number` | `100` | Effect radius in pixels |
| `strength` | `number` | `1` | -1=pinch, 0=none, 1=bulge |

### Usage

```ts
// Magnifying glass effect
const f = new BulgePinchFilter({
    center: { x: 0.5, y: 0.5 },
    radius: 150,
    strength: 1,
});

// Pinch (inverse)
const f = new BulgePinchFilter({ strength: -1 });

// Animate position
app.ticker.add(() => {
    f.centerX = mouse.x / app.screen.width;
    f.centerY = mouse.y / app.screen.height;
});
```

## TwistFilter

**Import:** `pixi-filters/twist`

Circular twist distortion within a radius.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `padding` | `number` | `20` | Filter area padding |
| `radius` | `number` | `200` | Twist radius in pixels |
| `angle` | `number` | `4` | Twist angle in radians |
| `offset` | `PointData` | `{ x: 0, y: 0 }` | Center offset |
| `offsetX` | `number` | `0` | Center X offset |
| `offsetY` | `number` | `0` | Center Y offset |

### Usage

```ts
// Swirl effect
const f = new TwistFilter({
    radius: 300,
    angle: Math.PI,
    offset: { x: 400, y: 300 },
});

// Animate twist
app.ticker.add(() => {
    f.angle = (f.angle + 0.05) % (Math.PI * 2);
});
```

## TiltShiftFilter

**Import:** `pixi-filters/tilt-shift`

Simulates depth of field by blurring between two points. Uses two internal axis filters (horizontal + vertical passes).

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `blur` | `number` | `100` | Blur strength |
| `gradientBlur` | `number` | `600` | Gradient transition blur |
| `start` | `PointData` | `{ x: 0, y: height/2 }` | Start point |
| `startX` | `number` | `0` | Start X |
| `startY` | `number` | `height/2` | Start Y |
| `end` | `PointData` | `{ x: width, y: height/2 }` | End point |
| `endX` | `number` | `width` | End X |
| `endY` | `number` | `height/2` | End Y |

### Usage

```ts
// Horizontal tilt shift
const f = new TiltShiftFilter({
    blur: 200,
    gradientBlur: 800,
    start: { x: 0, y: 300 },
    end: { x: 800, y: 300 },
});

// Vertical tilt shift
const f = new TiltShiftFilter({
    blur: 150,
    start: { x: 400, y: 0 },
    end: { x: 400, y: 600 },
});
```

## RGBSplitFilter

**Import:** `pixi-filters/rgb-split`

Chromatic aberration by independently offsetting the R, G, and B channels.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `red` | `PointData` | `{ x: -10, y: 0 }` | Red channel offset |
| `redX` | `number` | `-10` | Red X offset |
| `redY` | `number` | `0` | Red Y offset |
| `green` | `PointData` | `{ x: 0, y: 10 }` | Green channel offset |
| `greenX` | `number` | `0` | Green X offset |
| `greenY` | `number` | `10` | Green Y offset |
| `blue` | `PointData` | `{ x: 0, y: 0 }` | Blue channel offset |
| `blueX` | `number` | `0` | Blue X offset |
| `blueY` | `number` | `0` | Blue Y offset |

### Usage

```ts
// Classic chromatic aberration
const f = new RGBSplitFilter({
    red: { x: -8, y: 0 },
    green: { x: 0, y: 0 },
    blue: { x: 8, y: 0 },
});

// Subtle edge fringing
const f = new RGBSplitFilter({
    red: { x: -2, y: 0 },
    blue: { x: 2, y: 0 },
});

// Animate for dynamic effect
app.ticker.add(() => {
    f.redX = Math.sin(Date.now() / 1000) * 10;
    f.blueX = Math.cos(Date.now() / 1000) * 10;
});
```

## ShockwaveFilter

**Import:** `pixi-filters/shockwave`

Pond ripple / blast wave radial distortion.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `center` | `PointData` | `{ x: 0, y: 0 }` | Origin point |
| `centerX` | `number` | `0` | Center X |
| `centerY` | `number` | `0` | Center Y |
| `speed` | `number` | `500` | Ripple speed (px/s) |
| `amplitude` | `number` | `30` | Ripple displacement |
| `wavelength` | `number` | `160` | Ripple wavelength |
| `brightness` | `number` | `1` | Ripple brightness |
| `radius` | `number` | `-1` | Max radius; negative = infinite |
| `time` | `number` | `0` | Elapsed time |

### Usage

```ts
const f = new ShockwaveFilter({
    center: { x: 400, y: 300 },
    speed: 400,
    amplitude: 20,
});

// Animate shockwave
app.ticker.add((delta) => {
    f.time += delta / 1000;
});
```

## ReflectionFilter

**Import:** `pixi-filters/reflection`

Water reflection with wave distortion. Can mirror the image or apply waves only.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `mirror` | `boolean` | `true` | Reflect the image |
| `boundary` | `number` | `0.5` | Reflection boundary (0-1) |
| `amplitude` | `[number, number]` | `[0, 20]` | Wave amplitude range |
| `amplitudeStart` | `number` | `0` | Start amplitude |
| `amplitudeEnd` | `number` | `20` | End amplitude |
| `waveLength` | `[number, number]` | `[30, 100]` | Wavelength range |
| `wavelengthStart` | `number` | `30` | Start wavelength |
| `wavelengthEnd` | `number` | `100` | End wavelength |
| `alpha` | `[number, number]` | `[1, 1]` | Alpha range |
| `alphaStart` | `number` | `1` | Start alpha |
| `alphaEnd` | `number` | `1` | End alpha |
| `time` | `number` | `0` | Animation time |

### Usage

```ts
// Water reflection
const f = new ReflectionFilter({
    mirror: true,
    boundary: 0.5,
    amplitude: [0, 15],
    waveLength: [40, 80],
});

// Waves only (no mirror)
const f = new ReflectionFilter({
    mirror: false,
    amplitude: [5, 25],
});

// Animate waves
app.ticker.add((delta) => {
    f.time += delta / 1000;
});
```
