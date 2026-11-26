# Custom rendering and shaders

## Contents

- [custom-rendering](#custom-rendering)
  - [Custom-shader mesh](#custom-shader-mesh)
  - [WebGL and WebGPU programs](#webgl-and-webgpu-programs)
  - [Uniforms](#uniforms)
  - [Textures as resources](#textures-as-resources)
  - [Custom filter](#custom-filter)
  - [Advanced GPU features](#advanced-gpu-features)
- [Uniform types](#uniform-types)
  - [Arrays](#arrays)
- [Advanced GPU features](#advanced-gpu-features-1)
  - [Partial buffer updates](#partial-buffer-updates)
  - [Partial texture uploads](#partial-texture-uploads)
  - [Vertex count, index count, winding, and culling](#vertex-count-index-count-winding-and-culling)
  - [WGSL override constants (WebGPU only)](#wgsl-override-constants-webgpu-only)
  - [Custom bind group layout (WebGPU only)](#custom-bind-group-layout-webgpu-only)
  - [Sampling a depth texture with TextureView (WebGPU only)](#sampling-a-depth-texture-with-textureview-webgpu-only)
  - [Integer textures](#integer-textures)
  - [Several color attachments](#several-color-attachments)
  - [3D and array textures](#3d-and-array-textures)
  - [Storage textures (WebGPU only)](#storage-textures-webgpu-only)
  - [Render bundles (WebGPU only)](#render-bundles-webgpu-only)
  - [Pooled scratch textures](#pooled-scratch-textures)
  - [Custom Batcher (extension-based)](#custom-batcher-extension-based)
  - [Custom InstructionPipe cleanup](#custom-instructionpipe-cleanup)

## custom-rendering

Custom shaders on meshes: `Shader.from`, GLSL/WGSL programs, `UniformGroup`, textures as resources, UBOs.

### Custom-shader mesh

```ts
import { Mesh, MeshGeometry, Shader, UniformGroup } from "pixi.js";
import type { Application } from "pixi.js";

declare const app: Application;

const vertex = `
in vec2 aPosition;
in vec2 aUV;
out vec2 vUV;

uniform mat3 uProjectionMatrix;
uniform mat3 uWorldTransformMatrix;
uniform mat3 uTransformMatrix;

void main() {
  mat3 mvp = uProjectionMatrix * uWorldTransformMatrix * uTransformMatrix;
  gl_Position = vec4((mvp * vec3(aPosition, 1.0)).xy, 0.0, 1.0);
  vUV = aUV;
}`;

const fragment = `
in vec2 vUV;
out vec4 finalColor;

uniform vec4 uColor;           // mesh tint and alpha, premultiplied
uniform vec4 uWorldColorAlpha; // render group tint and alpha
uniform float uTime;

void main() {
  finalColor = vec4(vUV, 0.5 + 0.5 * sin(uTime), 1.0) * uColor * uWorldColorAlpha;
}`;

const shader = Shader.from({
  gl: { vertex, fragment },
  resources: {
    uniforms: new UniformGroup({ uTime: { value: 0, type: "f32" } }),
  },
});

const geometry = new MeshGeometry({
  positions: new Float32Array([0, 0, 100, 0, 100, 100, 0, 100]),
  uvs: new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]),
  indices: new Uint32Array([0, 1, 2, 0, 2, 3]),
});

const mesh = new Mesh({ geometry, shader });
app.stage.addChild(mesh);

app.ticker.add(() => {
  shader.resources.uniforms.uniforms.uTime = performance.now() / 1000;
});
```

v7's positional `Shader.from(vertex, fragment, uniforms)` is gone; pass the options object above.

A `Mesh` supplies the attributes `aPosition` and `aUV` (from `MeshGeometry`; a plain `Geometry` uses whatever attribute names you give it) and these uniforms: `uProjectionMatrix`, `uWorldTransformMatrix`, `uWorldColorAlpha` (global) and `uTransformMatrix`, `uColor` (per mesh). The v7 names `projectionMatrix`, `translationMatrix`, `aVertexPosition` and `aTextureCoord` are not provided, so a v7 shader draws nothing. `mesh.tint` and `mesh.alpha` reach a custom shader only through `uColor`; multiply by it or they are ignored.

Write premultiplied colour: the default blend is `ONE, ONE_MINUS_SRC_ALPHA`, and textures are premultiplied on upload. `vec4(1.0, 0.0, 0.0, 0.5)` adds full red on top of half the background (too bright); half-transparent red is `vec4(vec3(1.0, 0.0, 0.0) * 0.5, 0.5)`.

`mesh.texture` (and the `texture` option) feeds only the default mesh shader. With a custom `shader` it is never bound, and the sampler reads whatever texture was last bound to unit 0. Pass it as resources ([below](#textures-as-resources)).

`geometry.indexCount = n` draws a prefix of the index buffer on the unbatched path only; a custom-shader mesh is never batched, so it always applies ([mesh](07-mesh.md#drawing-part-of-the-index-buffer)).

In WGSL the same values are `@group(0) @binding(0) var<uniform> globalUniforms: GlobalUniforms;` (`uProjectionMatrix`, `uWorldTransformMatrix`: `mat3x3<f32>`, `uWorldColorAlpha`: `vec4<f32>`, `uResolution`: `vec2<f32>`) and `@group(1) @binding(0) var<uniform> localUniforms: LocalUniforms;` (`uTransformMatrix`: `mat3x3<f32>`, `uColor`: `vec4<f32>`, `uRound`: `f32`), with those struct fields in that order. Your own resources start at `@group(2)`.

### WebGL and WebGPU programs

```ts
import { Shader } from "pixi.js";

declare const glVertex: string;
declare const glFragment: string;
declare const wgslSource: string; // one source holding both entry points

const shader = Shader.from({
  gl: { vertex: glVertex, fragment: glFragment },
  gpu: {
    vertex: { entryPoint: "mainVert", source: wgslSource }, // must match the @vertex function name
    fragment: { entryPoint: "mainFrag", source: wgslSource },
  },
  resources: {},
});
```

With only `gl`, the shader is WebGL only: under WebGPU a `Mesh` using it is skipped without an error (dev builds warn "Mesh shader has no gpuProgram"). With only `gpu`, it is WebGPU only. The `compatibleRenderers` bitmask is set automatically.

**GLSL version.** `GlProgram` does **not** auto-inject `#version 300 es`; it picks the dialect from the **fragment** source alone. If the fragment contains `#version 300 es` (anywhere; leading whitespace is fine), PixiJS removes the line from both stages and re-inserts it first, so both compile as GLSL ES 3.0; `defaultFilterVert` and other version-less vertex shaders are promoted with it. Otherwise both stages get WebGL1 compat macros (`in` to `attribute`/`varying`, `texture` to `texture2D`, `finalColor` to `gl_FragColor`) and compile as GLSL ES 1.0, where `texelFetch`, integer samplers, `uint`, `layout` and multiple outputs fail. Write `#version 300 es` as the first line of both shaders. With it in the vertex shader but missing from the fragment, compilation fails ("#version directive must occur before anything else").

**Precision.** `GlProgram` always injects a default precision (`highp` vertex, `mediump` fragment) and the program name. It also declares `highp` for sampler types GLSL ES 3.0 gives no default (`usampler2D`, `isampler2D`, `sampler2DArray`, `sampler3D`, and others), so you don't need a precision line for them; one you write yourself is kept. `sampler2D` and `samplerCube` keep their `lowp` default.

### Uniforms

Every uniform needs an explicit `{ value, type }` pair: `new UniformGroup({ uTime: 1 })` is a type error and throws a `TypeError` at construction ("Cannot create property 'name' on number"). Type strings and value formats: [custom-rendering/uniform-types.md](14-custom-rendering.md). A plain object in `resources` (`myUniforms: { uTime: { value: 0, type: "f32" } }`) is auto-wrapped into a `UniformGroup`.

Update through `shader.resources.{group}.uniforms.{name}`. A group created with `isStatic: true` uploads only when you call `group.update()` after changing values.

#### UBO mode (Uniform Buffer Objects)

`ubo: true` makes WebGL upload the group as a uniform block (WebGL2), so the GLSL must declare a matching `uniform Block { ... };`; plain `uniform float` declarations stop receiving values. WebGPU always uploads a `UniformGroup` as a uniform buffer, so plain groups work on both renderers; you don't need `ubo: true` for WebGPU.

```ts
import { UniformGroup } from "pixi.js";

const ubo = new UniformGroup(
  {
    uProjection: { value: new Float32Array(16), type: "mat4x4<f32>" },
    uAlpha: { value: 1.0, type: "f32" },
  },
  { ubo: true, isStatic: true },
);

ubo.uniforms.uAlpha = 0.5;
ubo.update();
```

- `f32`, `i32` and `u32` scalars and vectors are supported. Matrices are float-only.
- Samplers/textures cannot go in a UBO.
- The UniformGroup name in resources must exactly match the UBO block name in the shader.
- Structure and order must exactly match the shader layout; a mismatch garbles rendering with no error.

Uniform sync code is generated with `new Function`: under a CSP without `unsafe-eval`, creating any renderer (WebGL or WebGPU) throws unless `import "pixi.js/unsafe-eval"` runs first ([environments](20-environments-builds.md)).

### Textures as resources

Textures are resources, not uniforms (v7 put them in the uniforms object). Pass the texture's `source` and `style` as separate top-level entries:

```ts
import { Shader, UniformGroup } from "pixi.js";
import type { Texture } from "pixi.js";

declare const vertSrc: string;
declare const fragSrc: string;
declare const texture: Texture;
declare const otherTexture: Texture;

const shader = Shader.from({
  gl: { vertex: vertSrc, fragment: fragSrc },
  resources: {
    uTexture: texture.source,
    uSampler: texture.source.style,
    myUniforms: new UniformGroup({ uAlpha: { value: 1.0, type: "f32" } }),
  },
});

shader.resources.uTexture = otherTexture.source; // swap at runtime
```

Resources are a flat key-value map. In WGSL every key must equal a binding variable name (`var<uniform> myUniforms`, `var uTexture`); an unmatched key is never bound. In GLSL a texture key must equal the sampler uniform name, a plain `UniformGroup` key is free (its member names must match the `uniform` declarations), and a UBO group's key must equal the uniform block name.

### Custom filter

A filter is a shader drawn over a container's rendered output: `Filter.from({ gl: { vertex: defaultFilterVert, fragment }, resources })`. Its traps (no default vertex shader, `vTextureCoord` range, `highp` uniforms, a gl-only filter on WebGPU, premultiplied colour, sampling the backdrop with `blendRequired`) are in [filters](12-filters.md#custom-filter).

### Advanced GPU features

Read [custom-rendering/advanced-gpu.md](14-custom-rendering.md) when the task needs one of these:

- **Partial uploads**: `buffer.update(sizeInBytes, offsetInBytes)`; `bufferImageSource.update(startTexel, endTexel)`.
- **Vertex/index counts, winding, culling**: `geometry.vertexCount` (replaces the deprecated `getSize()`), `geometry.indexCount` with `batchMode`, `state.clockwiseFrontFace`, `cullMode`.
- **WGSL override constants** (WebGPU): `Shader.from({ gpu, resources, overrides: { STEPS: 8 } })`.
- **Custom bind group layouts** (WebGPU): `gpuLayout` from `generateGpuLayoutGroups(extractStructAndGroups(source))`.
- **Depth sampling** (WebGPU): `new TextureView(depth, { aspect: "depth-only" })` with a `depthReadOnly` attachment.
- **Integer textures**: `rgba32uint` etc., `usampler2D`/`texelFetch`, `texture_2d<u32>`/`textureLoad`.
- **Several color attachments**: `colorAttachments` with mixed formats (`rgba16float`, `rg16float`, `r32uint`); a draw writes only the attachments its shader has `@location(n)` / `layout(location = n) out` outputs for, integer attachments never blend, each attachment clears to its own `clearValue` unless it says `loadOp: "load"`.
- **3D and array textures**: `depth` / `arrayLayerCount`, `sampler3D`/`texture_3d<f32>`, `sampler2DArray`, rendering into one slice with `layer`.
- **Storage textures** (WebGPU): `storage: true`, `getGpuSource(source).createView()`.
- **Render bundles** (WebGPU): `encoder.beginBundle()` / `endBundle()` / `executeBundle()`, `isBundleValid()`.
- **Pooled scratch textures**: `TexturePool.getOptimalTexture({ width, height, ... })`, `returnTexture()`.
- **Custom `Batcher`** and **custom `InstructionPipe`** (`destroyInstructionSet`) registered via extensions.


---

## Uniform types

Every `type` string a `UniformGroup` entry accepts, and the JS value each takes.

| PixiJS type   | GLSL     | JS value                      |
| ------------- | -------- | ----------------------------- |
| `f32`         | `float`  | `number`                      |
| `i32`         | `int`    | `number`                      |
| `u32`         | `uint`   | `number`                      |
| `vec2<f32>`   | `vec2`   | `Float32Array(2)` or `[x, y]` |
| `vec3<f32>`   | `vec3`   | `Float32Array(3)`             |
| `vec4<f32>`   | `vec4`   | `Float32Array(4)`             |
| `vec2<i32>`   | `ivec2`  | `Int32Array(2)`               |
| `vec3<i32>`   | `ivec3`  | `Int32Array(3)`               |
| `vec4<i32>`   | `ivec4`  | `Int32Array(4)`               |
| `vec2<u32>`   | `uvec2`  | `Uint32Array(2)`              |
| `vec3<u32>`   | `uvec3`  | `Uint32Array(3)`              |
| `vec4<u32>`   | `uvec4`  | `Uint32Array(4)`              |
| `mat2x2<f32>` | `mat2`   | `Float32Array(4)`             |
| `mat3x3<f32>` | `mat3`   | `Float32Array(9)` or `Matrix` |
| `mat4x4<f32>` | `mat4`   | `Float32Array(16)`            |
| `mat3x2<f32>` | `mat3x2` | `Float32Array(6)`             |
| `mat4x2<f32>` | `mat4x2` | `Float32Array(8)`             |
| `mat2x3<f32>` | `mat2x3` | `Float32Array(6)`             |
| `mat4x3<f32>` | `mat4x3` | `Float32Array(12)`            |
| `mat2x4<f32>` | `mat2x4` | `Float32Array(8)`             |
| `mat3x4<f32>` | `mat3x4` | `Float32Array(12)`            |

The type string is the WGSL type. A PixiJS `Matrix` (2D affine) maps to `mat3x3<f32>`; a 3D projection is a `Float32Array(16)` with `mat4x4<f32>`.

Non-square matrices (`mat3x2` and the rest) work on WebGPU and inside a WebGL UBO only. As a plain WebGL `uniform` they throw at render time ("Cannot read properties of undefined (reading 'replace')"); use `mat2x2`, `mat3x3` or `mat4x4` there.

`uint` and `uvec*` need GLSL ES 3.0 (`#version 300 es` as the first line).

### Arrays

Use the `size` property; `array<vec4<f32>, 10>` in the type field throws an error directing you to `size`.

```ts
import { UniformGroup } from "pixi.js";

const uniforms = new UniformGroup({
  uColors: { value: new Float32Array(40), type: "vec4<f32>", size: 10 },
});
```

Which types a `{ ubo: true }` group can hold and how it must match the shader's block: [custom-rendering](14-custom-rendering.md#ubo-mode-uniform-buffer-objects).


---

## Advanced GPU features

Lower-level rendering APIs for custom draw code. Items marked WebGPU only are ignored or unavailable on the WebGL renderer; branch on `renderer.name === "webgpu"` before relying on them.

### Partial buffer updates

```ts
import { Buffer, BufferUsage } from "pixi.js";

const buffer = new Buffer({
  data: new Float32Array(4096),
  usage: BufferUsage.VERTEX | BufferUsage.COPY_DST,
});

buffer.data.set(newVertices, 256);
buffer.update(newVertices.byteLength, 256 * 4); // size and offset in bytes
```

`update()` with no arguments re-uploads the whole buffer. Pass a byte size and byte offset to upload only the range you changed. Works on WebGL and WebGPU.

### Partial texture uploads

```ts
import { BufferImageSource } from "pixi.js";

const data = new Float32Array(4096 * 64 * 4); // rgba32float: 4 floats per texel
const source = new BufferImageSource({ resource: data, width: 4096, height: 64 });

data.fill(1, 100 * 4, 116 * 4); // change texels 100 to 115
source.update(100, 116); // upload only those 16 texels
```

Texel `i` sits at `x = i % width`, `y = floor(i / width)`, and `end` is exclusive. The range applies to that call only, so track the lowest and highest changed texel yourself and call `update` once per frame. `update()` with no arguments uploads the whole texture. Works on WebGL and WebGPU. A 3D texture (`depth`) or 2D array (`arrayLayerCount`) always uploads whole, so call `update()` with no range.

### Vertex count, index count, winding, and culling

```ts
const count = geometry.vertexCount; // cached, from the first non-instanced attribute

// several geometries share one index buffer sized for the biggest batch;
// each draws only the prefix it currently uses
const quads = new Geometry({
  attributes: { aPosition: positions },
  indexBuffer: sharedIndices,
  indexCount: liveQuads * 6,
});
quads.indexCount = 12; // read at draw time; no re-upload

const state = new State();
state.culling = true;
state.clockwiseFrontFace = true; // or state.cullMode = "front"
```

`geometry.getSize()` is deprecated since 8.20.0 and logs a warning; read `vertexCount` instead, which is recomputed only when buffers or attributes change. `indexCount` of `0` (the default) draws the whole index buffer; any other value draws that many indices. A `size` passed to `encoder.draw()` still wins. The batcher ignores `indexCount` and draws every index, so it has no effect on a `Mesh` with no custom shader and a `MeshGeometry` of 100 vertices or fewer (`batchMode: "auto"`); set `geometry.batchMode = "no-batch"` there. A plain `Geometry` like this one, or any mesh with a custom `Shader`, always takes the direct path. `clockwiseFrontFace` selects which winding counts as front-facing on both renderers. When rendering into a texture PixiJS inverts the winding to match the flipped projection; call `renderer.renderTarget.isFrontFaceInverted()` if your own code needs the resolved orientation, or `isFrontFaceInverted(target, flipY)` to ask about a `RenderTarget` before binding it (`renderer.renderTarget.getRenderTarget(texture)` returns one for a texture).

### WGSL override constants (WebGPU only)

```ts
const source = /* wgsl */ `
  override BLUR_STEPS: u32 = 4u;
  // ...
`;

const shader = Shader.from({
  gpu: {
    vertex: { source, entryPoint: "vsMain" },
    fragment: { source, entryPoint: "fsMain" },
  },
  resources: { uniforms },
  overrides: { BLUR_STEPS: 8 },
});
```

`overrides` takes a plain `Record<string, number>` or a `ShaderOverrides` instance. Values are fixed when the shader is created and become part of the pipeline cache key, so every distinct set compiles its own pipeline. To change a value, create a new shader. On browsers without pipeline constants (Safari) PixiJS substitutes the values into the WGSL source; `renderer.limits.supportsOverrideConstants` tells you which path is active. WebGL ignores `overrides` entirely.

### Custom bind group layout (WebGPU only)

```ts
import { GpuProgram, extractStructAndGroups, generateGpuLayoutGroups } from "pixi.js";

const gpuLayout = generateGpuLayoutGroups(extractStructAndGroups(source));

// narrow one texture binding to the fragment stage
gpuLayout[0][1].visibility = GPUShaderStage.FRAGMENT;

const program = new GpuProgram({
  vertex: { source, entryPoint: "vsMain" },
  fragment: { source, entryPoint: "fsMain" },
  gpuLayout,
});
```

`generateGpuLayoutGroups` is the same generator `GpuProgram` runs when `gpuLayout` is omitted, and it marks every binding visible to both stages. Generate the default, edit the entries you care about, and pass the whole array back rather than hand-writing the layout.

### Sampling a depth texture with TextureView (WebGPU only)

```ts
import { RenderTarget, Shader, State, TextureSource, TextureView } from "pixi.js";

const depth = new TextureSource({ width: 512, height: 512, format: "depth24plus-stencil8" });
const color = new TextureSource({ width: 512, height: 512 });

// pass 1: write depth
const writeTarget = new RenderTarget({
  colorAttachments: [{ texture: color, clearValue: [0, 0, 0, 1] }],
  depthStencilAttachment: { texture: depth, depthLoadOp: "clear", depthClearValue: 1 },
});

// pass 2: keep the same depth attached read-only while sampling it
const readTarget = new RenderTarget({
  colorAttachments: [{ texture: color, loadOp: "load" }], // keeps pass 1's color even when bound with clear
  depthStencilAttachment: { texture: depth, depthReadOnly: true },
});

const shader = Shader.from({
  gpu: { vertex: { source, entryPoint: "vsMain" }, fragment: { source, entryPoint: "fsMain" } },
  resources: { uDepthTexture: new TextureView(depth, { aspect: "depth-only" }) },
});
```

Declare `@group(0) @binding(1) var uDepthTexture: texture_depth_2d;` in WGSL and read it with `textureLoad`. Use a `State` with `depthMask = false` in the read pass. A `TextureView` is a bind resource like a `TextureSource`; on WebGL it binds the underlying source and the descriptor is ignored.

### Integer textures

```ts
import { BufferImageSource, Shader } from "pixi.js";

const ids = new BufferImageSource({
  resource: new Uint32Array([1, 2, 3, 4]), // picks rgba32uint
  width: 1,
  height: 1,
  scaleMode: "nearest",
});

const shader = Shader.from({
  gl: { vertex: vertSrc, fragment: fragSrc },
  gpu: { vertex: { source, entryPoint: "vsMain" }, fragment: { source, entryPoint: "fsMain" } },
  resources: { uIds: ids },
});
```

Integer formats (`*uint`, `*sint`) hold exact integers. Use them where a float texture would lose bits, since small integers are denormal floats and GPUs may flush them to zero. They can't be filtered, so set `scaleMode: "nearest"`. `BufferImageSource` infers `rgba32float` from a `Float32Array`, `rgba32uint` from a `Uint32Array` or `Int32Array`, and `rgba16uint` from a `Uint16Array` or `Int16Array`; pass `format: "rgba32sint"` (or another signed format) explicitly for signed data. Any other array, including a `Uint8Array`, becomes `bgra8unorm`, which swaps red and blue on WebGPU; pass `format: "rgba8unorm"` for RGBA bytes. It defaults integer formats to `alphaMode: "no-premultiply-alpha"` because integer data can't be premultiplied on upload.

In GLSL ES 3.0, declare `uniform usampler2D uIds;` (or `isampler2D`) and read it with `texelFetch(uIds, ivec2(x, y), 0)`. GLSL ES 3.0 gives integer samplers no default precision, so PixiJS declares `highp` for them and you don't need a precision line. A precision line you write yourself is kept. In WGSL, declare `@group(0) @binding(1) var uIds: texture_2d<u32>;` (or `<i32>`) and read it with `textureLoad(uIds, vec2<i32>(x, y), 0)`; the generated bind group layout takes its `sampleType` from the `<u32>` / `<i32>` suffix. An integer texture can also be a render target's color attachment (below); it can't be antialiased.

### Several color attachments

```ts
import { RenderTarget, TextureSource } from "pixi.js";

const target = new RenderTarget({
  colorAttachments: [
    { texture: new TextureSource({ width, height, format: "rgba16float" }) },
    { texture: new TextureSource({ width, height, format: "rg16float" }), clearValue: [0, 0, 0, 0] },
    { texture: new TextureSource({ width, height, format: "r32uint" }), clearValue: [0xffffffff, 0, 0, 0] },
  ],
});
```

Each attachment keeps its own format. A draw writes only the attachments its fragment shader has outputs for: WGSL `@location(n)` fields of the returned struct (or a single `-> @location(0)` return), GLSL ES 3.0 `layout(location = n) out` declarations. Every other attachment is left as it was, so a 2D sprite drawn into this target changes attachment 0 only. PixiJS reads the outputs from the source; a shader it can't read (an output built by a macro) writes every attachment. `GpuProgram.fragmentOutputMask` and `GlProgram.fragmentOutputMask` show what it found, one bit per location, or `null` when it couldn't read them.

Every attachment a draw writes blends with the draw's blend mode, except integer formats, which never blend. A blended draw needs a `vec4` output for each attachment it writes, as the blend reads its alpha: WebGPU reports a validation error and skips the draw, and WebGL blends with an undefined alpha. Write integer outputs as `u32` / `i32` in WGSL, and as `highp uint` / `highp int` in GLSL: a GLSL ES 3.0 fragment shader defaults integers to `mediump`, which only guarantees 16 bits on some phones. `renderer.extract` reads 8-bit color only, and throws when asked to read a float, integer or depth texture. For a 16-bit float texture, extract `new Sprite(texture)` instead. For 32-bit float, integer and depth textures, extract a `Mesh` whose shader reads the texture and outputs color.

The bind's `clear` decides whether anything clears. Each attachment clears to its own `clearValue`, or to the bind's clear color where it has none; integer attachments take the numbers as integers. An attachment with `loadOp: "load"` keeps its contents even when the bind clears, and a bind with `clear: false` never clears. WebGL1 clears all attachments or none.

### 3D and array textures

```ts
import { BufferImageSource } from "pixi.js";

const size = 64;
const noise = new BufferImageSource({
  resource: new Uint8Array(size * size * size * 4), // slice after slice, row-major
  width: size,
  height: size,
  depth: size, // or arrayLayerCount: n for a 2D array
  format: "rgba8unorm",
});
```

`depth` on a `TextureSource` or `BufferImageSource` makes a `"3d"` texture, and `arrayLayerCount > 1` makes a `"2d-array"` texture. A texture can't have both, and TypeScript rejects options that set both. Pass `viewDimension` only when the size doesn't decide it, such as `"cube"` for 6 layers. `dimensions` is deprecated; leave it out. These textures need WebGL2 or WebGPU; WebGL1 has no 3D or array textures.

The buffer holds the slices (or layers) one after another, each in row-major order, so texel `(x, y, z)` sits at index `x + y * width + z * width * height`. `resolution` doesn't scale `depth`. A 3D or array `BufferImageSource` defaults to `alphaMode: "no-premultiply-alpha"` and always uploads whole, so `update()` takes no range.

In GLSL ES 3.0, declare `uniform sampler3D` or `uniform sampler2DArray`. In WGSL, declare `texture_3d<f32>` or `texture_2d_array<f32>`. PixiJS adds the precision line for `sampler3D` and `sampler2DArray`, as for integer samplers above.

`rgba32float`, the default for a `Float32Array`, needs an optional feature for linear filtering that PixiJS doesn't request on WebGPU. Use `scaleMode: "nearest"` with it, or pick `rgba8unorm`, `r8unorm` or `rgba16float` for smooth sampling.

To draw into one slice or layer, pass the source itself as `target` and pick the slice with `layer`: `renderer.render({ container, target: noise, layer: z, clear: true })`. `layer` selects an array layer, a cube face, or a 3D depth slice. `RenderTexture.create` doesn't take `depth`, so use the `TextureSource` directly. `renderer.renderTarget.push({ target, layer })` takes `layer` too.

### Storage textures (WebGPU only)

```ts
import { TextureSource } from "pixi.js";
import type { Renderer, WebGPURenderer } from "pixi.js";

declare const renderer: Renderer;

const volume = new TextureSource({ width: 64, height: 64, depth: 64, format: "rgba8unorm", storage: true });

// bind this view to a texture_storage_3d<rgba8unorm, write> in your own compute pass
const view = (renderer as WebGPURenderer).texture.getGpuSource(volume).createView();
```

`storage: true` adds `GPUTextureUsage.STORAGE_BINDING`, so your own compute pass can write the texture through `getGpuSource(source).createView()`, which exists only on the WebGPU texture system (cast the renderer to `WebGPURenderer`). PixiJS still samples it like any other texture. WebGL ignores the option.

Every device accepts `rgba8unorm`, `rgba16float`, `r32float`, `rg32float`, `rgba32float` and the matching integer formats as storage textures. `bgra8unorm` needs the `bgra8unorm-storage` feature, and formats such as `r8unorm` or `r16float` need `texture-formats-tier1`. PixiJS enables both features when the GPU has them. WebGPU rejects any other format when the texture is created.

`autoGenerateMipmaps` on a 3D texture uses `gl.generateMipmap` on WebGL. WebGPU writes the mips with a compute shader, so the texture needs `storage: true` and the `rgba8unorm` or `rgba16float` format.

### Render bundles (WebGPU only)

```ts
import { RenderContainer } from "pixi.js";
import type { RenderBundle, WebGPURenderer } from "pixi.js";

let bundle: RenderBundle | null = null;

const props = new RenderContainer({
  render: (renderer) => {
    const encoder = (renderer as WebGPURenderer).encoder;

    if (!bundle || !encoder.isBundleValid(bundle)) {
      encoder.beginBundle("static-props");
      encoder.draw({ geometry, shader, state });
      bundle = encoder.endBundle();
    }

    encoder.executeBundle(bundle);
  },
});
```

A bundle records draw calls once and replays them on later frames. It bakes the render target it was recorded in (formats, sample count, winding) and the device, so `isBundleValid` returns `false` after the target changes (a filter wrapping the container, `flipY` flipping) or after a device loss. Re-record when it does; otherwise WebGPU rejects the frame or draws inside out. Pass an array to `executeBundle` to replay several bundles in one call. The optional label names the bundle in GPU captures.

### Pooled scratch textures

```ts
import { TexturePool } from "pixi.js";

const scratch = TexturePool.getOptimalTexture({
  width: bounds.width,
  height: bounds.height,
  resolution: renderer.resolution,
  antialias: true,
  scaleMode: "nearest",
});

const { width, height } = TexturePool.getOptimalSize(bounds.width, bounds.height, renderer.resolution);

TexturePool.returnTexture(scratch);
```

`getOptimalTexture` takes one request object: `width` and `height` are the minimum frame size; `resolution`, `antialias`, `autoGenerateMipmaps`, `format`, and `scaleMode` are optional, and each combination has its own bucket, so ask for a float or depth format directly instead of restyling a returned texture. Each axis is rounded up to the next power of two or the renderer's screen size, whichever is smaller. `getOptimalSize` reports that backing size without taking a texture, and `getSameSizeTexture(texture)` matches an existing texture's frame and resolution. The positional `getOptimalTexture(width, height, resolution, antialias)` form, `TexturePool.textureStyle`, and `enableFullScreen` are deprecated since 8.21.0.

### Custom Batcher (extension-based)

```ts
import { BatchGeometry, Batcher, extensions, ExtensionType } from "pixi.js";
import type { BatchableMeshElement, BatchableQuadElement, Shader } from "pixi.js";

declare const myBatchShader: Shader;

class MyBatcher extends Batcher {
  public static extension = {
    type: [ExtensionType.Batcher],
    name: "my-batcher",
  };

  public name = "my-batcher";
  protected vertexSize = 6; // floats per vertex
  public geometry = new BatchGeometry();
  public shader: Shader = myBatchShader;

  public packAttributes(
    element: BatchableMeshElement,
    float32View: Float32Array,
    uint32View: Uint32Array,
    index: number,
    textureId: number,
  ): void {}

  public packQuadAttributes(
    element: BatchableQuadElement,
    float32View: Float32Array,
    uint32View: Uint32Array,
    index: number,
    textureId: number,
  ): void {}
}

extensions.add(MyBatcher);
```

Elements reference the batcher by `batcherName`. The `BatchableElement` interface requires: `batcherName`, `texture`, `blendMode`, `indexSize`, `attributeSize`, `topology`, and `packAsQuad`.

### Custom InstructionPipe cleanup

A custom `InstructionPipe` that caches state per `InstructionSet` (the way `BatcherPipe` keeps its batchers) should implement `destroyInstructionSet(instructionSet)`. The renderer calls it when the owning render group is destroyed, so the cached GPU objects are released with it instead of leaking.

```ts
public destroyInstructionSet(instructionSet: InstructionSet): void {
  this._cache[instructionSet.uid]?.destroy();
  delete this._cache[instructionSet.uid];
}
```
