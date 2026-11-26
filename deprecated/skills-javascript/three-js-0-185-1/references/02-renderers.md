# Renderers

## WebGLRenderer

WebGL 2 renderer. WebGL 1 has been dropped since r163.

### Construction

```js
const renderer = new THREE.WebGLRenderer( {
	canvas: null,           // Custom canvas element (auto-created if null)
	context: null,          // Custom WebGL2RenderingContext
	depth: true,            // Depth buffer
	stencil: false,         // Stencil buffer
	alpha: false,           // Transparent background
	antialias: false,       // MSAA anti-aliasing
	premultipliedAlpha: true, // Premultiply alpha channel
	preserveDrawingBuffer: false, // Allow readback of canvas
	powerPreference: 'default', // 'default' | 'low-power' | 'high-performance'
	stencil: false,
	depth: true,
} );
```

### Output Settings

```js
renderer.setSize( width, height, preserveDrawingBuffer );
renderer.setPixelRatio( value );
renderer.domElement;                    // The canvas element
renderer.setSize( window.innerWidth, window.innerHeight );

// Color output — required for correct colors
renderer.outputColorSpace = THREE.SRGBColorSpace;

// Tone mapping
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
renderer.info.render.textures;   // Number of textures created
renderer.info.render.programs;   // Number of shader programs
renderer.info.memory.geometries; // Number of geometries in GPU
```

### Dispose

```js
renderer.dispose(); // Frees all shader programs
```

## WebGPURenderer

Unified renderer targeting WebGPU with automatic WebGL 2 fallback.

### Construction

```js
import { WebGPURenderer } from 'three/webgpu';

const renderer = new WebGPURenderer( {
	logarithmicDepthBuffer: false,
	reversedDepthBuffer: false,
	alpha: true,
	depth: true,
	stencil: false,
	antialias: false,
	samples: 0,           // MSAA samples (default 4 when antialias: true)
	forceWebGL: false,    // Force WebGL 2 backend
	multiview: false,     // Multiview for WebXR
	outputType: undefined, // Device preferred format
	outputBufferType: THREE.HalfFloatType,
} );
```

### Key Differences from WebGLRenderer

| Feature | WebGLRenderer | WebGPURenderer |
|---|---|---|
| Materials | Standard materials | Node materials required |
| Post-processing | EffectComposer | RenderPipeline |
| Shading | ShaderMaterial | NodeMaterial / TSL |
| Compute | Not available | ComputeNode |
| Storage textures | Not available | StorageTexture |
| Fallback | N/A | Auto WebGL 2 |

### Node Materials

WebGPURenderer requires node-based materials:

```js
import { MeshStandardNodeMaterial } from 'three/webgpu';

const material = new MeshStandardNodeMaterial( {
	color: new THREE.Color( 'steelblue' ),
	roughness: 0.5,
	metalness: 0.0,
} );
```

Available node materials: `MeshStandardNodeMaterial`, `MeshPhysicalNodeMaterial`, `MeshBasicNodeMaterial`, `MeshPhongNodeMaterial`, `MeshLambertNodeMaterial`, `MeshMatcapNodeMaterial`, `MeshNormalNodeMaterial`, `MeshSSSNodeMaterial`, `PointsNodeMaterial`, `LineBasicNodeMaterial`, `LineDashedNodeMaterial`, `SpriteNodeMaterial`, `ShadowNodeMaterial`, `VolumeNodeMaterial`.

### RenderPipeline

Post-processing for WebGPU (replaces EffectComposer):

```js
import { RenderPipeline, pass } from 'three/webgpu';

const renderPipeline = new RenderPipeline( renderer );
const scenePass = pass( scene, camera );
renderPipeline.outputNode = scenePass;
```

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
	anisotropy: 1,
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

### WebGLRenderTarget (3D / Array)

```js
// 3D texture target
const target3D = new THREE.WebGL3DRenderTarget( width, height, depth );

// Array texture target
const arrayTarget = new THREE.WebGLArrayRenderTarget( width, height, depthLayers );
```

## Capabilities

```js
const caps = renderer.capabilities;
caps.maxAnisotropy;        // Max anisotropy value
caps.maxTextureSize;       // Max texture dimension
caps.isWebGL2;             // Always true (WebGL 1 not supported)
caps.precision.highFloat;  // High precision float support
caps.precision.highInt;    // High precision int support
```

## Extensions

```js
renderer.extensions.get( 'OES_texture_float_linear' );
renderer.extensions.get( 'EXT_color_buffer_float' );
renderer.extensions.get( 'WEBGL_depth_texture' );
```

## Multiple Renderers

For mixed 2D/3D or layer-based rendering:

```js
// Layer-based: render different layers with different renderers
renderer1.render( scene, camera ); // Layer 0
renderer2.render( scene, camera ); // Layer 1

// Or use viewport scissoring
renderer.setScissorTest( true );
renderer.setScissor( x, y, width, height );
renderer.setViewport( x, y, width, height );
```
