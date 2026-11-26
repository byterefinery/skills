# Nodes and TSL (Three.js Shading Language)

TSL is the node-based shading system for Three.js, built to support the rendering capabilities introduced by WebGPU. Shader logic is written in JavaScript and structured as a graph of nodes, giving full IDE autocomplete and instant feedback. TSL is backend-agnostic: the same expressions compile to WGSL (WebGPU) or GLSL (WebGL) behind the scenes.

The official TSL guide in the repository lives at `tsl/content/Guide.md` and the hosted version at https://threejs.org/tsl/.

### Import Paths

```js
// TSL functions (no renderer needed)
import { vec3, mix, positionLocal, Fn } from 'three/tsl';

// Renderer + node materials + compute + storage
import * as THREE from 'three/webgpu';

// TSL addon nodes (display, lighting, math, shadows, utils)
import { dotScreen } from 'three/addons/tsl/display/DotScreenNode.js';
import { rgbShift } from 'three/addons/tsl/display/RGBShiftNode.js';
```

## Core Concepts

### Values and Types

TSL wraps JavaScript values into typed nodes. Type constructors:

```js
import { float, int, uint, bool, vec2, vec3, vec4, mat2, mat3, mat4, arr } from 'three/tsl';

float( 1.0 );
vec3( 1.0, 2.0, 3.0 );
vec4( 1.0, 2.0, 3.0, 4.0 );
```

Uniforms are created from plain values and can be mutated at runtime:

```js
import { uniform } from 'three/tsl';

const colorUniform = uniform( new THREE.Color( 'red' ) );
colorUniform.value.set( 'blue' ); // picked up on the next frame
```

### Math Operations

TSL supports operator overloading, so plain JS operators work on nodes:

```js
import { add, sub, mul, div, mod, mix, smoothstep, clamp, dot, cross, length, normalize } from 'three/tsl';

// These are equivalent:
add( a, b );
a + b;

mix( a, b, t );        // lerp
smoothstep( edge0, edge1, x );
clamp( x, minVal, maxVal );
normalize( v );
```

Method chaining is also available on node values (`.mul()`, `.add()`, `.negate()`, `.cross()`, `.reflect()`, `.refract()`, `.toVarying()`, `.toVar()`, ...).

### Control Flow and Functions

```js
import { Fn, Loop } from 'three/tsl';

// Fn( jsFunc, layout ) — layout is the return type ('vec3') or { return: 'vec3' }
const scale = Fn( ( color ) => color.mul( 2.0 ), 'vec3' );

// Loops
Loop( () => { /* ... */ } );
```

WGSL-only logic can be inlined with `wgslFn`.

### Accessor Nodes

Accessors read built-in shader data (verified names from `src/nodes/accessors/`):

```js
import {
	// Position
	positionLocal,        // model space
	positionView,         // view space
	positionWorld,        // world space
	positionViewDirection,
	positionWorldDirection,

	// Normal
	normalLocal, normalView, normalWorld, normalFlat,

	// UV / color / vertex data
	uv,                   // uv( set )
	color,                // vertex color
	vertexColor,

	// Camera and model
	cameraPosition,
	cameraProjectionMatrix,
	modelMatrix, modelViewMatrix, modelViewProjectionMatrix,

	// Material properties
	materialColor, materialEmissive, materialOpacity,
	materialRoughness, materialMetalness, materialNormal, materialAO,

	// Time and frame
	time,                 // current frame time (seconds)
	frameId,
} from 'three/tsl';
```

### Texture Sampling

```js
import { texture, textureBicubic, textureGrad } from 'three/tsl';

const color = texture( myTexture, uv );
const colorBicubic = textureBicubic( myTexture, uv );
```

### Utility Nodes

```js
import {
	remap,           // remap( value, inMin, inMax, outMin, outMax )
	triplanarTexture,// triplanar texturing
	screenUV,
	oscSine,         // oscillator: oscSine( speed )
	pass,            // pass( scene, camera ) — scene pass node for post-processing
} from 'three/tsl';
```

Addon TSL nodes live under `three/addons/tsl/`:

- `display/` — `bloom`, `dotScreen`, `rgbShift`, `outline`, `ssao`, `ssgi`, `ssr`, `fxaa`, `smaa`, `trAA`/`taau`, `motionBlur`, `lensflare`, ...
- `lighting/` — light and environment node helpers
- `math/` — extra math functions
- `shadows/` — shadow utilities
- `utils/` — general helpers

## Node Materials

Node materials let you wire TSL nodes into material properties. Standard materials (`MeshStandardMaterial`, ...) work with both renderers — node materials are only needed when assigning TSL nodes to material inputs.

### Pattern from the official examples

```js
import * as THREE from 'three/webgpu';
import { positionLocal, positionWorld, normalLocal } from 'three/tsl';

// PositionLocal as color
let material = new THREE.MeshBasicNodeMaterial();
material.colorNode = positionLocal;

// PositionWorld as color
material = new THREE.MeshBasicNodeMaterial();
material.colorNode = positionWorld;

// Normal as color
material = new THREE.MeshBasicNodeMaterial();
material.colorNode = normalLocal;
```

### Built-in Node Materials

From `three/webgpu`: `MeshBasicNodeMaterial`, `MeshStandardNodeMaterial`, `MeshPhysicalNodeMaterial`, `MeshPhongNodeMaterial`, `MeshLambertNodeMaterial`, `MeshMatcapNodeMaterial`, `MeshNormalNodeMaterial`, `MeshSSSNodeMaterial`, `PointsNodeMaterial`, `LineBasicNodeMaterial`, `LineDashedNodeMaterial`, `SpriteNodeMaterial`, `ShadowNodeMaterial`, `VolumeNodeMaterial`, `NodeMaterial` (base).

### Compute Shaders

See the [GPGPU reference](14-gpgpu.md) — compute logic is written with the same TSL functions and dispatched via `renderer.compute()`.

## Node Gotchas

- **TSL imports come from `three/tsl`** — the main `three` build exports core classes and `WebGLRenderer` only; it does not include TSL functions, node materials, or `WebGPURenderer`.
- **`Fn( jsFunc, layout )`** — the first argument is a function, the second (optional) is the return type as a string or `{ return: 'vec3' }`.
- **Uniforms mutate in place** — change `uniformNode.value` at runtime; no `needsUpdate` flag is needed on TSL uniform nodes.
- **Node values are immutable** — operations produce new nodes; reuse node expressions to avoid duplicated computation.
- **`pass( scene, camera )`** is the starting point for WebGPU post-processing chains (see Post-Processing reference).
- **`renderer.inspector = new Inspector()`** (from `three/addons/inspector/Inspector.js`) attaches a live node/material inspector for debugging TSL graphs.
