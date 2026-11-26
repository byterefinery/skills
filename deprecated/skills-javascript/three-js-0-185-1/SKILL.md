---
name: three-js-0-185-1
description: Three.js r185 (0.185.1) — comprehensive guide for building 3D graphics with WebGL/WebGPU. Covers core scene graph, materials hierarchy, geometries, nodes/TSL shading system, WebGPURenderer, post-processing, loaders, controls, WebXR, animation, color management, and GPGPU compute shaders. Use when working with three.js version 0.185.x, setting up 3D rendering pipelines, writing node materials, or migrating between WebGLRenderer and WebGPURenderer.
metadata:
  tags:
    - javascript
    - 3d
    - graphics
    - webgl
    - webgpu
    - shaders
---

# three-js 0.185.1

Three.js r185 is a JavaScript 3D library supporting WebGL 2 and WebGPU backends. It provides a node-based shading system (TSL), physically-based rendering, compute shaders, and a unified renderer architecture.

## Overview

- **Package**: `three@0.185.1` (ESM-first, CommonJS via `three.cjs`)
- **REVISION**: `'185'`
- **Renderers**: `WebGLRenderer` (WebGL 2 only, WebGL 1 dropped since r163), `WebGPURenderer` (WebGPU with WebGL 2 fallback)
- **Shading**: Legacy `ShaderMaterial` + node-based `NodeMaterial` / TSL system
- **Color**: `ColorManagement` with `LinearSRGBColorSpace` as default working space; textures use `NoColorSpace` by default
- **Post-processing**: `EffectComposer` (WebGL) / `RenderPipeline` (WebGPU)
- **Compute**: `ComputeNode` for GPGPU via WebGPU compute shaders
- **Addons**: Controls, loaders, post-processing passes, physics, environments — all under `three/addons/`

### Entry Points

| Import | Description |
|---|---|
| `three` | Full WebGL build (core + WebGLRenderer) |
| `three/webgpu` | WebGPU build (core + WebGPURenderer + node materials + TSL) |
| `three/tsl` | TSL functions only (lightweight, no renderer) |
| `three/addons/...` | Controls, loaders, post-processing, helpers |

### Quick Start

```js
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const renderer = new THREE.WebGLRenderer( { antialias: true } );
renderer.setSize( window.innerWidth, window.innerHeight );
renderer.setPixelRatio( window.devicePixelRatio );
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild( renderer.domElement );

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera( 50, window.innerWidth / window.innerHeight, 0.1, 1000 );
camera.position.set( 0, 2, 5 );

const controls = new OrbitControls( camera, renderer.domElement );

const geometry = new THREE.BoxGeometry( 1, 1, 1 );
const material = new THREE.MeshStandardMaterial( { color: 'steelblue' } );
const mesh = new THREE.Mesh( geometry, material );
scene.add( mesh );

const light = new THREE.DirectionalLight( 0xffffff, 2 );
light.position.set( 5, 10, 7 );
scene.add( light );

function animate() {
	requestAnimationFrame( animate );
	controls.update();
	renderer.render( scene, camera );
}
animate();
```

## References

- [01-core-architecture](references/01-core-architecture.md) — Scene graph, Object3D, Object lifecycle, groups, layers
- [02-renderers](references/02-renderers.md) — WebGLRenderer, WebGPURenderer, render targets, capabilities
- [03-materials](references/03-materials.md) — Material hierarchy, PBR, MeshPhysicalMaterial, ShaderMaterial
- [04-geometries](references/04-geometries.md) — BufferGeometry, built-in geometries, custom attributes, instancing
- [05-math](references/05-math.md) — Vectors, matrices, quaternions, Euler, color, ray, frustum
- [06-textures](references/06-textures.md) — Texture types, formats, filtering, wrapping, compression, PMREM
- [07-lighting](references/07-lighting.md) — Light types, shadows, environment maps, light probes
- [08-nodes-tsl](references/08-nodes-tsl.md) — Node system, TSL functions, node materials, custom shaders
- [09-postprocessing](references/09-postprocessing.md) — EffectComposer (WebGL), RenderPipeline (WebGPU), passes
- [10-loaders](references/10-loaders.md) — GLTFLoader, OBJLoader, texture loaders, compressed textures
- [11-animation](references/11-animation.md) — AnimationMixer, clips, keyframe tracks, morph targets, skinned meshes
- [12-controls-addons](references/12-controls-addons.md) — OrbitControls, TransformControls, physics, environments
- [13-webxr](references/13-webxr.md) — WebXR session management, controllers, hit testing, depth sensing
- [14-gpgpu](references/14-gpgpu.md) — ComputeNode, storage buffers/textures, workgroups, GPGPU patterns
- [15-color-management](references/15-color-management.md) — Color spaces, ColorManagement, tone mapping, output transforms

## Gotchas

- **WebGL 1 is not supported** — dropped since r163. `WebGLRenderer` requires WebGL 2. Use `WebGPURenderer` with `forceWebGL: false` for automatic WebGPU-first with fallback.
- **`outputColorSpace` is required** — set `renderer.outputColorSpace = SRGBColorSpace` (or use `OutputPass` in post-processing). Without it, colors look washed out.
- **Texture colorSpace defaults to `NoColorSpace`** — color textures loaded via `TextureLoader` auto-detect `srgb`. Non-color data (normal maps, AO maps, roughness) must stay `NoColorSpace`. Explicitly set `texture.colorSpace = SRGBColorSpace` for color textures loaded from data arrays.
- **`MeshPhysicalMaterial` costs more** — every enabled feature (clearcoat, iridescence, sheen, transmission) adds per-pixel cost. Keep features disabled by default and enable only what you need.
- **`WebGPURenderer` is the future** — it auto-falls back to WebGL 2 when WebGPU is unavailable. Use it instead of `WebGLRenderer` for new projects. Node materials are required for WebGPU.
- **`PostProcessing` is deprecated** — renamed to `RenderPipeline` since r183. Use `RenderPipeline` with `WebGPURenderer`.
- **`EffectComposer` is WebGL-only** — it uses `WebGLRenderTarget` internally. For WebGPU, use `RenderPipeline` with node-based passes.
- **`renderer.render()` vs `composer.render()`** — when using post-processing, call `composer.render()` instead of `renderer.render()`. Mixing them causes double rendering.
- **`controls.update()` must be called** — required every frame when `enableDamping` or `autoRotate` is true on `OrbitControls`.
- **Geometry disposal** — call `geometry.dispose()` and `material.dispose()` (including `material.map.dispose()`) when removing objects to avoid GPU memory leaks.
- **`BufferGeometry` attributes are immutable after first use** — dimensions, format, and type cannot change. Dispose and recreate instead.
- **`Raycaster` needs `setFromCamera()`** — call `raycaster.setFromCamera( mouse, camera )` before `raycaster.intersectObjects()`. The mouse vector must be normalized `[-1, 1]` device coordinates.
- **`InstancedMesh` count is fixed** — set instance count at construction. Use `setMatrixAt()` / `setColorAt()` per instance. Call `instanceMatrix.needsUpdate = true` after bulk updates.
- **`Clock` vs `performance.now()`** — use `Clock` for delta time (`clock.getDelta()`) which handles tab sleeping. `performance.now()` does not.
- **`requestAnimationFrame` callback receives time** — prefer `clock.getDelta()` over computing delta from the callback's time argument for consistency.
- **Node materials are required for WebGPU** — `MeshStandardMaterial` etc. work with `WebGLRenderer`. For `WebGPURenderer`, use `MeshStandardNodeMaterial` or the node material equivalents.
- **`PMREMGenerator` must be disposed** — always call `pmremGenerator.dispose()` after generating environment maps to free internal render targets.
- **`scene.environment` vs `material.envMap`** — `scene.environment` sets a shared environment map for all physical materials, but individual `material.envMap` overrides it.
- **`GLTFLoader` is async** — it returns a promise. Use `await` or `.then()`. For production, pair with `DRACOLoader` and `KTX2Loader` for compressed assets.
- **`Euler` order matters** — default is `'XYZ'`. Use `object.rotation.set(x, y, z, 'YXZ')` for camera-like rotation (avoids gimbal lock on common orientations). Prefer quaternions for interpolation.
