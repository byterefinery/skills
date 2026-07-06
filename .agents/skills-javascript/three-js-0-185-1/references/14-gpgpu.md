# GPGPU (Compute Shaders)

## Overview

GPGPU (General-Purpose computing on GPU) uses compute shaders for parallel data processing. Available via `WebGPURenderer` with `ComputeNode`.

## ComputeNode

```js
import { ComputeNode } from 'three/webgpu';
import { workgroupSize, workgroupId, localIndex, localSize } from 'three/tsl';

const compute = new ComputeNode(
	// Compute shader body — returns void
	() => {
		// Global invocation ID
		const globalId = workgroupId.mul( localSize ).add( localIndex );

		// Your compute logic here
		// ...
	},
	[ 64 ] // Workgroup size [x, y, z]
);

// Dispatch
compute.dispatch( numWorkgroupsX, numWorkgroupsY, numWorkgroupsZ );
```

## Storage Buffers

```js
import { StorageBufferAttribute } from 'three/webgpu';

// Create storage buffer
const data = new Float32Array( 1024 );
const buffer = new THREE.StorageBufferAttribute( data, 1 );

// Read/write in compute shader
import { storage } from 'three/tsl';
const storageBuffer = storage( buffer, 'read_write' ); // 'read_only', 'read_write'
```

## Storage Textures

```js
import { StorageTexture } from 'three/webgpu';

// Create storage texture
const texture = new THREE.StorageTexture(
	width,
	height,
	THREE.RGBAFormat,
	THREE.FloatType,
	'read_write' // 'read_only', 'read_write'
);

// 3D storage texture
const texture3D = new THREE.Storage3DTexture(
	width,
	height,
	depth,
	THREE.RGBAFormat,
	THREE.FloatType,
	'read_write'
);

// Array storage texture
const arrayTexture = new THREE.StorageArrayTexture(
	width,
	height,
	depth,
	THREE.RGBAFormat,
	THREE.FloatType,
	'read_write'
);
```

## Workgroup Memory

```js
import { workgroupSize, workgroupId, localIndex, localSize, barrier } from 'three/tsl';

// Shared workgroup memory
const shared = new THREE.StorageBufferAttribute( new Float32Array( 64 ), 1 );

// Barrier — synchronize within workgroup
barrier();
```

## GPGPU Patterns

### Particle System

```js
// Position buffer
const positions = new Float32Array( count * 3 );
const velocities = new Float32Array( count * 3 );

const positionBuffer = new THREE.StorageBufferAttribute( positions, 3 );
const velocityBuffer = new THREE.StorageBufferAttribute( velocities, 3 );

// Compute shader
const particleCompute = new ComputeNode(
	() => {
		const id = workgroupId.x.mul( localSize.x ).add( localIndex.x );

		// Read current state
		const pos = positionBuffer[ id ];
		const vel = velocityBuffer[ id ];

		// Update physics
		const newPos = pos.add( vel.mul( dt ) );
		const newVel = vel.add( acceleration.mul( dt ) );

		// Write back
		positionBuffer[ id ] = newPos;
		velocityBuffer[ id ] = newVel;
	},
	[ 64 ]
);

// Dispatch
const numWorkgroups = Math.ceil( count / 64 );
particleCompute.dispatch( numWorkgroups, 1, 1 );
```

### Blur / Image Processing

```js
// Read from regular texture, write to storage texture
const inputTexture = new THREE.StorageTexture( width, height, THREE.RGBAFormat, THREE.FloatType, 'read_only' );
const outputTexture = new THREE.StorageTexture( width, height, THREE.RGBAFormat, THREE.FloatType, 'read_write' );

const blurCompute = new ComputeNode(
	() => {
		const x = workgroupId.x.mul( localSize.x ).add( localIndex.x );
		const y = workgroupId.y.mul( localSize.y ).add( localIndex.y );

		// Sample neighbors and average
		let sum = vec3( 0 );
		for ( let dy = -radius; dy <= radius; dy ++ ) {
			for ( let dx = -radius; dx <= radius; dx ++ ) {
				sum = sum.add( inputTexture[ vec2( x + dx, y + dy ) ].rgb );
			}
		}
		sum = sum.div( ( radius * 2 + 1 ) ** 2 );

		outputTexture[ vec2( x, y ) ] = vec4( sum, 1.0 );
	},
	[ 8, 8 ]
);

const numWorkgroupsX = Math.ceil( width / 8 );
const numWorkgroupsY = Math.ceil( height / 8 );
blurCompute.dispatch( numWorkgroupsX, numWorkgroupsY, 1 );
```

### Sort / Reduce

```js
// Parallel reduce pattern
const reduceCompute = new ComputeNode(
	() => {
		const localId = localIndex.x;
		const localSizeVal = localSize.x;

		// Load into shared memory
		const globalId = workgroupId.x.mul( localSize.x ).add( localId );
		shared[ localId ] = inputBuffer[ globalId ];
		barrier();

		// Parallel reduce in shared memory
		for ( let stride = localSizeVal / 2; stride > 0; stride /= 2 ) {
			barrier();
			if ( localId < stride ) {
				shared[ localId ] = shared[ localId ] + shared[ localId + stride ];
			}
		}

		// Write result
		if ( localId == 0 ) {
			outputBuffer[ workgroupId.x ] = shared[ 0 ];
		}
	},
	[ 64 ]
);
```

## Atomic Operations

```js
import { atomicAdd, atomicAnd, atomicOr, atomicXor, atomicMin, atomicMax, atomicCompSwap } from 'three/tsl';

// Atomic increment
atomicAdd( counter, 1 );

// Atomic compare-and-swap
atomicCompSwap( value, expected, desired );
```

## Subgroup Operations

```js
import { subgroupAdd, subgroupAnd, subgroupOr, subgroupXor, subgroupMin, subgroupMax } from 'three/tsl';

// Subgroup (wavefront) operations
const sum = subgroupAdd( value );
const all = subgroupAnd( condition );
const any = subgroupOr( condition );
```

## GPGPU Gotchas

- **WebGPU only** — compute shaders require `WebGPURenderer`. Not available with `WebGLRenderer`.
- **Workgroup size limits** — typically max 256-1024 total invocations per workgroup. Check device limits.
- **Storage buffer alignment** — data must be properly aligned (typically 16-256 bytes).
- **Barrier synchronization** — `barrier()` only synchronizes within a workgroup, not across workgroups.
- **Memory ordering** — use `barrier()` after writing shared memory before other threads read it.
- **Dispatch count** — `dispatch(x, y, z)` specifies number of workgroups, not invocations.
- **Read-write textures** — storage textures must be explicitly marked `read_write`. Regular textures are read-only in compute shaders.
- **No recursion** — compute shaders do not support recursive function calls.
- **Limited precision** — some devices have limited precision for float operations in compute shaders.
