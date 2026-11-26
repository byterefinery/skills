---
name: three-js-0-187-0
description: Three.js r187 (0.187.0) — comprehensive guide for building 3D graphics on the web with WebGL 2 and WebGPU. Covers the scene graph, materials and PBR, geometries and instancing, math, textures, lighting and shadows, TSL node shading, post-processing, loaders and GLTF, animation and skinning, controls and addons, WebXR, GPGPU compute, and color management. Use when building 3D scenes with three.js 0.187.x, writing TSL node shaders, choosing between WebGLRenderer and WebGPURenderer, loading models, or animating 3D assets.
license: MIT
metadata:
  tags:
    - javascript
    - 3d
    - graphics
    - webgl
    - webgpu
    - tsl
---

# three-js 0.187.0

Three.js r187 is a cross-browser JavaScript 3D library. The current builds include WebGL and WebGPU renderers (SVG and CSS3D renderers are available as addons). It provides a node-based shading system (TSL), physically-based rendering, compute shaders, and a unified renderer architecture with automatic WebGPU-to-WebGL2 fallback.

## Overview

- **Package**: `three@0.187.0` (ESM-first, CommonJS via `build/three.cjs`)
- **REVISION**: `'187'`
- **Renderers**: `WebGLRenderer` (WebGL 2 only; WebGL 1 dropped since r163), `WebGPURenderer` (WebGPU with automatic WebGL 2 fallback)
- **Shading**: Legacy `ShaderMaterial` (GLSL strings) + node-based materials and TSL (Three.js Shading Language)
- **Color**: `ColorManagement` with `LinearSRGBColorSpace` as working space; `renderer.outputColorSpace` defaults to `SRGBColorSpace`
- **Post-processing**: `EffectComposer` (WebGL) / `RenderPipeline` (WebGPU, node-based)
- **Compute**: `compute()` TSL function + `ComputeNode`, dispatched via `renderer.compute()`
- **Addons**: Controls, loaders, post-processing, physics, environments, inspector — all under `three/addons/`

### Entry Points

| Import | Description |
|---|---|
| `three` | Core + `WebGLRenderer` (main build) |
| `three/webgpu` | Core + `WebGPURenderer`, node materials, compute, storage buffers |
| `three/tsl` | TSL functions only (lightweight, no renderer) |
| `three/addons/...` | Controls, loaders, post-processing, helpers, TSL display/lighting nodes |
| `three/src/...` | Direct source modules (build-tool use) |

### Quick Start

```js
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const width = window.innerWidth, height = window.innerHeight;

const camera = new THREE.PerspectiveCamera( 50, width / height, 0.1, 1000 );
camera.position.set( 0, 2, 5 );

const scene = new THREE.Scene();

const geometry = new THREE.BoxGeometry( 1, 1, 1 );
const material = new THREE.MeshStandardMaterial( { color: 'steelblue' } );
const mesh = new THREE.Mesh( geometry, material );
scene.add( mesh );

const light = new THREE.DirectionalLight( 0xffffff, 2 );
light.position.set( 5, 10, 7 );
scene.add( light );

const renderer = new THREE.WebGLRenderer( { antialias: true } );
renderer.setSize( width, height );
renderer.setAnimationLoop( animate );
document.body.appendChild( renderer.domElement );

const controls = new OrbitControls( camera, renderer.domElement );

function animate( time ) {
	controls.update();
	mesh.rotation.y = time / 1000;
	renderer.render( scene, camera );
}
```

Browser examples use an import map:

```html
<script type="importmap">
	{
		"imports": {
			"three": "../build/three.module.js",
			"three/addons/": "./jsm/"
		}
	}
</script>
```

WebGPU examples map `three/webgpu` and `three/tsl` to `build/three.webgpu.js` / `build/three.tsl.js`.

## References

- [01-core-architecture](references/01-core-architecture.md) — Scene graph, Object3D, groups, layers, render order, clipping, culling
- [02-renderers](references/02-renderers.md) — WebGLRenderer, WebGPURenderer, render targets, capabilities
- [03-materials](references/03-materials.md) — Material hierarchy, PBR, MeshPhysicalMaterial, ShaderMaterial
- [04-geometries](references/04-geometries.md) — BufferGeometry, built-in geometries, custom attributes, instancing, BatchedMesh
- [05-math](references/05-math.md) — Vectors, matrices, quaternions, Euler, color, ray, frustum, MathUtils
- [06-textures](references/06-textures.md) — Texture types, formats, filtering, wrapping, compression, PMREM
- [07-lighting](references/07-lighting.md) — Light types, shadows, environment maps, IES/projector lights
- [08-nodes-tsl](references/08-nodes-tsl.md) — TSL (Three.js Shading Language), node materials, accessors, compute()
- [09-postprocessing](references/09-postprocessing.md) — EffectComposer (WebGL), RenderPipeline (WebGPU), passes
- [10-loaders](references/10-loaders.md) — GLTFLoader, DRACO/KTX2, texture loaders, splat loaders, format list
- [11-animation](references/11-animation.md) — AnimationMixer, clips, keyframe tracks, morph targets, skinned meshes
- [12-controls-addons](references/12-controls-addons.md) — OrbitControls, TransformControls, InteractionManager, physics, environments
- [13-webxr](references/13-webxr.md) — XR sessions, controllers, hand tracking, AR/VR buttons, depth sensing
- [14-gpgpu](references/14-gpgpu.md) — compute(), ComputeNode, storage textures/buffers, dispatch
- [15-color-management](references/15-color-management.md) — Color spaces, ColorManagement, tone mapping, output transforms

## Gotchas

- **`three` main build does not include WebGPU** — `WebGPURenderer`, node materials, `compute()`, and storage buffers come from `three/webgpu`. TSL functions come from `three/tsl`. Mixing imports across builds causes duplicated node state.
- **`WebGPURenderer` auto-falls back to WebGL 2** — if WebGPU is unavailable it warns and runs the WebGL 2 backend. Use `forceWebGL: true` to force it. Both renderers expose the same `render()`, `setAnimationLoop()`, and `domElement` API.
- **Standard materials work with `WebGPURenderer`** — `MeshStandardMaterial` etc. are auto-converted to their node equivalents. Node materials (`MeshBasicNodeMaterial`, ...) are needed only when wiring TSL nodes into material properties.
- **`PostProcessing` is deprecated** — renamed to `RenderPipeline` since r183; the old name only exists as a backward-compatibility wrapper that logs a warning. Use `RenderPipeline` with `three/webgpu`.
- **`EffectComposer` is WebGL-only** — for WebGPU post-processing use `RenderPipeline` + TSL passes (`pass( scene, camera )` from `three/tsl`). When using a composer, call `composer.render()`, not `renderer.render()`.
- **`renderer.outputColorSpace` defaults to `SRGBColorSpace`** — you do not need to set it. `renderer.toneMapping` defaults to `NoToneMapping`; set `ACESFilmicToneMapping` (or similar) deliberately for HDR content.
- **`controls.update()` must be called every frame** when `enableDamping` or `autoRotate` is true on `OrbitControls`.
- **Geometry disposal** — call `geometry.dispose()` and `material.dispose()` (plus `material.map.dispose()`) when removing objects to avoid GPU memory leaks.
- **`Raycaster` needs `setFromCamera()`** — call `raycaster.setFromCamera( mouse, camera )` before `intersectObjects()`; the mouse vector must be normalized `[-1, 1]` device coordinates.
- **`InstancedMesh` count is fixed at construction** — use `setMatrixAt()` / `setColorAt()` per instance; set `instanceMatrix.needsUpdate = true` after updates.
- **`BufferGeometry` attributes are fixed once uploaded** — dimensions, format, and type cannot change; replace the attribute instead. Set `needsUpdate = true` after modifying data in place.
- **`GLTFLoader` is async** — use `await` or callbacks. Pair with `DRACOLoader` and `KTX2Loader` for compressed assets; both need decoder paths set before loading.
- **`Euler` order matters** — default is `'XYZ'`; valid orders are `'XYZ'`, `'YZX'`, `'ZXY'`, `'XZY'`, `'YXZ'`, `'ZXZ'`. Prefer quaternions for interpolation to avoid gimbal lock.
- **`LightProbeGenerator` and `RoomEnvironment` take no renderer** — `RoomEnvironment` and `DebugEnvironment` are `Scene` subclasses with zero-argument constructors; feed them to `pmremGenerator.fromScene()`.
- **Rapier/Jolt physics are async factories** — `await RapierPhysics()` before use; the WASM must initialize first.
- **`PMREMGenerator` must be disposed** — always call `pmremGenerator.dispose()` after generating environment maps.
- **`scene.environment` vs `material.envMap`** — `scene.environment` sets a shared environment map for physical materials; individual `material.envMap` overrides it.
