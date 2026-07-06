# Lighting

## Light Types

### AmbientLight

Uniform illumination from all directions. Does not cast shadows.

```js
const light = new THREE.AmbientLight( color, intensity );
// color: Color | string | number (default: 0xffffff)
// intensity: number (default: 1)
```

### HemisphereLight

Gradient between sky and ground colors. No shadows.

```js
const light = new THREE.HemisphereLight( skyColor, groundColor, intensity );
light.position.set( 0, 1, 0 ); // Direction of sky color
```

### DirectionalLight

Parallel light from a direction (simulates the sun). Supports shadows.

```js
const light = new THREE.DirectionalLight( color, intensity );
light.position.set( 5, 10, 7 );
light.target.position.set( 0, 0, 0 );
// Or: light.target = object;

// Shadow settings
light.castShadow = true;
light.shadow.mapSize.width = 2048;
light.shadow.mapSize.height = 2048;
light.shadow.camera.near = 0.5;
light.shadow.camera.far = 500;
light.shadow.camera.left = -10;
light.shadow.camera.right = 10;
light.shadow.camera.top = 10;
light.shadow.camera.bottom = -10;
light.shadow.bias = -0.0001;
light.shadow.normalBias = 0.02;
light.shadow.radius = 4;               // Shadow blur (PCFSoft only)
light.shadow.autoUpdate = true;
light.shadow.mapSize.set( 2048, 2048 );
```

### PointLight

Omni-directional light at a position. Supports shadows.

```js
const light = new THREE.PointLight( color, intensity, distance, decay );
// distance: 0 = infinite range
// decay: 1 = physically-correct (inverse square), 2 = legacy

light.castShadow = true;
light.shadow.mapSize.set( 1024, 1024 );
light.shadow.bias = -0.0001;
```

### SpotLight

Cone-shaped light with angle. Supports shadows.

```js
const light = new THREE.SpotLight( color, intensity, distance, angle, penumbra, decay );
// angle: in radians (default: Math.PI / 3)
// penumbra: [0, 1] soft edge (default: 0)
// decay: 1 = physically-correct

light.position.set( 0, 10, 0 );
light.target.position.set( 0, 0, 0 );
light.castShadow = true;
light.shadow.mapSize.set( 1024, 1024 );
```

### RectAreaLight

Flat rectangular light panel. No shadows (uses analytical approximation).

```js
const light = new THREE.RectAreaLight( color, intensity, width, height );
light.position.set( 0, 5, -5 );
light.lookAt( 0, 0, 0 );
```

Requires `RectAreaLightUniformsLib.init()` before first use (addons).

### LightProbe

Captures lighting from an environment for use with non-physical materials.

```js
const probe = new THREE.LightProbe( shCoefficients );
// shCoefficients: Array of 9 Vector3 (Spherical Harmonics)

// Or create from scene:
const probe = new THREE.LightProbeGenerator( renderer, scene ).fromScene( position, size );
```

### IESSpotLight

Spot light with IES profile for realistic light distribution.

```js
import { IESSpotLight } from 'three/webgpu';
// Requires WebGPURenderer
```

### ProjectorLight

Cookie/stencil light that projects a texture pattern.

```js
import { ProjectorLight } from 'three/webgpu';
// Requires WebGPURenderer
```

## Shadows

### Enabling Shadows

```js
// 1. Enable on renderer
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// 2. Configure light
light.castShadow = true;
light.shadow.mapSize.set( 2048, 2048 );

// 3. Configure objects
mesh.castShadow = true;       // Object casts shadow
floor.receiveShadow = true;   // Object receives shadow
```

### Shadow Map Types

| Type | Quality | Speed | Notes |
|---|---|---|---|
| `BasicShadowMap` | Lowest | Fastest | Hard, unfiltered edges |
| `PCFShadowMap` | Medium | Fast | PCF filtering |
| `PCFSoftShadowMap` | High | Medium | Soft shadows, best for low-res maps |
| `VSMShadowMap` | High | Medium | Variance shadow mapping, all receivers also cast |

### Shadow Optimization

```js
// Limit shadow camera frustum
light.shadow.camera.left = -5;
light.shadow.camera.right = 5;
light.shadow.camera.top = 5;
light.shadow.camera.bottom = -5;
light.shadow.camera.near = 1;
light.shadow.camera.far = 50;

// Use lower resolution for distant lights
light.shadow.mapSize.set( 512, 512 );

// Bias tuning (reduce shadow acne / peter-panning)
light.shadow.bias = -0.0001;
light.shadow.normalBias = 0.02;

// Disable shadow updates when light is static
light.shadow.autoUpdate = false;
light.shadow.needsUpdate = true; // Manual update
```

### Shadow Helpers

```js
import { DirectionalLightHelper } from 'three';
const helper = new DirectionalLightHelper( light, 0.5 );
scene.add( helper );
helper.update(); // Call after changes
```

## Environment Maps

### Setting Environment

```js
// From scene (PMREM)
const pmremGenerator = new THREE.PMREMGenerator( renderer );
const envMap = pmremGenerator.fromScene( scene, 0, 1024, 0.1, 1000 ).texture;
scene.environment = envMap;
pmremGenerator.dispose();

// From HDR equirectangular
const rgbeLoader = new RGBELoader();
const envTexture = rgbeLoader.load( 'env.hdr' );
envTexture.mapping = THREE.EquirectangularReflectionMapping;
envTexture.colorSpace = THREE.SRGBColorSpace;

const pmremGenerator = new THREE.PMREMGenerator( renderer );
const envMap = pmremGenerator.fromEquirectangular( envTexture ).texture;
scene.environment = envMap;
pmremGenerator.dispose();

// Per-material override
material.envMap = envMap;
material.envMapIntensity = 1.0;
```

### Environment Helpers

```js
// Room environment (procedural, no external files)
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
const pmremGenerator = new THREE.PMREMGenerator( renderer );
const envMap = pmremGenerator.fromScene( new RoomEnvironment( renderer ) ).texture;
scene.environment = envMap;

// Color environment (simple gradient)
import { ColorEnvironment } from 'three/addons/environments/ColorEnvironment.js';
const envMap = new ColorEnvironment( renderer );
envMap.setBackground( color );
scene.environment = envMap.toTexture();
```

## Light Helpers (Debugging)

```js
new THREE.DirectionalLightHelper( light, size );
new THREE.PointLightHelper( light, sphereSize );
new THREE.SpotLightHelper( light );
new THREE.HemisphereLightHelper( light, sphereSize );
new THREE.RectAreaLightHelper( light );

// Update helpers each frame
helper.update();
```

## Lighting Gotchas

- **`DirectionalLight` needs a target** — set `light.target` or `light.target.position` to define where the light points. Default target is at origin.
- **`decay = 1` for physical accuracy** — PointLight and SpotLight use `decay = 1` (inverse square) by default in r138+. Legacy code may expect `decay = 2`.
- **Shadow camera frustum** — DirectionalLight shadow camera is an orthographic camera. Adjust `left/right/top/bottom` to cover the area of interest. Too large = blurry shadows.
- **`castShadow` / `receiveShadow`** — both must be set correctly. Mesh casts, ground receives.
- **Multiple shadow-casting lights** — each shadow-casting light adds a render pass. Limit to 2-4 for performance.
- **`RectAreaLight` has no shadows** — it uses an analytical approximation. Use SpotLight for shadowed area lighting.
- **`scene.environment` is shared** — all physical materials use it unless overridden by `material.envMap`.
- **Light intensity units** — physically-correct values: Sun ≈ 10-100, indoor ≈ 1-10, candle ≈ 0.1-1.
