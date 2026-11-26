# GPGPU (Compute Shaders)

Compute shaders run on `WebGPURenderer`. Logic is written in TSL and dispatched with `renderer.compute()`. For the WebGL path there is also `GPUComputationRenderer` (addon, texture-based) — see `examples/jsm/gpgpu/`.

## Core API

```js
import * as THREE from 'three/webgpu';
import { compute, computeKernel, Fn, instanceIndex, instancedArray } from 'three/tsl';

// renderer.compute( computeNodes, dispatchSize = null )
// renderer.computeAsync( ... ) — use when the backend may not be initialized yet
```

- `compute( node, count, workgroupSize = [64] )` — TSL factory wrapping a node in a `ComputeNode`. `count` (number) auto-generates bounds checking against `instanceIndex`; a `[x, y, z]` array sets the explicit `dispatchSize`.
- `computeKernel( node, workgroupSize )` — same, but requires passing a dispatch size to `renderer.compute()`.
- `new ComputeNode( computeNode, workgroupSize )` — the class behind the factory.

## Pattern from the official example (`webgpu_compute_particles.html`)

```js
import * as THREE from 'three/webgpu';
import { Fn, If, float, vec3, hash, instanceIndex, instancedArray } from 'three/tsl';

const particleCount = 10000;

// Instanced data arrays (vec3 per element)
const positions = instancedArray( particleCount, 'vec3' );
const velocities = instancedArray( particleCount, 'vec3' );

// Init compute node — Fn body, called once, then .compute( count )
const computeInit = Fn( () => {

	const position = positions.element( instanceIndex );

	const amount = Math.sqrt( particleCount );
	const offset = float( amount / 2 );

	position.x = offset.sub( instanceIndex.mod( amount ) );
	position.z = offset.sub( instanceIndex.div( amount ) );

} )().compute( particleCount ).setName( 'Init Particles' );

// Update compute node — runs every frame
const computeUpdate = Fn( () => {

	const position = positions.element( instanceIndex );
	const velocity = velocities.element( instanceIndex );

	velocity.addAssign( vec3( 0.0, gravity, 0.0 ) );
	position.addAssign( velocity );

	If( position.y.lessThan( 0 ), () => {
		position.y = 0;
		velocity.y = velocity.y.negate().mul( bounce );
	} );

} );

const computeParticles = computeUpdate().compute( particleCount ).setName( 'Update Particles' );

// Dispatch — renderer.compute() expects a ComputeNode
renderer.compute( computeInit );      // one-time init

function animate() {
	renderer.compute( computeParticles );
	renderer.render( scene, camera );
}
renderer.setAnimationLoop( animate );
```

Reading compute results on the CPU: use `renderer.readRenderTargetPixels()` for render targets, or `ReadbackBuffer` (from `three/webgpu`) for async readback.

## Render Particles from Compute Data

```js
const material = new THREE.SpriteNodeMaterial();
material.positionNode = positions.toAttribute(); // feed instanced array as attribute
material.colorNode = uv().mul( colors.element( instanceIndex ) );
```

## Storage Textures and Buffers

From `three/webgpu`:

```js
// Storage textures — read/write texture targets
const storage = new THREE.StorageTexture( width, height );
const storage3D = new THREE.Storage3DTexture( width, height, depth );
const storageArray = new THREE.StorageArrayTexture( width, height, depth );

// Storage buffer attributes — per-instance GPU buffers
const attr = new THREE.StorageBufferAttribute( array, itemSize );
const instanced = new THREE.StorageInstancedBufferAttribute( array, itemSize );
const indirect = new THREE.IndirectStorageBufferAttribute( array, itemSize );
```

## GPGPU Gotchas

- **`renderer.compute()` needs a `ComputeNode`** — it throws for other node types. Wrap logic with `Fn(...)( ).compute( count )`.
- **Do not pass a dispatch size to `renderer.compute()`** for nodes created with `compute( count )` — the count is baked in. Use `computeKernel()` if you need a dynamic dispatch size.
- **`renderer.compute()` before backend init** — logs a warning and defers to `computeAsync()`; call compute after the first render or use `computeAsync()`.
- **Workgroup size defaults to `[64]`** — the total thread count should be a multiple of the workgroup size for full utilization.
- **`instanceIndex`** is the per-invocation index inside compute; use `.element( instanceIndex )` to index instanced arrays.
- **WebGL has no compute** — the WebGL fallback backend cannot dispatch compute; guard compute usage when targeting `forceWebGL` or WebGL-only browsers.
