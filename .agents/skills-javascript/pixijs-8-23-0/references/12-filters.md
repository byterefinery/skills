# Filters

## Contents

- [filters](#filters-1)
  - [Built-in filters](#built-in-filters)
  - [Custom filter](#custom-filter)
  - [Filter options](#filter-options)
  - [Community filters (pixi-filters)](#community-filters-pixi-filters)
- [Multi-pass filters](#multi-pass-filters)
- [WGSL filter skeleton](#wgsl-filter-skeleton)

## filters

Built-in filters, custom GLSL/WGSL filters, filter options and `pixi-filters`.

`container.filters` returns a frozen array (or `undefined` if never set). Add, remove or reorder by assigning a new array: `c.filters = [...(c.filters ?? []), blur]`. `c.filters.push(blur)` is a type error and throws "object is not extensible". Filters in an array run in array order.

### Built-in filters

```ts
import { AlphaFilter, BlurFilter, ColorMatrixFilter, DisplacementFilter, NoiseFilter, Assets, Sprite } from "pixi.js";
import type { Application, Texture } from "pixi.js";

declare const app: Application;
declare const sprite: Sprite;

// uniform transparency for a group, without per-child layering
const alpha = new AlphaFilter({ alpha: 0.5 });

// strengthX/strengthY split the axes; reading `strength` throws when they differ.
// kernelSize must be odd (5, 7, 9, ... 15)
const blur = new BlurFilter({ strength: 4, quality: 4, kernelSize: 5 });
blur.repeatEdgePixels = true; // property only, not a constructor option

const colorMatrix = new ColorMatrixFilter();
colorMatrix.brightness(1.5, false); // false replaces the matrix
colorMatrix.contrast(0.5, true); // true combines, and the NEW matrix runs first: contrast, then brightness
colorMatrix.alpha = 0.7; // mix between original and transformed

const mapTexture = await Assets.load<Texture>("displacement_map.png");
mapTexture.source.addressMode = "repeat"; // lets the map scroll without edges
const map = new Sprite(mapTexture);
app.stage.addChild(map); // required: the filter reads the map's world transform
const displacement = new DisplacementFilter({ sprite: map, scale: { x: 20, y: 10 } }); // scale: number or PointData, default 20
displacement.scale.x = 30; // `scale` is a getter-only Point; mutate x/y

// seed picks the pattern; the same seed reproduces it
const noise = new NoiseFilter({ noise: 0.5, seed: Math.random() });

sprite.filters = [blur, colorMatrix];
```

**ColorMatrixFilter order.** `cm.A(..., false); cm.B(..., true);` applies B to the colour first and A second. For "A then B", call `cm.B(..., false); cm.A(..., true);`, or use two filters `[a, b]`. Other presets: `tint`, `hue`, `saturate`, `desaturate`, `greyscale`/`grayscale`, `blackAndWhite`, `negative`, `sepia`, `technicolor`, `polaroid`, `kodachrome`, `browni`, `vintage`, `colorTone`, `night`, `predator`, `lsd`, `reset`; raw access through `cm.matrix` (20 elements).

**DisplacementFilter map must be in the scene.** A detached map sprite's world transform is never updated, so moving it (`map.x += 1` each tick) never moves the distortion. The filter sets the map's `renderable` to false, so adding it to the stage doesn't draw it. Animate by moving the map sprite. The filter reads only the map's `worldTransform` and `texture`, so the map must be a `Sprite`: a `TilingSprite`'s `tilePosition` is never read.

### Custom filter

There is no default vertex shader: `gl.vertex` is required. Pass the exported `defaultFilterVert`. A fragment-only `Filter.from({ gl: { fragment } })` fails type-checking and throws "Cannot read properties of undefined (reading 'substring')".

```ts
import { Filter, defaultFilterVert } from "pixi.js";
import type { Application, Sprite } from "pixi.js";

declare const app: Application;
declare const sprite: Sprite;

const fragment = `
in vec2 vTextureCoord;
out vec4 finalColor;

uniform sampler2D uTexture;
uniform highp vec4 uInputSize;
uniform highp vec4 uOutputFrame;
uniform highp vec4 uInputClamp;
uniform float uTime;

void main() {
  // 0..1 across the filtered area (vTextureCoord is not)
  vec2 local = vTextureCoord * uInputSize.xy / uOutputFrame.zw;
  vec2 offset = vec2(sin(local.y * 20.0 + uTime) * 4.0, 0.0) * uInputSize.zw; // 4px sway
  finalColor = texture(uTexture, clamp(vTextureCoord + offset, uInputClamp.xy, uInputClamp.zw));
}
`;

const filter = Filter.from({
  gl: { vertex: defaultFilterVert, fragment },
  resources: {
    timeUniforms: { uTime: { value: 0, type: "f32" } },
  },
});

sprite.filters = [filter];

app.ticker.add((ticker) => {
  filter.resources.timeUniforms.uniforms.uTime += 0.04 * ticker.deltaTime;
});
```

`Filter.from` is Filter's own static (not the inherited `Shader.from`) and returns a `Filter`. The long form is `new Filter({ glProgram: GlProgram.from({ vertex: defaultFilterVert, fragment }), resources })`.

Porting a v7 filter: `new Filter(vertex, fragment, uniforms)` becomes the options object above, `filter.uniforms.x` becomes `filter.resources.{group}.uniforms.x`, and in GLSL `uSampler` becomes `uTexture` (v7's name is not bound in v8), `varying` becomes `in`, `texture2D` becomes `texture`, `gl_FragColor` becomes `out vec4 finalColor`.

Filter shader rules:

- **`uTexture` holds premultiplied colour, and `finalColor` is composited as premultiplied.** Keep `rgb` at or below `a`: invert with `vec4(c.a - c.rgb, c.a)`, not `vec4(1.0 - c.rgb, c.a)`, which turns transparent pixels inside the filter area white. For straight-colour maths, use `c.rgb / max(c.a, 1e-4)` and multiply the result by `a` again before writing it.
- **Output is clipped to the object's bounds plus `padding`** (default 0). A shader that draws outside the shape (glow, outline, shadow, wave offset) needs `padding` of at least its reach in pixels, or the effect stops at the bounds.
- **`vTextureCoord` is not 0..1 over the object.** The input texture comes from a pool and is larger than the filtered area, so `vTextureCoord` runs from 0 to `uOutputFrame.zw / uInputSize.xy`; a gradient driven by it stops short and changes with the object's size. For a coordinate normalised across the filtered area (object bounds plus padding) use `vTextureCoord * uInputSize.xy / uOutputFrame.zw`. Sample with `vTextureCoord` itself, and clamp offset samples to `uInputClamp` so they don't read past the filtered area.
- **Declare `uInputSize`, `uOutputFrame` and `uOutputTexture` as `uniform highp vec4` in the fragment shader.** The vertex shader declares them highp and GlProgram gives the fragment stage mediump by default; the mismatch fails to link ("Precisions of uniform ... differ") and the filtered object disappears.
- `filterVertexPosition()` and `filterTextureCoord()` are functions inside `defaultFilterVert`; the fragment shader can't call them.
- Uniforms go in `resources` with explicit types. A texture is its own resource: `uMap: texture.source`, keyed by the sampler name.

Global filter uniforms, all `vec4`, set by the filter system for every pass:

| Uniform | Value |
| --- | --- |
| `uInputSize` | input texture size `(w, h, 1/w, 1/h)`; `zw` is one pixel in UV units |
| `uOutputFrame` | filtered area `(x, y, w, h)` in the output |
| `uInputClamp` | valid UV range `(minU, minV, maxU, maxV)` of the input |
| `uInputPixel` | input size in physical pixels (resolution applied) |
| `uOutputTexture` | output target size, used by the vertex shader |

A filter that needs a scratch texture or combines two passes (bloom: blur a copy, add it to the original) overrides `apply()` and borrows textures from `TexturePool`; v7's `filterManager.getFilterTexture()` is gone. Read [filters/multi-pass.md](12-filters.md) before writing one.

#### WebGPU needs a WGSL program too

**If any enabled filter on a container has no program for the active renderer, every filter on that container is skipped, with no error.** `Application` picks WebGL by default, so gl-only filters work until the app runs with `preference: "webgpu"`. Either force `preference: "webgl"`, or pass `gpu: { vertex: { source, entryPoint }, fragment: { source, entryPoint } }` as well. There is no default WGSL vertex shader: one WGSL source supplies both entry points and declares the filter globals at `@group(0)`. Copy the skeleton in [filters/wgsl-filter.md](12-filters.md).

#### Sampling the content behind the filter

Set `blendRequired: true` and declare `uniform sampler2D uBackTexture;`; PixiJS copies the destination pixels into it before running the filter:

```ts
import { Filter, defaultFilterVert } from "pixi.js";

const multiplyBehind = Filter.from({
  gl: {
    vertex: defaultFilterVert,
    fragment: `
      in vec2 vTextureCoord;
      out vec4 finalColor;
      uniform sampler2D uTexture;
      uniform sampler2D uBackTexture;

      void main() {
        finalColor = texture(uTexture, vTextureCoord) * texture(uBackTexture, vTextureCoord);
      }
    `,
  },
  resources: {},
  blendRequired: true,
});
```

On WebGL this needs `await app.init({ useBackBuffer: true })`; without it PixiJS skips **every** filter on that container, including the other filters in the array (dev builds warn every frame). WebGPU always has the back buffer. `blendRequired` costs an extra GPU copy every frame, so enable it only when the shader reads `uBackTexture`. Community filters that set it need the same init option.

### Filter options

A `filters` array renders every pass at the **lowest** resolution among its enabled filters (`'inherit'` counts as the target's resolution), so one filter left at the default `1` makes the whole chain low-res on a high-DPI screen. Padding adds up across the list.

```ts
import { Filter, GlProgram, Rectangle, defaultFilterVert } from "pixi.js";
import type { Application, Container, Sprite } from "pixi.js";

declare const fragment: string;
declare const app: Application;
declare const container: Container;
declare const sprite1: Sprite;
declare const sprite2: Sprite;

const filter = new Filter({
  glProgram: GlProgram.from({ vertex: defaultFilterVert, fragment }),
  resources: {},
  resolution: "inherit", // default 1, even on a resolution-2 renderer; 'inherit' matches the target
  padding: 10, // default 0
  antialias: "off", // default 'off'. 'on' | 'off' | 'inherit'
  blendMode: "normal", // the filtered container composites with its LAST filter's blendMode
  blendRequired: false, // default false
  clipToViewport: true, // default true
});

// skips per-frame bounds measurement; local coordinates of the container, content outside is clipped
container.filterArea = new Rectangle(0, 0, 800, 600);

// a filter covers only its container's bounds (plus padding), so a full-screen effect on the stage needs this
app.stage.filterArea = app.screen;

filter.enabled = false; // toggle without rebuilding the array

// one instance can be shared
sprite1.filters = [filter];
sprite2.filters = [filter];
```

`container.blendMode` on a filtered container only changes how its children draw into the filter input; an additive glow is `new BlurFilter({ strength: 8, blendMode: "add" })`. See [blend-modes](13-blend-modes.md#filtered-containers).

### Community filters (pixi-filters)

v8 imports community filters from `pixi-filters/{name}`; the `@pixi/filter-*` packages are v7 only.

```ts
import { AdjustmentFilter } from "pixi-filters/adjustment";
import { GlowFilter } from "pixi-filters/glow";
import type { Sprite } from "pixi.js";

declare const sprite: Sprite;

sprite.filters = [new AdjustmentFilter({ brightness: 1.2, contrast: 1.1 }), new GlowFilter({ distance: 15, outerStrength: 2 })];
```

Advanced blend modes (`color-burn`, `overlay`, ...) also run as filters: [blend-modes](13-blend-modes.md#advanced-blend-modes).


---

## Multi-pass filters

Override `apply()` when one filter needs a scratch texture or combines several passes. This bloom blurs a copy of the input and adds it back over the original:

```ts
import { BlurFilter, Filter, RendererType, Texture, TexturePool, defaultFilterVert } from "pixi.js";
import type { FilterSystem, RenderSurface } from "pixi.js";

const combineFragment = `
in vec2 vTextureCoord;
out vec4 finalColor;
uniform sampler2D uTexture;
uniform sampler2D uBlurred;

void main() {
  finalColor = texture(uTexture, vTextureCoord) + texture(uBlurred, vTextureCoord);
}`;

class BloomFilter extends Filter {
  private readonly blur = new BlurFilter({ strength: 8 });
  private readonly combine = Filter.from({
    gl: { vertex: defaultFilterVert, fragment: combineFragment },
    resources: { uBlurred: Texture.EMPTY.source },
  });

  constructor() {
    // no program of its own, so declare which renderers the inner passes support
    super({ compatibleRenderers: RendererType.WEBGL, resources: {} });
    this.padding = this.blur.padding;
  }

  public override apply(filterManager: FilterSystem, input: Texture, output: RenderSurface, clearMode: boolean): void {
    const blurred = TexturePool.getSameSizeTexture(input);

    this.blur.apply(filterManager, input, blurred, true);
    this.combine.resources.uBlurred = blurred.source;
    this.combine.blendMode = this.blendMode;
    filterManager.applyFilter(this.combine, input, output, clearMode);

    TexturePool.returnTexture(blurred);
  }
}

// sprite.filters = [new BloomFilter()];
```

Rules:

- **A filter with no program of its own is skipped unless it sets `compatibleRenderers`.** It defaults to the renderers its programs cover, which is none here. Use `RendererType.WEBGL | RendererType.WEBGPU` only when every inner pass has both programs.
- Run a pass with `innerFilter.apply(filterManager, input, output, clear)` (built-in filters such as `BlurFilter` run their own passes) or `filterManager.applyFilter(shaderFilter, input, output, clear)` for a shader-only filter.
- Borrow scratch textures with `TexturePool.getSameSizeTexture(input)` and give each back with `TexturePool.returnTexture()` in the same `apply()`. A same-size texture shares `vTextureCoord` with `input`, so pass it as a resource (`.source`) and sample it at `vTextureCoord`. v7's `filterManager.getFilterTexture()` / `returnFilterTexture()` don't exist.
- Only the outer filter's `padding`, `resolution` and `blendMode` count for the container. Copy the padding the inner passes need, and give the last pass `this.blendMode` so the filter's blend mode is honoured; intermediate passes write with `"normal"`.


---

## WGSL filter skeleton

A filter needs a `gpu` program to run on WebGPU ([filters](12-filters.md#webgpu-needs-a-wgsl-program-too)). There is no default WGSL vertex shader, so one WGSL source supplies both entry points. This desaturates by `uStrength` (0 = unchanged, 1 = grey):

```ts
import { Filter, defaultFilterVert } from "pixi.js";

declare const glFragment: string; // the GLSL version of the same effect

const source = /* wgsl */ `
struct GlobalFilterUniforms {
  uInputSize: vec4<f32>,
  uInputPixel: vec4<f32>,
  uInputClamp: vec4<f32>,
  uOutputFrame: vec4<f32>,
  uGlobalFrame: vec4<f32>,
  uOutputTexture: vec4<f32>,
};
struct GreyUniforms { uStrength: f32 };

@group(0) @binding(0) var<uniform> gfu: GlobalFilterUniforms;
@group(0) @binding(1) var uTexture: texture_2d<f32>;
@group(0) @binding(2) var uSampler: sampler;
@group(1) @binding(0) var<uniform> greyUniforms: GreyUniforms;

struct VSOutput {
  @builtin(position) position: vec4<f32>,
  @location(0) uv: vec2<f32>,
};

@vertex
fn mainVertex(@location(0) aPosition: vec2<f32>) -> VSOutput {
  var position = aPosition * gfu.uOutputFrame.zw + gfu.uOutputFrame.xy;
  position.x = position.x * (2.0 / gfu.uOutputTexture.x) - 1.0;
  position.y = position.y * (2.0 * gfu.uOutputTexture.z / gfu.uOutputTexture.y) - gfu.uOutputTexture.z;
  return VSOutput(vec4(position, 0.0, 1.0), aPosition * (gfu.uOutputFrame.zw * gfu.uInputSize.zw));
}

@fragment
fn mainFragment(@location(0) uv: vec2<f32>) -> @location(0) vec4<f32> {
  let c = textureSample(uTexture, uSampler, uv);
  let luma = dot(c.rgb, vec3(0.299, 0.587, 0.114));
  return vec4(mix(c.rgb, vec3(luma), greyUniforms.uStrength), c.a);
}`;

const grey = Filter.from({
  gl: { vertex: defaultFilterVert, fragment: glFragment },
  gpu: {
    vertex: { source, entryPoint: "mainVertex" },
    fragment: { source, entryPoint: "mainFragment" },
  },
  resources: { greyUniforms: { uStrength: { value: 1, type: "f32" } } },
});

grey.resources.greyUniforms.uniforms.uStrength = 0.5;
```

Rules:

- Keep `@group(0)` exactly as shown: the filter system binds the globals, the input texture and its sampler there. The struct must list all six fields in this order.
- Your uniform groups start at `@group(1)`. Each resource key must equal the WGSL variable name (`greyUniforms`); a key that matches no binding is never bound.
- `uv` has the same range as GLSL `vTextureCoord`: it is not 0..1 across the object. Normalise with `uv * gfu.uInputSize.xy / gfu.uOutputFrame.zw`.
- A `blendRequired` filter reads the content behind it from `@group(0) @binding(3) var uBackTexture: texture_2d<f32>;`.
- An extra texture is a resource keyed by its variable name, with its sampler under another key: `resources: { uMap: texture.source, uMapSampler: texture.source.style }`, declared after your uniforms in the same group: `@group(1) @binding(1) var uMap: texture_2d<f32>; @group(1) @binding(2) var uMapSampler: sampler;`.
