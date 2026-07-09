# Utility Filters

Special-purpose filters for shadows and lighting.

## DropShadowFilter

**Import:** `pixi-filters/drop-shadow`

Drop shadow using Kawase blur. Supports color, offset, blur, and shadow-only mode.

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `offset` | `PointData` | `{ x: 4, y: 4 }` | Shadow offset |
| `offsetX` | `number` | `4` | X offset |
| `offsetY` | `number` | `4` | Y offset |
| `color` | `ColorSource` | `0x000000` | Shadow color |
| `alpha` | `number` | `0.5` | Shadow opacity |
| `shadowOnly` | `boolean` | `false` | Hide content, show only shadow |
| `blur` | `number` | `2` | Blur strength |
| `quality` | `number` | `3` | Blur quality (passes) |
| `kernels` | `number[]` | — | Custom blur kernels |
| `pixelSize` | `PointData` | `{ x: 1, y: 1 }` | Pixel step size |
| `pixelSizeX` | `number` | `1` | X pixel step |
| `pixelSizeY` | `number` | `1` | Y pixel step |
| `resolution` | `number` | `1` | Render resolution |

### Usage

```ts
// Standard drop shadow
const f = new DropShadowFilter({
    offset: { x: 5, y: 5 },
    color: 0x000000,
    alpha: 0.5,
    blur: 4,
});

// Colored shadow
const f = new DropShadowFilter({
    offset: { x: 3, y: 3 },
    color: 0xff0000,
    alpha: 0.3,
    blur: 2,
});

// Shadow only (no content)
const f = new DropShadowFilter({
    offset: { x: 8, y: 8 },
    shadowOnly: true,
    blur: 6,
});

// Soft large shadow
const f = new DropShadowFilter({
    offset: { x: 0, y: 10 },
    blur: 10,
    quality: 5,
    alpha: 0.3,
});
```

## SimpleLightmapFilter

**Import:** `pixi-filters/simple-lightmap`

Apply a lightmap texture for dynamic lighting effects. Requires a lightmap texture (typically a canvas with radial gradients drawn on it).

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `lightMap` | `Texture` | `Texture.WHITE` | The lightmap texture |
| `color` | `ColorSource` | `0x000000` | Ambient color |
| `alpha` | `number` | `1` | Alpha multiplier |

### Usage

```ts
// Create a lightmap canvas
const lightCanvas = document.createElement('canvas');
lightCanvas.width = 800;
lightCanvas.height = 600;
const ctx = lightCanvas.getContext('2d');

// Draw a radial gradient (light source)
const gradient = ctx.createRadialGradient(400, 300, 0, 400, 300, 200);
gradient.addColorStop(0, 'rgba(255, 255, 200, 1)');
gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
ctx.fillStyle = gradient;
ctx.fillRect(0, 0, 800, 600);

const lightMapTexture = Texture.from(lightCanvas);

const f = new SimpleLightmapFilter({
    lightMap: lightMapTexture,
    color: 0x333333,
    alpha: 1,
});

// Apply to a container
container.filters = [f];
container.filterArea = new Rectangle(0, 0, 800, 600);

// Animate light position
app.ticker.add(() => {
    ctx.clearRect(0, 0, 800, 600);
    const x = 400 + Math.sin(Date.now() / 1000) * 200;
    const y = 300 + Math.cos(Date.now() / 1000) * 150;
    const gradient = ctx.createRadialGradient(x, y, 0, x, y, 250);
    gradient.addColorStop(0, 'rgba(255, 255, 200, 1)');
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 800, 600);
    lightMapTexture.source.update();
});
```

### Gotchas

- **`filterArea` is required** on the target display object, or lightmap coordinates will be wrong
- The lightmap texture dimensions should match the `filterArea` dimensions
- After modifying the lightmap canvas, call `texture.source.update()` to push changes to GPU
