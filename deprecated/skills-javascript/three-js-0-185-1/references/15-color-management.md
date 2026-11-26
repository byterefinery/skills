# Color Management

## Color Spaces

Three.js r185 uses a color management system that handles conversions between color spaces.

### Available Color Spaces

```js
// Constants
THREE.NoColorSpace          // '' — no color space (raw data)
THREE.SRGBColorSpace         // 'srgb' — standard RGB (display)
THREE.LinearSRGBColorSpace   // 'srgb-linear' — linear sRGB (rendering)

// Transfer functions
THREE.LinearTransfer         // 'linear'
THREE.SRGBTransfer           // 'srgb'
```

### Default Working Space

```js
// Default: linear sRGB for internal rendering
THREE.ColorManagement.workingColorSpace = THREE.LinearSRGBColorSpace;

// Enable/disable automatic color management
THREE.ColorManagement.enabled = true; // Default: true
```

## ColorManagement API

```js
// Convert color between spaces
THREE.ColorManagement.convert( color, sourceColorSpace, targetColorSpace );

// Convert from working space to target
THREE.ColorManagement.workingToColorSpace( color, targetColorSpace );

// Convert from source to working space
THREE.ColorManagement.colorSpaceToWorking( color, sourceColorSpace );

// Register custom color space
THREE.ColorManagement.spaces[ name ] = {
	primaries: [ rx, ry, gx, gy, bx, by ],
	whitePoint: [ x, y ],
	transfer: THREE.SRGBTransfer,
	toXYZ: new THREE.Matrix3(),
	fromXYZ: new THREE.Matrix3(),
	luminanceCoefficients: [ r, g, b ],
};
```

## Texture Color Spaces

### Color Textures

```js
// TextureLoader auto-detects sRGB for image files
const texture = textureLoader.load( 'texture.jpg' );
// texture.colorSpace === 'srgb' (auto-detected)

// Explicitly set for data textures
const dataTexture = new THREE.DataTexture( data, width, height );
dataTexture.colorSpace = THREE.SRGBColorSpace;

// For HDR textures
const hdrTexture = rgbeLoader.load( 'env.hdr' );
hdrTexture.colorSpace = THREE.SRGBColorSpace;
```

### Non-Color Textures

```js
// Normal maps, AO maps, roughness maps, displacement maps
// MUST use NoColorSpace (default)

const normalMap = textureLoader.load( 'normal.png' );
normalMap.colorSpace = THREE.NoColorSpace; // Explicit, though usually default

const aoMap = textureLoader.load( 'ao.png' );
aoMap.colorSpace = THREE.NoColorSpace;

const roughnessMap = textureLoader.load( 'roughness.png' );
roughnessMap.colorSpace = THREE.NoColorSpace;
```

## Renderer Output

### Setting Output Color Space

```js
// REQUIRED for correct color output
renderer.outputColorSpace = THREE.SRGBColorSpace;

// Without this, colors appear washed out (linear space displayed as sRGB)
```

### Tone Mapping

```js
// Available tone mappings
renderer.toneMapping = THREE.NoToneMapping;
renderer.toneMapping = THREE.LinearToneMapping;
renderer.toneMapping = THREE.ReinhardToneMapping;
renderer.toneMapping = THREE.CineonToneMapping;
renderer.toneMapping = THREE.ACESFilmicToneMapping;  // Popular choice
renderer.toneMapping = THREE.CustomToneMapping;
renderer.toneMapping = THREE.AgXToneMapping;
renderer.toneMapping = THREE.NeutralToneMapping;

// Exposure control
renderer.toneMappingExposure = 1.0;
```

### Tone Mapping Characteristics

| Tone Mapping | Best For | Notes |
|---|---|---|
| `NoToneMapping` | UI, non-physical | No HDR handling |
| `LinearToneMapping` | Simple scenes | Direct linear output |
| `ReinhardToneMapping` | General purpose | Soft rolloff |
| `CineonToneMapping` | Cinematic look | Film-like response |
| `ACESFilmicToneMapping` | HDR, realistic | Industry standard, needs exposure tuning |
| `AgXToneMapping` | Balanced | Good default for HDR |
| `NeutralToneMapping` | E-commerce, product | Khronos 3D Commerce standard |

## Material Color Handling

### MeshStandardMaterial

```js
const material = new THREE.MeshStandardMaterial( {
	color: new THREE.Color( 0xffffff ), // Interpreted as sRGB
	map: colorTexture,                  // sRGB (auto-detected)
	roughnessMap: roughnessTexture,     // NoColorSpace
	metalnessMap: metalnessTexture,     // NoColorSpace
	normalMap: normalTexture,           // NoColorSpace
	emissive: new THREE.Color( 0x000000 ), // Linear space
	emissiveMap: emissiveTexture,       // sRGB if color data
} );
```

### ShaderMaterial

```js
// In fragment shaders, colors are in linear space
// Apply tone mapping manually if needed

fragmentShader: `
	uniform sampler2D map;
	varying vec2 vUv;

	#include <tonemapping_fragment>  // Apply renderer's tone mapping
	#include <colorspace_fragment>    // Apply output color space

	void main() {
		vec4 texColor = texture2D( map, vUv );
		gl_FragColor = texColor;
	}
`
```

## Post-Processing Color

### EffectComposer

```js
// OutputPass applies tone mapping + color space conversion
const outputPass = new OutputPass();
composer.addPass( outputPass );

// Without OutputPass, post-processing output is in linear space
```

### Custom Color Correction

```js
import { ColorCorrectionShader } from 'three/addons/shaders/ColorCorrectionShader.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';

const colorCorrection = new ShaderPass( ColorCorrectionShader );
colorCorrection.uniforms[ 'colorDelta' ].value = new THREE.Vector3( 0, 0, 0 );
colorCorrection.uniforms[ 'contrast' ].value = 1.0;
colorCorrection.uniforms[ 'saturation' ].value = 1.0;
composer.addPass( colorCorrection );
```

### LUT (Look-Up Table)

```js
import { LUTPass } from 'three/addons/postprocessing/LUTPass.js';
import { LUTCubeLoader } from 'three/addons/loaders/LUTCubeLoader.js';

const lutLoader = new LUTCubeLoader();
lutLoader.load( 'lookups/Filmic.cube', ( lut ) => {
	const lutPass = new LUTPass( lut );
	composer.addPass( lutPass );
} );
```

## Color Gotchas

- **`renderer.outputColorSpace = SRGBColorSpace` is mandatory** — without it, all output is in linear space and looks washed out.
- **`OutputPass` for post-processing** — replaces the need for `outputColorSpace` when using EffectComposer.
- **Texture colorSpace auto-detection** — `TextureLoader` sets `srgb` for jpg/png/webp. Data textures and non-image sources default to `NoColorSpace`.
- **Normal/AO/roughness maps** — must be `NoColorSpace`. Setting `SRGBColorSpace` corrupts the data.
- **`emissive` is linear** — emissive color values are in linear space, not sRGB.
- **ACES needs exposure tuning** — `ACESFilmicToneMapping` often needs `toneMappingExposure` between 0.5 and 2.0 depending on scene lighting.
- **`ColorManagement.enabled`** — disable only if you handle color conversion manually. Leaving it enabled is recommended.
- **Linear working space** — all internal rendering happens in `LinearSRGBColorSpace`. sRGB textures are converted on load, output is converted on display.
- **`convertSRGBToLinear()` / `convertLinearToSRGB()`** — manual conversion methods on `Color` objects.
