# WebXR

## Session Management

```js
// Check support
if ( navigator.xr ) {
	const supported = await navigator.xr.isSessionSupported( 'immersive-vr' );
	// 'inline', 'immersive-vr', 'immersive-ar'
}

// Enter VR
renderer.xr.enabled = true;

const button = document.createElement( 'button' );
button.textContent = 'Enter VR';
button.addEventListener( 'click', async () => {
	const session = await navigator.xr.requestSession( 'immersive-vr', {
		optionalFeatures: [
			'local-floor',
			'bounded-floor',
			'hand-tracking',
			'layers',
		],
	} );
	renderer.xr.setSession( session );
} );
```

## XR Renderer Settings

```js
renderer.xr.enabled = true;
renderer.xr.setReferenceSpaceType( 'local-floor' ); // 'local', 'bounded-floor', 'unbounded'
renderer.xr.setFoveation( 1.0 );                    // [0, 1] foveated rendering
renderer.xr.getCamera( camera );                     // Get XR camera
renderer.xr.getController( index );                  // Get controller (0 or 1)
renderer.xr.getControllerGrip( index );              // Get controller grip
renderer.xr.getHand( index );                        // Get hand (0 or 1)
```

## Controllers

```js
// Controller models
import { VRButton } from 'three/addons/webxr/VRButton.js';
import { XRControllerModelFactory } from 'three/addons/webxr/XRControllerModelFactory.js';

const controllerModelFactory = new XRControllerModelFactory();

// Controller 0 (left)
const controller0 = renderer.xr.getController( 0 );
controller0.addEventListener( 'connected', ( event ) => {
	const controllerModel = controllerModelFactory.createControllerModel( controller0 );
	controller0.add( controllerModel );
} );
scene.add( controller0 );

// Controller 1 (right)
const controller1 = renderer.xr.getController( 1 );
controller1.addEventListener( 'connected', ( event ) => {
	const controllerModel = controllerModelFactory.createControllerModel( controller1 );
	controller1.add( controllerModel );
} );
scene.add( controller1 );

// Controller grip (for models)
const grip0 = renderer.xr.getControllerGrip( 0 );
const grip1 = renderer.xr.getControllerGrip( 1 );
scene.add( grip0, grip1 );

// Input events
controller0.addEventListener( 'selectstart', onSelectStart );
controller0.addEventListener( 'selectend', onSelectEnd );
controller0.addEventListener( 'squeeze', onSqueeze );

function onSelectStart( event ) {
	const raycaster = event.target;
	const intersects = raycaster.intersectObjects( scene.children, true );
	if ( intersects.length > 0 ) {
		// Select object
	}
}
```

## Hand Tracking

```js
// Request hand tracking
const session = await navigator.xr.requestSession( 'immersive-vr', {
	optionalFeatures: [ 'hand-tracking' ],
} );

// Get hand
const hand0 = renderer.xr.getHand( 0 );
const hand1 = renderer.xr.getHand( 1 );
scene.add( hand0, hand1 );

// Hand joints
import { XRHandMeshModel } from 'three/addons/webxr/XRHandMeshModel.js';
import { XRHandSkeleton } from 'three/addons/webxr/XRHandSkeleton.js';

const handSkeleton = new XRHandSkeleton();

hand0.addEventListener( 'connected', ( event ) => {
	const handModel = new XRHandMeshModel( hand0, handSkeleton );
	hand0.add( handModel );
} );
```

## Hit Testing

```js
// AR hit testing
const session = await navigator.xr.requestSession( 'immersive-ar', {
	requiredFeatures: [ 'hit-test' ],
	optionalFeatures: [ 'dom-overlay' ],
	domOverlay: { root: document.body },
} );

const viewerSpace = await session.requestReferenceSpace( 'viewer' );
const hitTestSource = await session.requestHitTestSource( { space: viewerSpace } );

// In render loop
const frame = event.frame;
const hitTestResults = frame.getHitTestResults( hitTestSource );
for ( const hit of hitTestResults ) {
	const pose = hit.getPose( frame.views[ 0 ].space );
	// Place object at pose.transform.position
}
```

## Depth Sensing (AR)

```js
// Request depth sensing
const session = await navigator.xr.requestSession( 'immersive-ar', {
	requiredFeatures: [ 'depth-sensing' ],
} );

// Access depth data
const depthSensing = renderer.xr.depthSensing;
const depthImage = depthSensing.depthImage;
const confidenceImage = depthSensing.confidenceImage;
```

## XR Camera

```js
// XR modifies the camera automatically
// Use renderer.xr.getCamera() to get the XR camera
const camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 0.01, 100 );
renderer.xr.getCamera( camera );

// For stereo rendering, use ArrayCamera
const arrayCamera = new THREE.ArrayCamera();
renderer.xr.getCamera( arrayCamera );
```

## VRButton

```js
import { VRButton } from 'three/addons/webxr/VRButton.js';

document.body.appendChild( VRButton.createButton( renderer ) );
```

## XR Layers

```js
// Quadrilateral layer (for passthrough cutouts)
const quadLayer = session.createLayer( {
	format: renderer.xr.getLayerFormat(),
	rectangle: true,
} );
session.updateRenderState( { layers: [ session.renderState.layers, quadLayer ] } );
```

## WebXR Gotchas

- **HTTPS required** — WebXR only works over HTTPS (or localhost).
- **`renderer.xr.enabled = true`** — must be set before rendering.
- **Camera is modified by XR** — don't manually update camera position during XR sessions.
- **Controllers are Ray objects** — use `controller.intersectObjects()` for picking.
- **Session lifecycle** — handle `session.end` event to clean up.
- **Hand tracking is optional** — check feature support before requesting.
- **AR requires `immersive-ar`** — different session type from VR.
- **Depth sensing is platform-specific** — not all AR devices support it.
- **Foveation** — higher values (closer to 1) reduce quality in peripheral vision but improve performance.
