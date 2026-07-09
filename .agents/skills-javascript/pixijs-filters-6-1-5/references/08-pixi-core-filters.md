# PixiJS Core Filters

Built-in filters from PixiJS itself. These do not require `pixi-filters`.

## BlurFilter

**Import:** `pixi.js` (built-in)

Gaussian blur with configurable strength, quality, resolution, and kernel size.

```ts
import { BlurFilter } from 'pixi.js';

new BlurFilter({
    blur: { x: 2, y: 2 },   // or a single number
    quality: 4,
    resolution: 1,
    kernelSize: 5,
});
```

| Property | Type | Default |
|---|---|---|
| `blur` | `PointData \| number` | `{ x: 2, y: 2 }` |
| `quality` | `number` | `4` |
| `resolution` | `number` | `1` |
| `kernelSize` | `number` | `5` |

## AlphaFilter

**Import:** `pixi.js` (built-in)

Clips rendering to non-transparent areas of the source. Useful for masking.

```ts
import { AlphaFilter } from 'pixi.js';

new AlphaFilter();
```

No configurable properties.

## ColorMatrixFilter

**Import:** `pixi.js` (built-in)

Full 4x4 color matrix transformation. Supports built-in presets.

```ts
import { ColorMatrixFilter } from 'pixi.js';

const f = new ColorMatrixFilter();

// Built-in methods
f.brightness(0.5, false);     // darken
f.contrast(1.5, false);       // increase contrast
f.desaturate(false);          // grayscale
f.saturate(1.5, false);       // oversaturate
f.sepia(false);               // sepia tone
f.tint(0xff0000, 0.5, false); // color tint
f.negative(false);            // invert colors
f.kodachrome(false);          // kodachrome effect
f.polaroid(false);            // polaroid effect
f.predator(4, false);         // predator aliasing
f.lsd(false);                 // LSD effect

// Or set matrix directly
f.matrix = [
    1, 0, 0, 0, 0,
    0, 1, 0, 0, 0,
    0, 0, 1, 0, 0,
    0, 0, 0, 1, 0,
];
```

## DisplacementFilter

**Import:** `pixi.js` (built-in)

Displace pixels using a displacement map texture.

```ts
import { DisplacementFilter, Texture } from 'pixi.js';

const sprite = await Sprite.from('displacement-map.png');
const f = new DisplacementFilter({
    scale: { x: 20, y: 20 },
    map: sprite,
});
```

| Property | Type | Default |
|---|---|---|
| `scale` | `PointData` | `{ x: 20, y: 20 }` |
| `map` | `Sprite` | — |

## NoiseFilter

**Import:** `pixi.js` (built-in)

Random noise overlay.

```ts
import { NoiseFilter } from 'pixi.js';

new NoiseFilter({
    noise: 0.5,  // noise intensity (0-1)
});
```

| Property | Type | Default |
|---|---|---|
| `noise` | `number` | `0.5` |
