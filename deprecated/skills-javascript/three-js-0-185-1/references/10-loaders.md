# Loaders

## Loader Architecture

```
Loader (abstract base)
├── FileLoader
│   ├── ImageLoader
│   │   ├── ImageBitmapLoader
│   │   ├── TextureLoader
│   │   │   ├── CubeTextureLoader
│   │   │   └── VideoTexture (special)
│   │   └── DataTextureLoader
│   ├── FileLoader → ObjectLoader (JSON)
│   └── FileLoader → BufferGeometryLoader
├── MaterialLoader
├── AnimationLoader
├── AudioLoader
└── CompressedTextureLoader
```

## LoadingManager

```js
const manager = new THREE.LoadingManager( onLoad, onProgress, onError );

manager.onLoad = () => { console.log('All loaded'); };
manager.onProgress = ( url, loaded, total ) => {
	console.log( `${loaded}/${total}: ${url}` );
};
manager.onError = ( url ) => { console.error( `Error loading: ${url}` ); };

// Pass to loaders
const textureLoader = new THREE.TextureLoader( manager );
const gltfLoader = new GLTFLoader( manager );

// Item cache
manager.itemCache; // Map of loaded items

// Signals
manager.signals.load.add( ( url ) => { /* ... */ } );
manager.signals.progress.add( ( url, loaded, total ) => { /* ... */ } );
manager.signals.error.add( ( url ) => { /* ... */ } );
```

## Cache

```js
THREE.Cache.enabled = true;
THREE.Cache.clear();
THREE.Cache.get( url );
THREE.Cache.remove( url );
THREE.Cache.addItem( url, item );
```

## GLTFLoader

Primary loader for 3D models. Supports glTF 2.0 (.gltf, .glb).

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const loader = new GLTFLoader();
loader.load(
	'model.glb',
	( gltf ) => {
		const model = gltf.scene;
		model.position.set( 0, 0, 0 );
		model.rotation.set( 0, 0, 0 );
		model.scale.set( 1, 1, 1 );
		model.traverse( ( child ) => {
			if ( child.isMesh ) {
				child.castShadow = true;
				child.receiveShadow = true;
			}
		} );
		scene.add( model );
	},
	( progress ) => {
		const percent = ( progress.loaded / progress.total ) * 100;
		console.log( `Loading: ${percent.toFixed(1)}%` );
	},
	( error ) => {
		console.error( 'Error loading model:', error );
	}
);
```

### GLTF Response

```js
gltf.scene;              // Root scene (Scene)
gltf.scenes;             // Array of scenes
gltf.cameras;            // Array of cameras
gltf.animations;         // Array of AnimationClip
gltf.asset;              // { generator, version, copyright }
gltf.parser;             // Internal parser (for extensions)
```

### GLTF with DRACO Compression

```js
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath( 'three/addons/libs/draco/' );
gltfLoader.setDRACOLoader( dracoLoader );
```

### GLTF with KTX2 Textures

```js
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';

const ktx2Loader = new KTX2Loader();
ktx2Loader.setTranscoderPath( 'three/addons/libs/ktx2/' );
ktx2Loader.detectSupport( renderer );
gltfLoader.setKTX2Loader( ktx2Loader );
```

### GLTF with Meshopt

```js
import { MeshoptDecoder } from 'three/addons/libs/meshopt/meshopt_decoder.module.js';
import { MeshoptLoader } from 'three/addons/loaders/MeshoptLoader.js';

const meshoptLoader = new MeshoptLoader();
meshoptLoader.setDecoderPath( 'three/addons/libs/meshopt/' );
meshoptLoader.setDecoderConfig( { decode: MeshoptDecoder.decode, decodeGpu: MeshoptDecoder.decodeGpu } );
gltfLoader.setMeshoptLoader( meshoptLoader );
```

## OBJLoader

Wavefront OBJ format. No materials (use MTLLoader separately).

```js
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';

const loader = new OBJLoader();
loader.load( 'model.obj', ( object ) => {
	scene.add( object );
} );
```

## MTLLoader

Loads .mtl material files (used with OBJ).

```js
import { MTLLoader } from 'three/addons/loaders/MTLLoader.js';

const mtlLoader = new MTLLoader();
mtlLoader.load( 'model.mtl', ( materials ) => {
	materials.preload();

	const objLoader = new OBJLoader();
	objLoader.setMaterials( materials );
	objLoader.load( 'model.obj', ( object ) => {
		scene.add( object );
	} );
} );
```

## Texture Loaders

```js
// Standard textures
const textureLoader = new THREE.TextureLoader();
const texture = textureLoader.load( 'texture.jpg' );

// Cube textures
const cubeLoader = new THREE.CubeTextureLoader();
const cubeTexture = cubeLoader.load( [ 'px.jpg', 'nx.jpg', 'py.jpg', 'ny.jpg', 'pz.jpg', 'nz.jpg' ] );

// HDR (.hdr / .rgbe)
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
const rgbeLoader = new RGBELoader();
const hdrTexture = rgbeLoader.load( 'environment.hdr' );
hdrTexture.mapping = THREE.EquirectangularReflectionMapping;
hdrTexture.colorSpace = THREE.SRGBColorSpace;

// HDR cube
import { HDRCubeTextureLoader } from 'three/addons/loaders/HDRCubeTextureLoader.js';
const hdrCubeLoader = new HDRCubeTextureLoader();
const hdrCube = hdrCubeLoader.load( [ 'px.hdr', 'nx.hdr', 'py.hdr', 'ny.hdr', 'pz.hdr', 'nz.hdr' ] );

// EXR
import { EXRLoader } from 'three/addons/loaders/EXRLoader.js';
const exrLoader = new EXRLoader();
const exrTexture = exrLoader.load( 'environment.exr' );

// DDS
import { DDSLoader } from 'three/addons/loaders/DDSLoader.js';
const ddsLoader = new DDSLoader();
const ddsTexture = ddsLoader.load( 'texture.dds' );

// KTX2
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
const ktx2Loader = new KTX2Loader();
ktx2Loader.setTranscoderPath( 'three/addons/libs/ktx2/' );
ktx2Loader.detectSupport( renderer );
const ktx2Texture = ktx2Loader.load( 'texture.ktx2' );

// PVR
import { PVRLoader } from 'three/addons/loaders/PVRLoader.js';
const pvrLoader = new PVRLoader();
const pvrTexture = pvrLoader.load( 'texture.pvr' );
```

## FontLoader

```js
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';

const fontLoader = new FontLoader();
fontLoader.load( 'fonts/helvetiker_regular.typeface.json', ( font ) => {
	const geometry = new TextGeometry( 'Hello', {
		font: font,
		size: 0.8,
		depth: 0.2,        // Previously: height
		curveSegments: 12,
		bevelEnabled: true,
		bevelThickness: 0.02,
		bevelSize: 0.01,
		bevelOffset: 0,
		bevelSegments: 5,
	} );
	geometry.computeBoundingBox();
	const mesh = new THREE.Mesh( geometry, material );
	scene.add( mesh );
} );
```

## Other Loaders

```js
// STL
import { STLLoader } from 'three/addons/loaders/STLLoader.js';

// PLY
import { PLYLoader } from 'three/addons/loaders/PLYLoader.js';

// 3D Model
import { ThreeDMLoader } from 'three/addons/loaders/3DMLoader.js';

// 3MF
import { ThreeMFLoader } from 'three/addons/loaders/3MFLoader.js';

// AMF
import { AMFLoader } from 'three/addons/loaders/AMFLoader.js';

// Collada
import { ColladaLoader } from 'three/addons/loaders/ColladaLoader.js';

// FBX
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';

// LDraw
import { LDrawILoader } from 'three/addons/loaders/LDrawLoader.js';

// SVG
import { SVGLoader } from 'three/addons/loaders/SVGLoader.js';

// Lottie
import { LottieLoader } from 'three/addons/loaders/LottieLoader.js';

// IES (light profiles)
import { IESLoader } from 'three/addons/loaders/IESLoader.js';

// LUT (color grading)
import { LUTCubeLoader } from 'three/addons/loaders/LUTCubeLoader.js';
import { LUT3dlLoader } from 'three/addons/loaders/LUT3dlLoader.js';
import { LUTImageLoader } from 'three/addons/loaders/LUTImageLoader.js';

// Point cloud
import { PCDLoader } from 'three/addons/loaders/PCDLoader.js';

// BVH
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
```

## Loader Gotchas

- **GLTFLoader is async** — always use callbacks or await. The model is not available synchronously.
- **DRACO decoder path** — must point to the correct directory: `'three/addons/libs/draco/'`. Include decoder drivers for your target platforms.
- **KTX2 transcoder path** — must be set before loading: `ktx2Loader.setTranscoderPath( 'three/addons/libs/ktx2/' )`.
- **GLTF animations** — access via `gltf.animations`. Use `AnimationMixer` to play.
- **GLTF materials** — glTF uses PBR (metallic-roughness). Materials are `MeshStandardMaterial`.
- **OBJ has no materials** — use `MTLLoader` + `objLoader.setMaterials()` for material support.
- **Texture auto-disposal** — loaders manage their own caches. Use `LoadingManager` for tracking.
- **Cross-origin textures** — set `textureLoader.crossOrigin = 'anonymous'` for CORS-enabled servers.
- **FBXLoader requires dependencies** — needs the FBX runtime library loaded separately.
