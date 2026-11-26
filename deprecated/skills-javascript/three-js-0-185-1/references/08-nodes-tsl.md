# Nodes and TSL (Three.js Shading Language)

## Overview

The node system provides a dataflow-based approach to shader programming. Nodes represent values and operations, connected in a graph that compiles to GLSL (WebGL) or WGSL (WebGPU).

### Import Paths

```js
// From main three package (GLSL nodes)
import { Node, vec3, mix, positionLocal } from 'three';

// From webgpu package (full node system + TSL)
import { vec3, mix, positionLocal, material } from 'three/webgpu';
import * as TSL from 'three/tsl';
```

## Core Concepts

### Nodes

A node represents a value in the shader graph. Nodes are typed and composable.

```js
// Input nodes — wrap JavaScript values
const uniform = new THREE.UniformNode( value );
const input = new THREE.InputNode( value, type );
const prop = new THREE.PropertyNode( value, type );

// Constant nodes
const constNode = new THREE.ConstNode( value, type );

// Parameter nodes — function parameters
const param = new THREE.ParameterNode( type );

// Assign nodes — assign to variables
const assign = new THREE.AssignNode( target, value );
```

### TSL Functions

TSL provides factory functions for creating nodes. These are the primary way to write shader logic.

#### Type Constructors

```js
import { float, int, uint, bool, vec2, vec3, vec4, mat2, mat3, mat4, arr } from 'three/tsl';

float( 1.0 );
int( 42 );
uint( 42u );
bool( true );
vec2( 1.0, 2.0 );
vec3( 1.0, 2.0, 3.0 );
vec4( 1.0, 2.0, 3.0, 4.0 );
mat3( /* 9 floats */ );
arr( 'float', 10 ); // Array of 10 floats
```

#### Math Operations

```js
import {
	add, sub, mul, div, mod,
	min, max, clamp, mix, smoothstep,
	step, sign, abs, floor, ceil, round, fract,
	exp, log, exp2, log2, sqrt, inversesqrt, pow,
	dot, cross, length, distance, normalize, faceforward, reflect, refract,
	sin, cos, tan, asin, acos, atan, atan2,
	matrixCompMult, transpose, determinant, inverse,
} from 'three/tsl';

add( a, b );           // a + b
mul( a, b );           // a * b
mix( a, b, t );        // lerp
smoothstep( edge0, edge1, x );
clamp( x, minVal, maxVal );
dot( a, b );
cross( a, b );
normalize( v );
```

Operators work directly with node values:

```js
// These are equivalent:
add( a, b );
a + b;

mul( a, b );
a * b;
```

#### Control Flow

```js
import { cond, loop, forLoop, whileLoop, break, continue, discard } from 'three/tsl';

// Conditional
cond( condition, trueExpr, falseExpr );

// Ternary shorthand
condition ? trueExpr : falseExpr;

// Loops
loop( condition, body );
forLoop( init, condition, increment, body );
whileLoop( condition, body );

// Discard fragment
discard();
```

#### Functions

```js
import { Fn, call } from 'three/tsl';

// Define a function
const myFunc = new Fn( 'vec3', ( color ) => {
	return color.mul( vec3( 2.0 ) );
} );

// Call a function
const result = myFunc.call( color );
```

### Accessor Nodes

Accessor nodes provide access to built-in shader data:

```js
// Position
import { positionLocal, positionView, positionWorld, positionClip } from 'three/tsl';
// positionLocal — local (model) space position
// positionView — view (camera) space position
// positionWorld — world space position
// positionClip — clip space position

// Normal
import { normalLocal, normalView, normalWorld, normalGeometry } from 'three/tsl';

// UV
import { uv } from 'three/tsl';
uv( 0 ); // UV set 0

// Material properties
import { materialColor, materialOpacity, materialEmissive, materialNormal, materialAO } from 'three/tsl';

// Camera
import { cameraPosition, cameraNear, cameraFar, cameraProjectionMatrix, cameraViewMatrix } from 'three/tsl';

// Model matrices
import { modelMatrix, modelViewMatrix, modelViewProjectionMatrix } from 'three/tsl';

// Instance
import { instanceMatrix, instanceColor } from 'three/tsl';

// Morph targets
import { morphTarget0, morphTarget1, /* ... */ } from 'three/tsl';

// Skin
import { skinning } from 'three/tsl';

// Vertex color
import { vertexColor } from 'three/tsl';

// Time
import { frameId, bufferTime, clock, mouse } from 'three/tsl';
```

### Texture Nodes

```js
import { texture, textureCompare, textureGrad, textureBicubic, textureSize } from 'three/tsl';

// Sample texture
const color = texture( textureNode, uvNode );

// With LOD
const color = texture( textureNode, uvNode, lod );

// Compare (depth textures)
const depth = textureCompare( depthTexture, uvNode );

// Bicubic filtering
const color = textureBicubic( textureNode, uvNode );

// Texture size
const size = textureSize( textureNode );
```

### Utility Nodes

```js
import {
	remap,           // remap( value, inMin, inMax, outMin, outMax )
	triplanar,       // Triplanar texturing
	reflector,       // Planar reflection
	rtt,             // Render-to-texture
	postProcessing,  // Post-processing utilities
	sample,          // Sampling utilities
	oscillate,       // Oscillator nodes (sine, square, saw, triangle)
	spriteSheetUV,   // Sprite sheet UV calculation
} from 'three/tsl';
```

## Node Materials

Node materials use the node system for shader generation. Required for `WebGPURenderer`.

### Base Class

```js
import { NodeMaterial } from 'three/webgpu';

class MyMaterial extends NodeMaterial {
	constructor( parameters = {} ) {
		super();

		this.colorNode = new THREE.ColorNode( parameters.color || new THREE.Color( 0xffffff ) );
		this.roughnessNode = new THREE.FloatNode( parameters.roughness ?? 0.5 );
	}

	getType( builder ) { return 'fragment'; }

	generateCode( builder ) {
		const color = this.colorNode.build( builder );
		return `gl_FragColor = ${color};`;
	}
}
```

### Built-in Node Materials

```js
import {
	MeshStandardNodeMaterial,
	MeshPhysicalNodeMaterial,
	MeshBasicNodeMaterial,
	MeshPhongNodeMaterial,
	MeshLambertNodeMaterial,
	MeshMatcapNodeMaterial,
	MeshNormalNodeMaterial,
	MeshSSSNodeMaterial,       // Subsurface scattering
	PointsNodeMaterial,
	LineBasicNodeMaterial,
	LineDashedNodeMaterial,
	SpriteNodeMaterial,
	ShadowNodeMaterial,
	VolumeNodeMaterial,
} from 'three/webgpu';
```

### Custom Node Material with TSL

```js
import { NodeMaterial, NodeMaterialInstance } from 'three/webgpu';
import { vec3, positionLocal, materialColor, output } from 'three/tsl';

class GradientMaterial extends NodeMaterial {
	constructor( parameters = {} ) {
		super();

		this.topColor = new THREE.ColorNode( parameters.topColor || new THREE.Color( 'blue' ) );
		this.bottomColor = new THREE.ColorNode( parameters.bottomColor || new THREE.Color( 'white' ) );
	}

	getType( builder ) { return 'fragment'; }

	getOutputType( builder ) { return 'vec4'; }

	build( builder ) {
		const pos = positionLocal;
		const t = pos.y.mul( 0.5 ).add( 0.5 );
		const color = mix( this.bottomColor, this.topColor, t );
		return vec4( color, 1.0 );
	}
}
```

### NodeMaterialObserver

Automatically tracks which shader features are used and only compiles what's needed:

```js
// Used internally by NodeMaterial
// Automatically enables/disables features based on material properties
```

## Compute Shaders (GPGPU)

```js
import { ComputeNode, workgroupSize } from 'three/tsl';

const compute = new ComputeNode(
	// Compute shader body
	() => {
		const localId = workgroupId.mul( workgroupSize ).add( localIndex );
		// ... compute logic
	},
	[ 64 ] // workgroup size
);
```

## Node Gotchas

- **Node values are immutable** — creating a new node for each operation. Reuse nodes to avoid duplication.
- **Type inference** — TSL infers types from context. Explicit type constructors (`float()`, `vec3()`) help resolve ambiguity.
- **`needsUpdate`** — set `node.needsUpdate = true` when modifying uniform values at runtime.
- **Node materials are required for WebGPU** — standard materials (`MeshStandardMaterial`) work only with `WebGLRenderer`.
- **TSL from `three/webgpu`** — the full TSL is exported from the webgpu build. The main `three` package has limited TSL exports.
- **`Fn` caching** — function nodes are cached by signature. Reuse function definitions across materials.
- **`discard()`** — available in fragment shaders. Use for alpha testing or shape clipping.
