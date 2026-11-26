# Animation

## AnimationMixer

Central controller for playing animations on objects.

```js
const mixer = new THREE.AnimationMixer( object );

// Play an animation clip
const action = mixer.clipAction( clip );
action.play();

// Multiple clips
const walkAction = mixer.clipAction( walkClip );
const runAction = mixer.clipAction( runClip );

// Crossfade between clips
walkAction.fadeOut( 0.5 );
runAction.reset().fadeIn( 0.5 ).play();

// Update mixer (every frame)
const delta = clock.getDelta();
mixer.update( delta );
```

### Action Properties

```js
action.play();
action.stop();
action.reset();           // Reset to beginning
action.paused = false;
action.timeScale = 1.0;   // Speed multiplier
action.weight = 1.0;      // Blend weight [0, 1]
action.loop = THREE.LoopRepeat; // LoopOnce, LoopRepeat, LoopPingPong
action.repetitions = 1;   // Number of repetitions (LoopRepeat)
action.clampWhenFinished = false; // Hold last frame
action.zeroSlopeAtStart = false;
action.zeroSlopeAtEnd = false;

// Fade
action.fadeIn( duration );
action.fadeOut( duration );
action.crossFadeTo( targetAction, duration, waitForFadeIn );

// Events
action.getMixer();
action.getClip();
action.getTracks();
action.timeScale;

// State
action.isRunning();
action.isPaused();
action.isReady();
action.isInProgress();
action.isInFadein();
action.isInFadeout();
action.isInFade();
action.isPlaying();
action.isScheduled();
action.hasBeenPlayed();
action.isReady();
action.getGraph();
```

## AnimationClip

A named animation sequence.

```js
// From loaded model
const clips = gltf.animations; // Array of AnimationClip

// Create manually
const clip = new THREE.AnimationClip(
	'name',          // Name
	duration,        // Duration in seconds (null = auto from tracks)
	tracks           // Array of KeyframeTrack
);

// Properties
clip.name;
clip.duration;
clip.tracks;
clip.timeScale;

// Methods
clip.trim();
clip.resetDuration();
clip.stripUniqueKeyTimes();
```

## KeyframeTrack

Interpolates a property over time.

```js
const track = new THREE.VectorKeyframeTrack(
	'.position',           // Property name path
	[ 0, 1, 2, 3 ],        // Times
	[ 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3 ], // Values (3 per keyframe)
	THREE.InterpolateLinear // Interpolation mode
);

// Track types
new THREE.NumberKeyframeTrack( propertyName, times, values, interpolation );
new THREE.VectorKeyframeTrack( propertyName, times, values, interpolation );
new THREE.QuaternionKeyframeTrack( propertyName, times, values, interpolation );
new THREE.ColorKeyframeTrack( propertyName, times, values, interpolation );
new THREE.StringKeyframeTrack( propertyName, times, values );
new THREE.TextKeyframeTrack( propertyName, times, values );
new THREE.BoolKeyframeTrack( propertyName, times, values );
new THREE.IndexKeyframeTrack( propertyName, times, values );
```

### Interpolation Modes

```js
THREE.InterpolateDiscrete  // Step interpolation
THREE.InterpolateLinear    // Linear interpolation (default)
THREE.InterpolateSmooth    // Smooth (Catmull-Rom)
THREE.InterpolateBezier    // Cubic Bezier (requires tangent data)
```

### Ending Modes

```js
THREE.ZeroCurvatureEnding
THREE.ZeroSlopeEnding
THREE.WrapAroundEnding
```

### Property Paths

```js
'.position'                  // Object position
'.rotation'                  // Object rotation
'.scale'                     // Object scale
'.material.color'            // Material color
'.morphTargetInfluences.0'   // Morph target 0 influence
'.children[0].position'      // Child position
```

## AnimationUtils

```js
// Create keyframe tracks from samples
THREE.AnimationUtils.createKeyframeTrack(
	propertyName,
	times,
	values,
	interpolation
);

// Create clip from object samples
THREE.AnimationUtils.create_clip(
	name,
	duration,
	hierarchy,
	fps
);

// Convert between formats
THREE.AnimationUtils.subclip( clip, name, start, end );
THREE.AnimationUtils.merge_clip( clip1, clip2, name );
THREE.AnimationUtils.multiplyClipScale( clip, scale );
```

## Morph Targets

Per-vertex animation stored in geometry.

```js
// Create geometry with morph targets
const geometry = new THREE.BufferGeometry();
geometry.setAttribute( 'position', new THREE.BufferAttribute( basePositions, 3 ) );

// Add morph target
const morphPositions = new Float32Array( [ /* displaced positions */ ] );
geometry.morphAttributes.position = [
	new THREE.BufferAttribute( morphPositions, 3 ),
	// Can have multiple morph targets
];

// Use with material
const material = new THREE.MeshStandardMaterial();
const mesh = new THREE.Mesh( geometry, material );

// Animate morph influences
mesh.morphTargetInfluences[ 0 ] = 0.5; // [0, 1] for each morph target
mesh.morphTargetInfluences[ 1 ] = 0.3;
```

### Morph Target Animation

```js
// Using AnimationMixer with morph targets
const track = new THREE.NumberKeyframeTrack(
	'.morphTargetInfluences[0]',
	[ 0, 1, 2 ],
	[ 0, 1, 0 ]
);
const clip = new THREE.AnimationClip( 'morph', 2, [ track ] );
const mixer = new THREE.AnimationMixer( mesh );
mixer.clipAction( clip ).play();
```

## Skinned Meshes

Vertex animation driven by a bone hierarchy.

```js
const skeleton = new THREE.Skeleton( bones, skinIndex, skinWeight );
const geometry = new THREE.SkinnedBufferGeometry();
// ... set position, skinIndex, skinWeight attributes

const material = new THREE.MeshStandardMaterial();
const skinnedMesh = new THREE.SkinnedMesh( geometry, material );
skinnedMesh.bind( skeleton, bindMatrix );

// Animate bones
bones[ 0 ].rotation.x = Math.sin( time ) * 0.5;
skinnedMesh.updateMatrixWorld( true );
```

### Bind Modes

```js
skinnedMesh.bindMode = THREE.AttachedBindMode;  // Default: shares world space
skinnedMesh.bindMode = THREE.DetachedBindMode;  // Independent world space
skinnedMesh.bindMatrix;
skinnedMesh.bindMatrixInverse;
```

### Skeleton Helper

```js
const helper = new THREE.SkeletonHelper( skinnedMesh );
scene.add( helper );
```

## Animation Loading from GLTF

```js
gltfLoader.load( 'model.glb', ( gltf ) => {
	const model = gltf.scene;
	const mixer = new THREE.AnimationMixer( model );

	// Play first animation
	if ( gltf.animations.length > 0 ) {
		const action = mixer.clipAction( gltf.animations[ 0 ] );
		action.play();
	}

	// Or play by name
	const clip = THREE.AnimationClip.findByName( gltf.animations, 'Walk' );
	if ( clip ) {
		mixer.clipAction( clip ).play();
	}

	scene.add( model );
} );
```

## Animation Gotchas

- **`mixer.update(delta)` every frame** — must be called with delta time. Without it, animations freeze.
- **`clipAction` returns a reusable action** — cache the action reference. Calling `clipAction` repeatedly creates new actions.
- **`fadeOut` + `fadeIn` for transitions** — use these for smooth blending between animations.
- **`timeScale` for speed control** — `action.timeScale = 0.5` plays at half speed. Negative values reverse.
- **Morph target count is fixed** — set at geometry creation. Cannot add morph targets after first render.
- **`bindMode` for shared skeletons** — use `DetachedBindMode` when sharing a skeleton across multiple meshes.
- **Quaternion tracks for rotation** — use `QuaternionKeyframeTrack` for smooth 3D rotation. Euler tracks can gimbal-lock.
- **Property paths use dot notation** — `'.position'` (with leading dot) for object properties, `'.material.color'` for nested.
- **`LoopOnce` vs `LoopRepeat`** — `LoopOnce` holds the last frame. `LoopRepeat` loops from start.
- **Animation memory** — dispose clips and mixers when done to free memory.
