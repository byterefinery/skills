# Renderers

## WebGLRenderer

WebGL 2 renderer. WebGL 1 has been dropped since r163.

### Construction

```js
const renderer = new THREE.WebGLRenderer( {
	canvas: null,               // Custom canvas element (auto-created if null)
	context: null,              // Custom WebGL2RenderingContext
	depth: true,                // Depth buffer
	stencil: false,             // Stencil buffer
	alpha: false,               // Transparent background
	antialias: false,           // MSAA anti-aliasing
	premultipliedAlpha: true,   // Premultiply alpha channel
	preserveDrawingBuffer: false, // Allow readback of canvas
	powerPreference: 'default', // 'default' | 'low-power' | 'high-performance'
} );
```

### Output Settings

```js
renderer.setSize( width, height, style );
renderer.setPixelRatio( value );
renderer.domElement;            // The canvas element

// Color output — defaults to SRGBColorSpace, no need to set
renderer.outputColorSpace;      // THREE.SRGBColorSpace (default)

// Tone mapping — defaults to NoToneMapping
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;

// Available tone mappings:
// NoToneMapping, LinearToneMapping, ReinhardToneMapping,
// CineonToneMapping, ACESFilmicToneMapping, CustomToneMapping,
// AgXToneMapping, NeutralToneMapping
```

### Rendering

```js
renderer.render( scene, camera );
renderer.render( scene, camera, renderTarget, forceClear );

// Animation loop (preferred over requestAnimationFrame)
renderer.setAnimationLoop( function ( time ) { /* ... */ } );
```

### Shadows

```js
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
// Types: BasicShadowMap, PCFShadowMap, PCFSoftShadowMap, VSMShadowMap
```

### Info

```js
renderer.info.render.calls;      // Number of draw calls
renderer.info.render.triangles;  // Number of triangles
renderer.info.memory.geometries; // Number of geometries in GPU
renderer.info.memory.textures;   // Number of textures in GPU
renderer.info.programs;          // Shader programs
```

### Dispose

```js
renderer.dispose(); // Frees all shader programs and GPU resources
```

## WebGPURenderer

Unified renderer targeting WebGPU with automatic WebGL 2 fallback. If WebGPU is unavailable, it warns and falls back to the WebGL 2 backend.

```js
import * as THREE from 'three/webgpu';

const renderer = new THREE.WebGPURenderer( {
	logarithmicDepthBuffer: false, // Log depth (ignored with reversed depth)
	reversedDepthBuffer: false,   // Reversed depth buffer
	alpha: true,                  // Transparent canvas
	depth: true,                  // Depth buffer
	stencil: false,               // Stencil buffer
	antialias: false,             // MSAA (4 samples by default when true)
	samples: 0,                   // Override MSAA sample count (0 = default)
	forceWebGL: false,            // Use WebGL 2 backend unconditionally
	multiview: false,             // Multiview for WebXR
	outputType: undefined,        // Canvas output format (device preferred)
	outputBufferType: THREE.HalfFloatType, // HalfFloatType (quality) or UnsignedByteType (memory)
} );

renderer.setSize( window.innerWidth, window.innerHeight );
renderer.setAnimationLoop( animate );
document.body.appendChild( renderer.domElement );
```

### Capabilities Check

```js
import { WebGPU } from 'three/addons/capabilities/WebGPU.js';

if ( WebGPU.isAvailable() === false ) {
	document.body.appendChild( WebGPU.getErrorMessage() );
}
```

### Compute

`renderer.compute( computeNode )` dispatches a compute node (see GPGPU reference). Use `renderer.computeAsync()` when the backend may not be initialized yet.

## Render Targets

### WebGLRenderTarget

```js
const target = new THREE.WebGLRenderTarget( width, height, {
	colorSpace: THREE.SRGBColorSpace,
	type: THREE.HalfFloatType,
	format: THREE.RGBAFormat,
	stencilBuffer: false,
	depthBuffer: true,
	depthTexture: null,
	generateMipmaps: false,
	minFilter: THREE.LinearFilter,
	magFilter: THREE.LinearFilter,
	wrapS: THREE.ClampToEdgeWrapping,
	wrapT: THREE.ClampToEdgeWrapping,
} );

// Render to target
renderer.setRenderTarget( target );
renderer.render( scene, camera );
renderer.setRenderTarget( null ); // Back to screen

// Dispose
target.dispose();
```

### WebGLCubeRenderTarget

```js
const cubeTarget = new THREE.WebGLCubeRenderTarget( size, {
	format: THREE.RGBAFormat,
	type: THREE.HalfFloatType,
	generateMipmaps: true,
	minFilter: THREE.LinearMipmapLinearFilter,
} );
```

### 3D and Array Targets

```js
// 3D texture target
const target3D = new THREE.WebGL3DRenderTarget( width, height, depth );

// Array texture target
const arrayTarget = new THREE.WebGLArrayRenderTarget( width, height, depthLayers );
```

### CubeRenderTarget (WebGPU build)

```js
import { CubeRenderTarget } from 'three/webgpu';
const cubeTarget = new CubeRenderTarget( size );
```

## Capabilities

```js
const caps = renderer.capabilities;
caps.maxAnisotropy;        // Max anisotropy value
caps.maxTextureSize;       // Max texture dimension
caps.precision;            // Shader precision support
```

## Viewport and Scissor

For mixed 2D/3D or layer-based rendering:

```js
renderer.setScissorTest( true );
renderer.setScissor( x, y, width, height );
renderer.setViewport( x, y, width, height );
```
