# Mesh

## Contents

- [scene-mesh](#scene-mesh)
  - [Variants](#variants)
  - [MeshGeometry owns the vertex data](#meshgeometry-owns-the-vertex-data)
  - [Indices are never optional in practice](#indices-are-never-optional-in-practice)
  - [UVs are relative to the texture's frame](#uvs-are-relative-to-the-textures-frame)
  - [Batching](#batching)
  - [Hit testing and state](#hit-testing-and-state)
- [Mesh](#mesh-1)
  - [Constructor options](#constructor-options)
  - [Updating vertices at runtime](#updating-vertices-at-runtime)
  - [Drawing part of the index buffer](#drawing-part-of-the-index-buffer)
  - [Custom shader](#custom-shader)
- [MeshSimple](#meshsimple)
- [MeshPlane](#meshplane)
  - [Deforming the grid](#deforming-the-grid)
  - [Size and autoResize](#size-and-autoresize)
- [MeshRope](#meshrope)
  - [Options](#options)
- [PerspectiveMesh](#perspectivemesh)

## scene-mesh

`Mesh` and `MeshGeometry`, plus the `MeshSimple`, `MeshPlane`, `MeshRope` and `PerspectiveMesh` variants: geometry rules, UVs, batching and hit testing.

```ts
const texture = await Assets.load("pattern.png");

const geometry = new MeshGeometry({
  positions: new Float32Array([0, 0, 100, 0, 100, 100, 0, 100]),
  uvs: new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]),
  indices: new Uint32Array([0, 1, 2, 0, 2, 3]),
  topology: "triangle-list",
});
const mesh = new Mesh({ geometry, texture });
```

Every mesh class takes one options object. The base `Mesh` requires a `geometry`; the subclasses build their own geometry and require a `texture`. v7 → v8: `SimpleMesh` → `MeshSimple`, `SimplePlane` → `MeshPlane`, `SimpleRope` → `MeshRope` (the old names are not exported); `new MeshGeometry(vertices, uvs, indices)` → `new MeshGeometry({ positions, uvs, indices })` (the property is `positions`; `vertices` is only `MeshSimple`'s name); `new Mesh(geometry, shader)` is deprecated for `new Mesh({ geometry, shader })`, and its `drawMode` argument is gone: set `geometry.topology`.

### Variants

| Variant           | Use when                                                         | Reference                                       |
| ----------------- | ---------------------------------------------------------------- | ----------------------------------------------- |
| `Mesh`            | Custom geometry or a custom shader; indexed partial draws        | [mesh.md](07-mesh.md)                   |
| `MeshSimple`      | Quick textured shape with per-frame vertex animation             | [mesh-simple.md](07-mesh.md)     |
| `MeshPlane`       | Subdivided textured rectangle for distortion (waves, cloth)      | [mesh-plane.md](07-mesh.md)       |
| `MeshRope`        | Texture following a polyline (ropes, trails); thickness is `texture.height` | [mesh-rope.md](07-mesh.md)         |
| `PerspectiveMesh` | 2D plane warped to four corners (tilted card, floor); not 3D, no depth buffer | [mesh-perspective.md](07-mesh.md) |

A plain textured quad is a `Sprite` ([scene-sprite](04-sprites.md)), not a mesh. Shader authoring is in [custom-rendering](14-custom-rendering.md).

### MeshGeometry owns the vertex data

`MeshGeometry` holds `positions`, `uvs`, `indices` and `topology` (`'triangle-list'` default, `'triangle-strip'`, `'line-list'`, `'line-strip'`, `'point-list'`; topology is a geometry property, not a mesh one). One geometry can be shared across meshes. It is not reference-counted and `mesh.destroy()` does not destroy it; call `geometry.destroy()` after the last mesh using it is gone.

`new MeshGeometry({ shrinkBuffersToFit: true })` reallocates the GPU buffers when you later assign a smaller `positions`/`uvs`/`indices` array. The default `false` keeps the larger allocation and reuses it, which is cheaper when sizes change often.

### Indices are never optional in practice

Omitted `indices` default to the quad list `[0, 1, 2, 0, 2, 3]`; there is no unindexed "draw in vertex order" mode. Pass `indices` for anything other than a 4-vertex quad drawn as `'triangle-list'`, whatever the topology: for a strip over `n` vertices pass `[0, 1, ..., n - 1]`. Without them a triangle reads a vertex that does not exist and a strip draws only its first quad.

### UVs are relative to the texture's frame

Mesh UVs `0..1` span the texture's frame, not its source image: the renderer multiplies them by `texture.textureMatrix`. For an atlas sub-texture use `0..1` UVs (or fractions of the frame). Feeding atlas-space UVs (such as `subTexture.uvs` values, or `frame.x / source.width`) to a sub-texture maps the frame twice and samples the wrong region. To address the whole atlas in atlas coordinates, use a texture of the full source (`new Texture({ source: sub.source })`) instead.

UVs above `1` tile only after `texture.source.addressMode = "repeat"`; the default `'clamp-to-edge'` smears the edge pixels instead. The setting changes every user of that source, and repeat wraps the whole source, so tile a standalone image, not an atlas frame. Omitted `uvs` are all zero, so the mesh samples one texel.

### Batching

A mesh batches only if its geometry is a `MeshGeometry` or subclass (a plain `Geometry` never batches), it has no custom shader and no depth or culling state, and `geometry.batchMode` allows it: `'auto'` (default) batches at 100 vertices or fewer, `'batch'` always, `'no-batch'` never.

`geometry.indexCount = n` draws only the first `n` indices, but only on the unbatched path: a batched mesh draws every index. Set `geometry.batchMode = "no-batch"` with it when the mesh uses the default shader (see [mesh](07-mesh.md#drawing-part-of-the-index-buffer)).

### Hit testing and state

`Mesh.containsPoint(point)` (and so pointer events) tests the triangles in the index buffer. It works for a connected `'triangle-list'` (quads, `MeshPlane`, `MeshRope`). On a `'triangle-strip'` it tests only every third triangle, so most of the strip ignores the pointer; on a list holding separate pieces it also tests triangles straddling two neighbours, so the gaps between pieces register hits. Give those meshes a `hitArea` (a `Polygon` of the outline) or build strips as triangle lists.

`new Mesh({ geometry, state })` takes a `State` for blend, depth and culling (default `State.for2d()`); depth or culling flags disable batching.


---

## Mesh

The base `Mesh`: constructor options, updating vertex buffers, drawing part of the index buffer, custom shaders. Geometry, UV, index and batching rules are in [scene-mesh](07-mesh.md).

### Constructor options

`new Mesh({ geometry, shader?, state?, texture?, roundPixels? })`

| Option        | Default         | Notes                                                                                 |
| ------------- | --------------- | ------------------------------------------------------------------------------------- |
| `geometry`    | —               | Required. Shareable across meshes.                                                    |
| `shader`      | `null`          | When set, the mesh skips batching and the shader decides what to sample.              |
| `state`       | `State.for2d()` | Blend, depth, culling. Depth or culling flags disable batching.                       |
| `texture`     | `Texture.WHITE` | Sampled by the default shader. Ignored if a custom `shader` provides its own texture. |
| `roundPixels` | `false`         |                                                                                       |

The constructor assigns `texture` from `shader.texture` when a custom shader is passed without an explicit `texture` option. Assigning `null`/`undefined` to `mesh.texture` at runtime coerces it to `Texture.EMPTY`.

### Updating vertices at runtime

```ts
declare const mesh: Mesh<MeshGeometry>;
mesh.geometry.positions[1] = Math.sin(performance.now() / 500) * 20;
mesh.geometry.getBuffer("aPosition").update();
```

The `positions`, `uvs` and `indices` getters return the underlying `Float32Array` / `Uint32Array` directly: the same data as `getBuffer('aPosition').data` / `getBuffer('aUV').data` / `getIndex().data`. Mutate in place, or assign a whole new array via the setter (the setters do `buffer.data = value` with no length check; the real invariant is `uvs.length >= positions.length` so every vertex has a UV).

Call `update()` on the buffer after mutating its `data` array to push changes to the GPU. The attribute names are `aPosition` and `aUV` (v7's `aVertexPosition`/`aTextureCoord` throw in `getBuffer`); a custom shader must declare the same names. `MeshSimple` uploads automatically.

### Drawing part of the index buffer

```ts
declare const pool: MeshGeometry; // indices for the largest number of quads
declare const activeQuads: number;

pool.batchMode = "no-batch"; // batched meshes ignore indexCount
pool.indexCount = activeQuads * 6; // 0 (default) draws every index
```

`geometry.indexCount` draws only the first `n` indices; it is read at draw time, so changing it uploads nothing. Only the direct (unbatched) draw honours it: a batched mesh always draws every index in `geometry.indices`. With the default shader and 100 or fewer vertices the mesh batches, so also set `batchMode = 'no-batch'` (a custom shader, or depth/culling state, already disables batching). `MeshGeometry` has no `indexCount` constructor option; assign the property.

### Custom shader

```ts
declare const geometry: MeshGeometry;
const shader = Shader.from({
  gl: { vertex: vertSrc, fragment: fragSrc },
  resources: { uTexture: tex.source, uSampler: tex.source.style },
});
const mesh = new Mesh({ geometry, shader });
```

With a shader, `texture` is optional and batching is bypassed. Shader authoring: [custom-rendering](14-custom-rendering.md).


---

## MeshSimple

A `Mesh` that builds its own `MeshGeometry` from `vertices` and uploads the position buffer every frame. v7's `SimpleMesh` (positional args) is not exported.

```ts
const triangle = new MeshSimple({
  texture: tex,
  vertices: new Float32Array([0, 0, 100, 0, 50, 100]),
  uvs: new Float32Array([0, 0, 1, 0, 0.5, 1]),
  indices: new Uint32Array([0, 1, 2]),
});

app.ticker.add(() => {
  triangle.vertices[5] = 100 + Math.sin(performance.now() / 500) * 20;
});
```

| Option     | Default              | Notes                                                                                      |
| ---------- | -------------------- | ------------------------------------------------------------------------------------------ |
| `texture`  | —                    | Required.                                                                                  |
| `vertices` | `undefined`          | Flat `x, y` pairs, passed to `MeshGeometry` as `positions`; also the `mesh.vertices` getter. |
| `uvs`      | `undefined`          | Omitted UVs are zeros, so the mesh samples only pixel `(0, 0)`. Run `0..1` across the texture's frame, also for a spritesheet frame. |
| `indices`  | `[0, 1, 2, 0, 2, 3]` | The default is a quad; pass indices for any other vertex count or topology (a 3-vertex mesh without them reads a fourth vertex that does not exist; a line strip would follow `0-1-2-0-2-3`). |
| `topology` | `'triangle-list'`    | Any `MeshGeometry` topology.                                                               |

`geometry` is not an option; `shader`, `state` and `roundPixels` behave as on [Mesh](07-mesh.md).

`autoUpdate` is a runtime property (default `true`), not a constructor option: mutating `vertices` in place or assigning a new array reaches the GPU on the next render. Set `autoUpdate = false` to upload yourself with `mesh.geometry.getBuffer("aPosition").update()`.

The auto-update runs as the mesh's own `onRender` callback. Assigning `mesh.onRender = ...` replaces it, and vertex changes silently stop reaching the GPU. Animate from `app.ticker` instead, or call `mesh.geometry.getBuffer("aPosition").update()` inside your `onRender`.


---

## MeshPlane

A texture mapped onto a subdivided grid for per-vertex distortion (waves, cloth, heat haze). v7's `SimplePlane(texture, 10, 10)` is `new MeshPlane({ texture, verticesX: 10, verticesY: 10 })`.

Options: `texture` (required; sets the initial `width`/`height`), `verticesX` and `verticesY` (each default `10`). `geometry` is not an option (it builds a `PlaneGeometry`); `shader`, `state` and `roundPixels` behave as on [Mesh](07-mesh.md).

Meshes batch only with 100 vertices or fewer, so the 10×10 default is the last batchable size; any denser plane costs its own draw call. Vertex density doesn't change how an undeformed plane samples its texture, and `roundPixels` only snaps the position: for blurry pixel art set `texture.source.scaleMode = "nearest"`.

### Deforming the grid

```ts
const plane = new MeshPlane({ texture: tex, verticesX: 30, verticesY: 30 });
const { buffer } = plane.geometry.getAttribute("aPosition");
const original = new Float32Array(buffer.data);

app.ticker.add(() => {
  const t = performance.now() / 500;
  for (let i = 0; i < buffer.data.length; i += 2) {
    buffer.data[i + 1] = original[i + 1] + Math.sin(t + original[i] * 0.1) * 5;
  }
  buffer.update();
});
```

The buffer does not observe its own `data` array: without `buffer.update()` the next render draws stale vertices. UVs are fixed once the plane is built, so moving vertices stretches the texture to follow.

### Size and autoResize

`autoResize` is a runtime property the constructor sets to `true`, not a constructor option. While it is on, changing the texture (or the texture emitting `'update'`) rebuilds the geometry to the new texture's dimensions. For a size decoupled from the texture:

```ts
declare const plane: MeshPlane;
plane.autoResize = false;
const geometry = plane.geometry as PlaneGeometry; // typed as MeshGeometry
geometry.width = 500;
geometry.height = 300;
geometry.build({});
```

`build()` keeps the geometry's current `verticesX`/`verticesY`/`width`/`height` and ignores the same keys in its argument, so `build({ verticesX: 20 })` changes nothing: assign the fields, then call `build({})`.


---

## MeshRope

A texture stretched or tiled along a polyline of points (ropes, trails, tentacles). v7's `SimpleRope(texture, points)` is `new MeshRope({ texture, points })`.

```ts
const points: Point[] = [];
for (let i = 0; i < 20; i++) points.push(new Point(i * 50, 0));

const rope = new MeshRope({ texture: tex, points, textureScale: 0 });

app.ticker.add(() => {
  const t = performance.now() / 500;
  points.forEach((p, i) => (p.y = Math.sin(i * 0.5 + t) * 30));
});
```

The texture's x-axis runs along the path and its y-axis is the thickness. The rope bends only at points, so a visible curve needs many closely spaced points (typically 15–30); two points draw a straight segment. With `autoUpdate` on (default), moving the points updates the geometry on the next render.

Two silent traps:

- **Keep the point count fixed.** With `textureScale: 0` the buffers are sized once from the initial array; points pushed later are never drawn. Preallocate the full length (a trail of N points shifted each frame), or create a new rope when the count changes. `textureScale > 0` rebuilds on every update and does follow the length.
- **Thickness is `texture.height`, not `width`.** The rope's render hook resets the geometry width to `texture.height` every frame, so the `width` option only lasts until the first render. Use a texture whose height is the thickness you want, or replace the hook:

```ts
declare const points: Point[];
const thick = new MeshRope({ texture: tex, points, width: 60 });
thick.onRender = () => (thick.geometry as RopeGeometry).update();
```

### Options

| Option         | Default          | Notes                                                                                                                       |
| -------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `texture`      | —                | Required.                                                                                                                   |
| `points`       | —                | Required. `PointData[]`, the ordered path.                                                                                  |
| `textureScale` | `0`              | `0` stretches the texture over the full length. `> 0` repeats it at its aspect ratio, scales the thickness to `texture.height * textureScale`, and sets the shared source's `addressMode` to `'repeat'`. Values `< 1` with a larger source reduce alpha artifacts. |
| `width`        | `texture.height` | Overwritten with `texture.height` on the first render (see above).                                                          |

`geometry` is not an option (it builds a `RopeGeometry`); `shader`, `state` and `roundPixels` behave as on [Mesh](07-mesh.md). `MeshRope.defaultOptions` overrides the `textureScale` default globally.

`autoUpdate` is a runtime property (default `true`), not a constructor option. Set `rope.autoUpdate = false` and call `(rope.geometry as RopeGeometry).update()` when you choose. The auto-update is the rope's own `onRender`; assigning `rope.onRender = ...` replaces it, so call `(rope.geometry as RopeGeometry).update()` yourself inside your callback.

With `textureScale > 0` on a WebGL1 context (`preferWebGLVersion: 1`, or a device without WebGL2), PixiJS forces non-power-of-two textures to clamp, so the tiles smear into stretched edge pixels. WebGL2 and WebGPU repeat any size; use power-of-two dimensions (128, 256, 512, ...) when WebGL1 must be supported.


---

## PerspectiveMesh

A textured plane warped to four corner points (tilted card, fake floor). It projects a subdivided vertex grid; UVs stay a regular grid and interpolate linearly per triangle, so density sets the quality. There is no Z axis, depth buffer or camera; real 3D needs a 3D library.

```ts
const card = new PerspectiveMesh({
  texture: tex,
  verticesX: 20,
  verticesY: 20,
  x0: 0, y0: 0, // texture top-left
  x1: 300, y1: 30, // top-right
  x2: 280, y2: 300, // bottom-right
  x3: 20, y3: 280, // bottom-left
});

app.ticker.add(() => {
  const wave = Math.sin(performance.now() / 1000) * 30;
  card.setCorners(0, wave, 200, -wave, 200, 200, 0, 200);
});
```

Corners go clockwise from the top-left: corner `0` receives the texture's top-left, `1` top-right, `2` bottom-right, `3` bottom-left, whatever their screen positions. For a floor, put corners 0 and 1 (the texture's top edge) higher and closer together. Keep the quad convex; a bow-tie or non-convex quad produces artifacts. `setCorners(x0, y0, x1, y1, x2, y2, x3, y3)` updates the geometry in place.

Options: the options type is `PerspectivePlaneOptions` (not `PerspectiveMeshOptions`), extending `MeshPlaneOptions`. Defaults: `texture` `Texture.WHITE`, `verticesX`/`verticesY` `10`, corners forming a 100x100 square (`x1`, `x2`, `y2`, `y3` = `100`, the rest `0`); `PerspectiveMesh.defaultOptions` overrides them globally. `geometry` is not an option (it builds a `PerspectivePlaneGeometry`); `shader`, `state` and `roundPixels` behave as on [Mesh](07-mesh.md).

Density: a 2×2 grid is two triangles and shows no perspective correction, 5×5 shows obvious triangular stretching, 20×20 is a good default; use more than 10×10 for any visible tilt.

Assigning a new `texture` rebuilds the geometry to the new dimensions and keeps the corners.
