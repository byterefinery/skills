# Controls and Addons

## Controls

### OrbitControls

Camera orbits around a target point.

```js
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const controls = new OrbitControls( camera, domElement );

// Settings
controls.enableDamping = true;       // Inertia (requires controls.update())
controls.dampingFactor = 0.05;       // [0, 1] damping strength
controls.autoRotate = false;         // Auto orbit
controls.autoRotateSpeed = 2.0;      // Degrees per second
controls.enableZoom = true;
controls.enablePan = true;
controls.enableRotate = true;
controls.enableKeys = true;          // Arrow key control

// Limits
controls.minDistance = 0;            // Dolly zoom
controls.maxDistance = Infinity;
controls.minZoom = 0;                // Orthographic zoom
controls.maxZoom = Infinity;
controls.minPolarAngle = 0;          // Vertical angle (radians)
controls.maxPolarAngle = Math.PI;
controls.minAzimuthAngle = -Infinity; // Horizontal angle (radians)
controls.maxAzimuthAngle = Infinity;
controls.minTargetx = -Infinity;     // Pan limits
controls.maxTargetx = Infinity;
controls.minTargety = -Infinity;
controls.maxTargety = Infinity;
controls.minTargetz = -Infinity;
controls.maxTargetz = Infinity;

// Speed
controls.rotateSpeed = 1.0;
controls.zoomSpeed = 1.0;
controls.panSpeed = 1.0;

// Keys
controls.keys = { LEFT: 'ArrowLeft', UP: 'ArrowUp', RIGHT: 'ArrowRight', BOTTOM: 'ArrowDown' };

// Mouse buttons
controls.mouseButtons = {
	LEFT: THREE.ROTATE,
	MIDDLE: THREE.DOLLY,
	RIGHT: THREE.PAN,
};

// Touch
controls.touches = {
	ONE: THREE.ROTATE,
	TWO: THREE.DOLLY_PAN,
};

// Target
controls.target.set( 0, 0, 0 );
controls.target0; // Initial target
controls.position0; // Initial position
controls.zoom0; // Initial zoom

// Methods
controls.update();                  // Required when damping or autoRotate
controls.dispose();                 // Remove event listeners
controls.saveState();               // Save current state
controls.reset();                   // Reset to saved state
controls.getObject();               // Returns camera
controls.getTarget( target );       // Get target vector
controls.update();

// Events
controls.addEventListener( 'change', () => { /* render */ } );
controls.addEventListener( 'start', () => { /* interaction started */ } );
controls.addEventListener( 'end', () => { /* interaction ended */ } );
```

### TransformControls

Gizmo for transforming objects in the scene.

```js
import { TransformControls } from 'three/addons/controls/TransformControls.js';

const controls = new TransformControls( camera, domElement );
controls.attach( object );
scene.add( controls );

controls.setMode( 'translate' );   // 'translate', 'rotate', 'scale'
controls.setSize( 0.5 );
controls.setSpace( 'world' );      // 'world' or 'local'
controls.showX = true;
controls.showY = true;
controls.showZ = true;

// Snap
controls.setTranslationSnap( 0.1 );
controls.setRotationSnap( THREE.MathUtils DEG2RAD * 15 );
controls.setScaleSnap( 0.1 );

// Lock axes
controls.lockX = false;
controls.lockY = false;
controls.lockZ = false;

// Events
controls.addEventListener( 'change', () => { /* render */ } );
controls.addEventListener( 'mouseUp', () => { /* transform ended */ } );
controls.detach(); // Remove from object
controls.dispose();
```

**Note:** Combine with OrbitControls — OrbitControls should listen to `mouseDown` from TransformControls to prevent conflicts.

### Other Controls

```js
// Arcball — free rotation like a 3D ball
import { ArcballControls } from 'three/addons/controls/ArcballControls.js';

// First-person — WASD movement
import { FirstPersonControls } from 'three/addons/controls/FirstPersonControls.js';

// Fly — free flight with smooth controls
import { FlyControls } from 'three/addons/controls/FlyControls.js';

// Map — 2D map navigation
import { MapControls } from 'three/addons/controls/MapControls.js';

// Pointer lock — FPS-style mouse capture
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';

// Trackball — trackball-style rotation
import { TrackballControls } from 'three/addons/controls/TrackballControls.js';

// Drag — drag objects in screen space
import { DragControls } from 'three/addons/controls/DragControls.js';
```

## Environments

```js
// Room environment (procedural studio lighting)
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
const pmremGenerator = new THREE.PMREMGenerator( renderer );
const envMap = pmremGenerator.fromScene( new RoomEnvironment( renderer ) ).texture;
scene.environment = envMap;
pmremGenerator.dispose();

// Color environment (simple gradient)
import { ColorEnvironment } from 'three/addons/environments/ColorEnvironment.js';
const env = new ColorEnvironment( renderer );
env.setBackground( new THREE.Color( 0x87ceeb ) );
scene.background = env.getBackgroundTexture();
scene.environment = env.getEnvironmentTexture();

// Debug environment
import { DebugEnvironment } from 'three/addons/environments/DebugEnvironment.js';
const debugEnv = new DebugEnvironment( renderer );
scene.environment = debugEnv;
```

## Physics

```js
// Rapier (recommended — WASM-based, fast)
import { RapierPhysics } from 'three/addons/physics/RapierPhysics.js';
import * as RAPIER from 'rapier3ds'; // or 'rapier3d'

await RAPIER.init();
const physics = new RapierPhysics( scene );
await physics.init( RAPIER );

const rigidBody = physics.createRigidBody( mesh, { type: 'dynamic' } );
physics.addRigidBody( rigidBody );

// Update
physics.update( delta );

// Jolt Physics
import { JoltPhysics } from 'three/addons/physics/JoltPhysics.js';

// Ammo.js (legacy)
import { AmmoPhysics } from 'three/addons/physics/AmmoPhysics.js';
```

## Modifiers

```js
// Curve modifier (displace along curve)
import { CurveModifier } from 'three/addons/modifiers/CurveModifier.js';

// Edge split
import { EdgeSplitModifier } from 'three/addons/modifiers/EdgeSplitModifier.js';

// Simplify (reduce vertex count)
import { SimplifyModifier } from 'three/addons/modifiers/SimplifyModifier.js';

// Tessellate (subdivide)
import { TessellateModifier } from 'three/addons/modifiers/TessellateModifier.js';
```

## Helpers

```js
// Grid
const gridHelper = new THREE.GridHelper( size, divisions, centerColor, optionalColor );
scene.add( gridHelper );

// Axes
const axesHelper = new THREE.AxesHelper( size );
scene.add( axesHelper );

// Directional light
const lightHelper = new THREE.DirectionalLightHelper( light, size, color );
scene.add( lightHelper );
lightHelper.update();

// Point light
const pointHelper = new THREE.PointLightHelper( light, sphereSize, color );
scene.add( pointHelper );

// Spot light
const spotHelper = new THREE.SpotLightHelper( light );
scene.add( spotHelper );

// Skeleton
const skeletonHelper = new THREE.SkeletonHelper( skinnedMesh );
scene.add( skeletonHelper );

// Bounding box
const bboxHelper = new THREE.Box3Helper( object, color );
scene.add( bboxHelper );

// Box3 / bounding box
const boxHelper = new THREE.BoxHelper( object, color );
scene.add( boxHelper );

// Camera helper
const cameraHelper = new THREE.CameraHelper( camera );
scene.add( cameraHelper );

// Face normals
const normalsHelper = new THREE.FaceNormalsHelper( object, size, color, linewidth );
scene.add( normalsHelper );

// Vertex normals
const vertexNormalsHelper = new THREE.VertexNormalsHelper( object, size, color, linewidth );
scene.add( vertexNormalsHelper );

// Positional audio
import { PositionalAudioHelper } from 'three/addons/helpers/PositionalAudioHelper.js';

// Light probe
import { LightProbeHelper } from 'three/addons/helpers/LightProbeHelper.js';
import { LightProbeHelperGPU } from 'three/addons/helpers/LightProbeHelperGPU.js';

// RectAreaLight
import { RectAreaLightHelper } from 'three/addons/helpers/RectAreaLightHelper.js';

// Texture
import { TextureHelper } from 'three/addons/helpers/TextureHelper.js';
```

## Interaction

```js
// Sortable JS integration
import { Sortable } from 'three/addons/interactive/Sortable.js';

// CSS3D
import { CSS3DRenderer, CSS3DObject } from 'three/addons/renderers/CSS3DRenderer.js';

// HTML overlay
import { HTMLRenderer, HTMLObject } from 'three/addons/renderers/HTMLRenderer.js';
```

## Controls Gotchas

- **`controls.update()` required** — call every frame when `enableDamping` or `autoRotate` is true.
- **OrbitControls + TransformControls conflict** — OrbitControls should pause when TransformControls is active. Listen to `mouseDown`/`mouseUp` events.
- **`controls.dispose()`** — always call to remove event listeners and prevent memory leaks.
- **TransformControls must be in scene** — `scene.add( controls )` is required for the gizmo to render.
- **PointerLockControls needs user gesture** — `controls.lock()` must be called from a user event (click/tap).
- **Physics requires WASM** — Rapier and Jolt need to be initialized asynchronously before use.
