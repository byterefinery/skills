# Filters

## Filter Base Class

Filters are GPU shaders applied to containers. They break the render batch, render to a texture, apply the shader, then render back.

### Creating a Custom Filter

```ts
import { Filter, GlProgram, GpuProgram, UniformGroup } from 'pixi.js';

// Shader sources
const vertex = `
    in vec2 aPosition;
    in vec2 aUV;
    out vec2 vUV;
    void main() {
        vUV = aUV;
        gl_Position = vec4(aPosition, 0.0, 1.0);
    }
`;

const fragment = `
    in vec2 vUV;
    out vec4 fragColor;
    uniform sampler2D uTexture;
    uniform float uTime;
    void main() {
        vec4 color = texture(uTexture, vUV);
        fragColor = vec4(color.rgb * uTime, color.a);
    }
`;

const wgsl = `
@vertex
fn mainVert(@builtin(position) position: vec4<f32>,
             @location(0) uv: vec2<f32>) -> @builtin(position) vec4<f32> {
    return position;
}

@fragment
fn mainFrag(@location(0) uv: vec2<f32>) -> @location(0) vec4<f32> {
    return vec4<f32>(1.0, 1.0, 1.0, 1.0);
}
`;

// Create filter
const customFilter = new Filter({
    glProgram: GlProgram.from({ vertex, fragment }),
    gpuProgram: GpuProgram.from({
        vertex: { source: wgsl, entryPoint: 'mainVert' },
        fragment: { source: wgsl, entryPoint: 'mainFrag' },
    }),
    resources: {
        timeUniforms: new UniformGroup({
            uTime: { value: 0, type: 'f32' },
        }),
    },
    resolution: 1,
    padding: 0,
    antialias: false,
    blendMode: 'normal',
});
```

### Filter Options

```ts
interface FilterOptions {
    blendMode?: BLEND_MODES;        // Blend mode when rendering filter
    resolution?: number | 'inherit'; // Render resolution (default: 1)
    padding?: number;               // Extra pixels around bounds (default: 0)
    antialias?: boolean | 'on' | 'off' | 'inherit'; // AA mode
    blendRequired?: boolean;        // Pass background texture to shader
    clipToViewport?: boolean;       // Clip to viewport (default: true)
}
```

### Applying Filters

```ts
// Single filter
sprite.filters = [blurFilter];

// Multiple filters (applied in order)
container.filters = [blurFilter, colorMatrix, displacementFilter];

// Set filter area (optimization)
container.filterArea = new Rectangle(0, 0, 200, 200);

// Remove filters
container.filters = null;
// or
container.filters = [];
```

## BlurFilter

Gaussian blur with configurable strength and quality.

```ts
import { BlurFilter } from 'pixi.js';

// Default settings
const blur = new BlurFilter();

// Custom settings
const blur = new BlurFilter({
    strength: 8,        // Overall blur strength (default: 8)
    strengthX: 4,       // Horizontal blur (overrides strength)
    strengthY: 12,      // Vertical blur (overrides strength)
    quality: 4,         // Quality passes (default: 4, higher = better but slower)
    kernelSize: 5,      // Kernel size: 5, 7, 9, 11, 13, 15 (default: 5)
    resolution: 0.5,    // Lower resolution for performance
    repeatEdgePixels: false,
});

// Update properties
blur.strength = 10;
blur.strengthX = 5;
blur.strengthY = 15;
blur.quality = 2;

// Apply
sprite.filters = [blur];

// Animate blur
app.ticker.add(() => {
    blur.strength = Math.sin(Date.now() / 1000) * 5 + 5;
});
```

## ColorMatrixFilter

5x4 matrix color transformations with convenience methods.

```ts
import { ColorMatrixFilter } from 'pixi.js';

const colorMatrix = new ColorMatrixFilter();

// Brightness (-1 to 2, default: 1)
colorMatrix.brightness(1.2);    // 20% brighter
colorMatrix.brightness(0.8);    // 20% darker

// Contrast (0 to 2, default: 1)
colorMatrix.contrast(1.5);      // More contrast
colorMatrix.contrast(0.5);      // Less contrast

// Saturation (0 to 2, default: 1)
colorMatrix.saturate(0.5);      // Less saturated
colorMatrix.saturate(2);        // More saturated
colorMatrix.desaturate();       // Grayscale (saturation = 0)

// Hue rotation (degrees)
colorMatrix.hue(90);            // Rotate hue 90 degrees

// Preset effects
colorMatrix.gray();             // Grayscale
colorMatrix.sepia();            // Sepia tone
colorMatrix.negative();         // Invert colors
colorMatrix.tint(0xff0000);     // Tint with color
colorMatrix.colorize(0x00ff00); // Colorize

// Chain effects
colorMatrix
    .brightness(1.1)
    .contrast(1.2)
    .saturate(0.8)
    .hue(30);

// Reset
colorMatrix.reset();

// Direct matrix manipulation
colorMatrix.loadMatrix([
    1, 0, 0, 0, 0,
    0, 1, 0, 0, 0,
    0, 0, 1, 0, 0,
    0, 0, 0, 1, 0,
]);

// Alpha blending between original and filtered
colorMatrix.alpha = 0.5;

// Apply
sprite.filters = [colorMatrix];
```

## DisplacementFilter

Displaces pixels using a displacement map texture.

```ts
import { DisplacementFilter } from 'pixi.js';

// Create displacement map
const displacementSprite = new Sprite({ texture: displacementTexture });
displacementSprite.anchor.set(0.5);

// Create filter
const displacement = new DisplacementFilter({
    sprite: displacementSprite,  // Displacement map sprite
    scale: 5,                    // Displacement strength (default: 4)
    resolution: 1,
});

// Apply
container.filters = [displacement];

// Animate displacement map
app.ticker.add(() => {
    displacementSprite.x += 1;
    displacementSprite.y += 0.5;
});

// Update scale
displacement.scale = 10;
```

## NoiseFilter

Adds random noise to the rendered output.

```ts
import { NoiseFilter } from 'pixi.js';

const noise = new NoiseFilter({
    strength: 0.5, // Noise intensity (default: 0.1)
});

container.filters = [noise];

// Animate
app.ticker.add(() => {
    noise.strength = Math.random() * 0.5;
});
```

## AlphaFilter

Adjusts alpha channel of rendered output.

```ts
import { AlphaFilter } from 'pixi.js';

const alphaFilter = new AlphaFilter({
    alpha: 0.5, // Alpha value (0-1)
});

container.filters = [alphaFilter];
```

## PassthroughFilter

No-op filter. Useful as placeholder or for testing.

```ts
import { PassthroughFilter } from 'pixi.js';

const passthrough = new PassthroughFilter();
container.filters = [passthrough];
```

## Blend Mode Filters

Advanced blend mode effects via shaders.

```ts
import { BlendModeFilter } from 'pixi.js';

// Requires advanced blend modes
import 'pixi.js/advanced-blend-modes';

const blendFilter = new BlendModeFilter({
    blendMode: 'overlay',
    blendSource: backgroundTexture,
});

container.filters = [blendFilter];
```

## MaskFilter

Filter-based masking (alternative to `container.mask`).

```ts
import { MaskFilter } from 'pixi.js';

const maskFilter = new MaskFilter(maskSprite);
container.filters = [maskFilter];
```

## AlphaFilter

Applies uniform alpha to a container (flattens alpha instead of applying per-child).

```ts
import { AlphaFilter } from 'pixi.js';

const alphaFilter = new AlphaFilter({
    alpha: 0.5, // Alpha value (0-1)
});

container.filters = [alphaFilter];
```

## PassthroughFilter

No-op filter. Useful as placeholder or for testing.

```ts
import { PassthroughFilter } from 'pixi.js';

const passthrough = new PassthroughFilter();
container.filters = [passthrough];
```

## Blend Mode Filters

Advanced blend mode effects via shaders. Requires `import 'pixi.js/advanced-blend-modes'`.

```ts
import 'pixi.js/advanced-blend-modes';
import {
    ColorBurnBlend,
    ColorDodgeBlend,
    DarkenBlend,
    DivideBlend,
    HardMixBlend,
    LinearBurnBlend,
    LinearDodgeBlend,
    LinearLightBlend,
    PinLightBlend,
    SubtractBlend,
} from 'pixi.js';

container.filters = [new HardMixBlend()];
```

| Filter Class       | Description                                        |
|---|---|
| `ColorBurnBlend`   | Darkens the base color to reflect the blend color |
| `ColorDodgeBlend`  | Brightens the base color |
| `DarkenBlend`      | Retains the darkest color components |
| `DivideBlend`      | Divides the base color by the blend color |
| `HardMixBlend`     | High-contrast blend |
| `LinearBurnBlend`  | Darkens using linear formula |
| `LinearDodgeBlend` | Lightens using linear formula |
| `LinearLightBlend` | Combination of linear dodge and burn |
| `PinLightBlend`    | Selective replacement of colors |
| `SubtractBlend`    | Subtracts the blend color from base |

## Filter Performance Tips

- **Group filtered objects** — one filter on a parent container is much faster than many filters on children
- **Use `filterArea`** — limits filter to a specific region, reducing render target size
- **Lower `resolution`** — use 0.5 or 0.25 for blurs (quality loss is minimal)
- **Reduce `quality`** on BlurFilter — quality 2 is often sufficient
- **Avoid filters in render loop** — update filter uniforms, don't recreate filters
- **Use `padding`** for blurs — prevents edge clipping (padding = blur strength)
- **Prefer `container.mask`** over MaskFilter for simple masks (no extra render pass)
- **Batch-friendly** — filters break batching; minimize filter count
- **Use `antialias: false`** unless needed — AA adds overhead
