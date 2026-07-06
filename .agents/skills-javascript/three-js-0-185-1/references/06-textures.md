# Textures

## Texture Types

```js
// Image-based
new THREE.Texture( image, mapping, wrapS, wrapT, magFilter, minFilter, format, type, anisotropy, colorSpace );
new THREE.CanvasTexture( canvas );
new THREE.DataTexture( data, width, height, format, type );
new THREE.Data3DTexture( data, width, height, depth, format, type );
new THREE.DataArrayTexture( data, width, height, depth, format, type );
new THREE.CubeTexture( urls, cubemapLoader, onLoad );
new THREE.VideoTexture( videoElement );
new THREE.VideoFrameTexture( videoFrame );
new THREE.HTMLTexture( element );
new THREE.ExternalTexture( name, width, height ); // WebXR

// Compressed
new THREE.CompressedTexture( image, mapping, wrapS, wrapT, magFilter, minFilter, format, type, anisotropy, colorSpace );
new THREE.CompressedCubeTexture( faces, format, type );
new THREE.CompressedArrayTexture( images, width, height, depth, format, type );

// Depth
new THREE.DepthTexture( geometry );

// Framebuffer
new THREE.FramebufferTexture( width, height, format, type );
```

## Texture Properties

```js
texture.wrapS = THREE.ClampToEdgeWrapping;  // RepeatWrapping, MirroredRepeatWrapping
texture.wrapT = THREE.ClampToEdgeWrapping;
texture.magFilter = THREE.LinearFilter;      // NearestFilter
texture.minFilter = THREE.LinearMipmapLinearFilter; // NearestMipmapNearestFilter, NearestMipmapLinearFilter, LinearMipmapNearestFilter
texture.anisotropy = 1;                       // Up to renderer.capabilities.maxAnisotropy
texture.format = THREE.RGBAFormat;
texture.type = THREE.UnsignedByteType;
texture.colorSpace = THREE.NoColorSpace;     // SRGBColorSpace for color textures
texture.offset.set( 0, 0 );                  // UV offset
texture.repeat.set( 1, 1 );                  // UV repeat (negative for flip)
texture.center.set( 0, 0 );                  // UV center for repeat/rotation
texture.rotation = 0;                        // UV rotation (radians)
texture.premultiplyAlpha = false;
texture.flipY = true;                        // Flip Y axis (default for uploaded images)
texture.generateMipmaps = true;
texture.mipmapBias = 0;
texture.maxAnisotropy = 1;
texture.mapping = THREE.UVMapping;           // CubeReflectionMapping, CubeRefractionMapping,
                                             // EquirectangularReflectionMapping, EquirectangularRefractionMapping, CubeUVReflectionMapping

// Update
texture.needsUpdate = true;
texture.onUpdate = ( texture ) => { /* ... */ };

// Dispose
texture.dispose();
```

## Texture Formats

```js
// Color formats
THREE.RGBAFormat
THREE.RGBFormat
THREE.RedFormat
THREE.RGFormat
THREE.RedIntegerFormat
THREE.RGIntegerFormat
THREE.RGBIntegerFormat
THREE.RGBAIntegerFormat

// Alpha-only
THREE.AlphaFormat

// Depth
THREE.DepthFormat
THREE.DepthStencilFormat

// Compressed formats
THREE.RGBA_ASTC_4x4_Format   // Through RGBA_ASTC_12x12_Format
THREE.RGBA_BPTC_Format
THREE.RGB_BPTC_SIGNED_Format
THREE.RGB_BPTC_UNSIGNED_Format
THREE.RGB_ETC2_Format
THREE.RGBA_ETC2_EAC_Format
THREE.RGB_S3TC_DXT1_Format   // Through RGBA_S3TC_DXT5_Format
THREE.RGB_PVRTC_4BPPV1_Format // Through RGBA_PVRTC_2BPPV1_Format
// ... and many more
```

## Texture Types

```js
THREE.UnsignedByteType          // 8-bit per channel (default)
THREE.ByteType
THREE.ShorType
THREE.UnsignedShortType
THREE.IntType
THREE.UnsignedIntType
THREE.FloatType                 // 32-bit float (for HDR)
THREE.HalfFloatType             // 16-bit float (good balance of quality/memory)
THREE.UnsignedShort4444Type
THREE.UnsignedShort5551Type
THREE.UnsignedInt248Type        // Depth + stencil
THREE.UnsignedInt5999Type
THREE.UnsignedInt101111Type
```

## Filters

```js
// Magnification (no mipmaps)
THREE.NearestFilter
THREE.LinearFilter

// Minification (with mipmaps)
THREE.NearestMipmapNearestFilter
THREE.NearestMipmapLinearFilter
THREE.LinearMipmapNearestFilter
THREE.LinearMipmapLinearFilter  // Default, best quality
```

## TextureLoader

```js
const loader = new THREE.TextureLoader();
const texture = loader.load( 'texture.jpg', onLoad, onProgress, onError );

// Auto-detects sRGB for common image formats (jpg, png, bmp, gif, webp)
// Set explicitly for non-standard sources:
texture.colorSpace = THREE.SRGBColorSpace;

// For non-color textures (normal maps, AO maps, etc.):
const normalMap = loader.load( 'normal.png' );
normalMap.colorSpace = THREE.NoColorSpace; // Usually already default
```

## DataTexture

```js
const width = 256, height = 256;
const data = new Uint8Array( width * height * 4 );

// Fill data (RGBA)
for ( let i = 0; i < width * height; i ++ ) {
	data[ i * 4 + 0 ] = 255; // R
	data[ i * 4 + 1 ] = 0;   // G
	data[ i * 4 + 2 ] = 0;   // B
	data[ i * 4 + 3 ] = 255; // A
}

const texture = new THREE.DataTexture( data, width, height, THREE.RGBAFormat );
texture.needsUpdate = true;
texture.colorSpace = THREE.SRGBColorSpace;
```

## CubeTexture

```js
const loader = new THREE.CubeTextureLoader();
const texture = loader.load( [
	'px.jpg', 'nx.jpg',
	'py.jpg', 'ny.jpg',
	'pz.jpg', 'nz.jpg',
] );
texture.mapping = THREE.CubeReflectionMapping;
```

## PMREMGenerator

Generates prefiltered environment maps for PBR rendering.

```js
const pmremGenerator = new THREE.PMREMGenerator( renderer );
pmremGenerator.compileEquirectangularShader();

// From scene
const envMap = pmremGenerator.fromScene( scene, exposure, defaultSize, nearVal, farVal ).texture;

// From cube texture
const envMap = pmremGenerator.fromCubemap( cubeTexture, colorSpace ).texture;

// From equirectangular
const envMap = pmremGenerator.fromEquirectangular( equirectangularTexture ).texture;

// Apply
scene.environment = envMap;

// Dispose
pmremGenerator.dispose();
envMap.dispose();
```

## Compressed Textures

Load compressed textures with appropriate loaders:

```js
// KTX2 (recommended — best compression)
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { TranscoderLoader } from 'three/addons/libs/ktx2/TranscoderLoader.js';

const ktx2Loader = new KTX2Loader();
ktx2Loader.setTranscoderPath( 'three/addons/libs/ktx2/' );
ktx2Loader.detectSupport( renderer );
const texture = ktx2Loader.load( 'texture.ktx2', onLoad, onProgress, onError );

// DDS
import { DDSLoader } from 'three/addons/loaders/DDSLoader.js';
const ddsLoader = new DDSLoader();
const texture = ddsLoader.load( 'texture.dds' );

// HDR (.hdr / .rgbe)
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
const rgbeLoader = new RGBELoader();
const texture = rgbeLoader.load( 'environment.hdr' );
texture.mapping = THREE.EquirectangularReflectionMapping;
texture.colorSpace = THREE.SRGBColorSpace;

// EXR
import { EXRLoader } from 'three/addons/loaders/EXRLoader.js';
const exrLoader = new EXRLoader();
const texture = exrLoader.load( 'environment.exr' );
```

## Texture Gotchas

- **`needsUpdate = true`** — must be set after creating/modifying `DataTexture` or `CanvasTexture` data.
- **`flipY` is true by default** — matches WebGL coordinate system. Set `false` when using canvas textures or data that is already in the correct orientation.
- **Power-of-two textures** — required for mipmaps and `RepeatWrapping` / `MirroredRepeatWrapping`. Non-power-of-two textures are limited to `ClampToEdgeWrapping` and no mipmaps.
- **`colorSpace` for normal/AO/roughness maps** — always `NoColorSpace`. Setting `SRGBColorSpace` corrupts the data.
- **`PMREMGenerator` memory** — creates internal render targets. Always `dispose()` when done.
- **CubeTexture face order** — `+X, -X, +Y, -Y, +Z, -Z`. Wrong order produces scrambled reflections.
- **`generateMipmaps`** — disabled for `DataTexture` by default. Enable manually: `texture.generateMipmaps = true; texture.needsUpdate = true;`.
