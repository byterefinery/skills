# Materials

## Material Hierarchy

```
Material (abstract base)
├── LineBasicMaterial
├── LineDashedMaterial
├── PointsMaterial
├── SpriteMaterial
├── ShadowMaterial
├── RawShaderMaterial
├── ShaderMaterial
├── MeshBasicMaterial
├── MeshDepthMaterial
├── MeshDistanceMaterial
├── MeshNormalMaterial
├── MeshMatcapMaterial
├── MeshLambertMaterial
├── MeshPhongMaterial
│   └── MeshStandardMaterial
│       └── MeshPhysicalMaterial
├── MeshToonMaterial
```

## Base Material Properties

All materials share these properties from `Material`:

```js
const material = new THREE.MeshStandardMaterial( {
	// Rendering
	blending: THREE.NormalBlending,   // NoBlending, AdditiveBlending, SubtractiveBlending,
	                                 // MultiplyBlending, CustomBlending, MaterialBlending
	side: THREE.FrontSide,            // BackSide, DoubleSide
	depthTest: true,
	depthWrite: true,
	depthFunc: THREE.LessEqualDepth,  // Never, Less, Equal, LessEqual, GreaterEqual, Greater, NotEqual, Always
	stencilWrite: false,
	stencilWriteMask: 0xFF,
	stencilFunc: THREE.AlwaysStencilFunc,
	stencilRef: 0,
	stencilFuncMask: 0xFF,
	stencilFail: THREE.KeepStencilOp,
	stencilZFail: THREE.KeepStencilOp,
	stencilZPass: THREE.KeepStencilOp,

	// Transparency
	transparent: false,
	opacity: 1.0,
	alphaTest: 0.0,          // Discard fragments below this alpha
	alphaToCoverage: false,  // MSAA-friendly transparency (requires antialias)

	// Appearance
	color: new THREE.Color( 0xffffff ),
	vertexColors: false,
	fog: true,               // Affected by scene fog

	// Wireframe
	wireframe: false,
	wireframeLinewidth: 1,
	wireframeLinecap: 'round',
	wireframeLinejoin: 'round',

	// Face culling
	polygonOffset: false,
	polygonOffsetFactor: 0,
	polygonOffsetUnits: 0,

	// Clipping
	clippingPlanes: null,    // Array of Plane
	clipShadows: true,
	clipIntersection: false,

	// Custom blending (requires blending: CustomBlending)
	blendSrc: THREE.SrcAlphaFactor,
	blendDst: THREE.OneMinusSrcAlphaFactor,
	blendEquation: THREE.AddEquation,
	blendSrcRGB: THREE.SrcAlphaFactor,
	blendDstRGB: THREE.OneMinusSrcAlphaFactor,
	blendEquationRGB: THREE.AddEquation,
	blendSrcAlpha: THREE.OneFactor,
	blendDstAlpha: THREE.ZeroFactor,
	blendEquationAlpha: THREE.AddEquation,

	// Tone mapping
	toneMapped: true,        // Apply renderer's tone mapping

	// Prepass
	premultipliedAlpha: false,
} );
```

## MeshStandardMaterial

Physically-based material following the metallic-roughness workflow.

```js
const material = new THREE.MeshStandardMaterial( {
	color: new THREE.Color( 0xffffff ),      // Base color (albedo)
	roughness: 1.0,                          // [0, 1] surface roughness
	metalness: 0.0,                          // [0, 1] metallic factor
	roughnessMap: null,                      // GR texture (R=roughness, G=metalness)
	metalnessMap: null,                      // R texture
	map: null,                               // Color/diffuse texture
	envMap: null,                            // Environment map
	envMapIntensity: 1.0,                    // Scale env map contribution
	normalMap: null,                         // Normal map texture
	normalMapType: THREE.TangentSpaceNormalMap, // ObjectSpaceNormalMap
	normalScale: new THREE.Vector2( 1, 1 ), // Normal map intensity
	displacementMap: null,                   // Grayscale displacement
	displacementScale: 1.0,
	displacementBias: 0.0,
	aoMap: null,                             // Ambient occlusion
	aoMapIntensity: 1.0,
	emissive: new THREE.Color( 0x000000 ),   // Emissive color
	emissiveIntensity: 1.0,
	emissiveMap: null,                       // Emissive mask
	alphaMap: null,                          // Alpha mask
	iridescence: false,
	iridescenceIOR: 1.3,
	iridescenceThicknessRange: [ 100, 400 ],
	iridescenceThicknessMap: null,
	iridescenceSlope: 0.7,
	sheen: false,
	sheenRoughness: 0.5,
	sheenColor: new THREE.Color( 0x000000 ),
	sheenRoughnessMap: null,
	sheenColorMap: null,
	transmission: 0.0,                       // Glass-like transparency [0, 1]
	transmissionMap: null,
	attenuationColor: new THREE.Color( 0xffffff ),
	attenuationDistance: 0.0,
	specularColor: new THREE.Color( 0xffffff ),
	specularIntensity: 1.0,
	specularColorMap: null,
	specularIntensityMap: null,
} );
```

## MeshPhysicalMaterial

Extended PBR material with advanced features. Inherits from `MeshStandardMaterial`.

```js
const material = new THREE.MeshPhysicalMaterial( {
	// From MeshStandardMaterial
	color: new THREE.Color( 0xffffff ),
	roughness: 0.5,
	metalness: 0.0,

	// Clearcoat (paint-like top layer)
	clearcoat: 0.0,               // [0, 1] clearcoat layer intensity
	clearcoatRoughness: 0.0,      // [0, 1] clearcoat roughness
	clearcoatMap: null,           // R channel = clearcoat
	clearcoatRoughnessMap: null,  // G channel = clearcoat roughness
	clearcoatNormalMap: null,
	clearcoatNormalScale: new THREE.Vector2( 1, 1 ),

	// Anisotropy (brushed metal)
	anisotropy: 0.0,              // [0, 1] anisotropy intensity
	anisotropyRotation: 0.0,      // Rotation in radians
	anisotropyMap: null,          // RG = direction, B = strength

	// Iridescence (rainbow effect)
	iridescence: 0.0,             // [0, 1]
	iridescenceIOR: 1.3,          // [1, 2.333]
	iridescenceThicknessRange: [ 100, 400 ], // [nm]
	iridescenceThicknessMap: null,

	// Sheen (fabric/cloth)
	sheen: 0.0,                   // [0, 1]
	sheenRoughness: 0.5,
	sheenColor: new THREE.Color( 0x000000 ),
	sheenRoughnessMap: null,
	sheenColorMap: null,

	// Transmission (glass)
	transmission: 0.0,            // [0, 1]
	transmissionMap: null,        // R channel
	attenuationColor: new THREE.Color( 0xffffff ),
	attenuationDistance: 0.0,     // Infinity = no attenuation

	// Specular
	specularColor: new THREE.Color( 0xffffff ),
	specularIntensity: 1.0,
	specularColorMap: null,
	specularIntensityMap: null,

	// Reflectivity (non-metallic)
	reflectivity: 0.5,            // [0, 1] — legacy, use specularColor/intensity
} );
```

**Performance note:** Each enabled feature adds per-pixel cost. Start with `MeshStandardMaterial` and only upgrade to `MeshPhysicalMaterial` when you need clearcoat, transmission, sheen, or anisotropy.

## MeshBasicMaterial

Unlit material — ignores lights and environment maps.

```js
const material = new THREE.MeshBasicMaterial( {
	color: new THREE.Color( 0xffffff ),
	map: null,
	alphaMap: null,
	wireframe: false,
} );
```

## MeshNormalMaterial

Displays vertex normals as colors. Useful for debugging geometry.

```js
const material = new THREE.MeshNormalMaterial( {
	flatShading: false,
	wireframe: false,
} );
```

## MeshMatcapMaterial

Uses a "material capture" texture for appearance. No lighting required.

```js
const material = new THREE.MeshMatcapMaterial( {
	matcap: texture,  // Matcap texture (must be power-of-two)
	color: new THREE.Color( 0xffffff ),
} );
```

## ShaderMaterial

Custom GLSL shaders.

```js
const material = new THREE.THREE.ShaderMaterial( {
	uniforms: {
		time: { value: 0.0 },
		texture: { value: null },
		resolution: { value: new THREE.Vector2( window.innerWidth, window.innerHeight ) },
	},
	vertexShader: `
		varying vec2 vUv;
		void main() {
			vUv = uv;
			gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
		}
	`,
	fragmentShader: `
		uniform float time;
		uniform sampler2D texture;
		varying vec2 vUv;
		void main() {
			vec4 color = texture2D( texture, vUv );
			gl_FragColor = color;
		}
	`,

	// Optional: inherit Material properties
	side: THREE.DoubleSide,
	transparent: true,
	depthWrite: false,
} );
```

**Update uniforms in render loop:**
```js
material.uniforms.time.value = clock.getElapsedTime();
```

## RawShaderMaterial

Like `ShaderMaterial` but without default attributes (no `uv`, `position`, etc. injected automatically). Full control over vertex attributes.

## PointsMaterial

For particle systems using `Points` objects.

```js
const material = new THREE.PointsMaterial( {
	color: new THREE.Color( 0xffffff ),
	size: 1.0,
	sizeAttenuation: true,       // Perspective size attenuation
	map: null,                   // Particle texture
	alphaMap: null,
	transparent: false,
	depthWrite: true,
} );
```

## LineBasicMaterial / LineDashedMaterial

```js
const lineMaterial = new THREE.LineBasicMaterial( {
	color: new THREE.Color( 0xffffff ),
	linewidth: 1,               // Note: most browsers ignore this and use 1
	linecap: 'round',
	linejoin: 'round',
} );

const dashedMaterial = new THREE.LineDashedMaterial( {
	color: new THREE.Color( 0xffffff ),
	dashSize: 3,
	gapSize: 1,
	linewidth: 1,
} );
// Call geometry.computeLineDistances() before rendering dashed lines
```

## SpriteMaterial

For billboarding sprites (always face camera).

```js
const material = new THREE.SpriteMaterial( {
	map: texture,
	color: new THREE.Color( 0xffffff ),
	transparent: true,
} );
```

## Material Gotchas

- **Non-color textures must use `NoColorSpace`** — normal maps, roughness maps, AO maps, displacement maps. Setting `colorSpace: SRGBColorSpace` on these produces incorrect results.
- **`alphaToCoverage` requires MSAA** — set `antialias: true` on the renderer. More efficient than `alphaTest` for soft edges.
- **`wireframeLinewidth` is ignored** — most WebGL implementations force linewidth to 1 regardless of setting.
- **Multiple materials on one mesh** — use `Mesh` with a single material. For multiple materials, use `BufferGeometry.groups` and an array of materials.
- **Material cloning** — `material.clone()` creates a shallow copy of uniforms. Texture references are shared.
