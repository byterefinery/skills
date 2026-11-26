# Core Architecture

## Scene Graph

Three.js uses a hierarchical scene graph rooted at `Scene`. Every renderable object inherits from `Object3D`.

### Object3D

Base class for all 3D objects. Provides transform, parent-child relationships, and events.

```js
const obj = new THREE.Object3D();
obj.position.set( x, y, z );       // World-relative position
obj.rotation.set( x, y, z );        // Euler angles (radians)
obj.rotation.set( x, y, z, 'YXZ' ); // With rotation order
obj.quaternion.set( x, y, z, w );   // Quaternion rotation
obj.scale.set( x, y, z );           // Non-uniform scale
obj.lookAt( target );               // Orient toward target

// Matrix properties (computed from position/rotation/scale)
obj.matrixAutoUpdate = true;        // Default: auto-compute matrix
obj.updateMatrix();                  // Manual matrix update
obj.matrixWorld;                     // World-space matrix (updated during render)
```

**Key properties:**
- `uuid` — unique identifier (auto-generated)
- `name` — string label for identification
- `visible` — hide/show without removing from scene
- `castShadow` / `receiveShadow` — shadow participation
- `layers` — `Layers` bitmask for selective rendering/raycasting
- `userData` — arbitrary data object (serialized with GLTF)
- `parent` / `children` — hierarchy traversal

**Transform methods:**
- `add( child )` — add child, returns child
- `remove( child )` — remove child
- `getObjectById( id )` — find by internal ID
- `getObjectByName( name )` — find by name (first match)
- `getWorldPosition( target )` — resolve world position
- `getWorldQuaternion( target )` — resolve world quaternion
- `getWorldDirection( target )` — forward direction in world space
- `traverse( callback )` — depth-first traversal
- `traverseVisible( callback )` — skip hidden objects

### Scene

```js
const scene = new THREE.Scene();
scene.background = new THREE.Color( 0x111111 );
scene.backgroundBlurriness = 0;      // Blur background env map [0, 1]
scene.backgroundIntensity = 1;       // Attenuate background color
scene.environment = texture;         // Shared env map for physical materials
scene.environmentBlurriness = 0;     // Blur env map
scene.environmentIntensity = 1;      // Scale env map intensity
scene.fog = new THREE.Fog( 0xffffff, 0.01, 100 );
```

### Group

Lightweight container for organizing objects. Shares transform with children.

```js
const group = new THREE.Group();
group.add( mesh1, mesh2 );
scene.add( group );
```

### Layers

Bitmask system for selective rendering. 32 layers (0-31).

```js
const layers = new THREE.Layers();
layers.enable( 1 );       // Enable layer 1
layers.disable( 0 );      // Disable layer 0
layers.set( 5 );          // Set only layer 5
layers.test( layerSet );  // Test against another Layers

// Per-object
mesh.layers.enable( 1 );
mesh.layers.disable( 0 );

// Per-camera
camera.layers.enable( 1 );

// Per-raycaster
raycaster.layers.enable( 1 );
```

### Object Lifecycle

```js
// Creation
const mesh = new THREE.Mesh( geometry, material );

// Add to scene
scene.add( mesh );

// Events (EventDispatcher)
mesh.addEventListener( 'added', ( e ) => { /* ... */ } );
mesh.addEventListener( 'removed', ( e ) => { /* ... */ } );
mesh.addEventListener( 'childadded', ( e ) => { /* ... */ } );
mesh.addEventListener( 'childremoved', ( e ) => { /* ... */ } );

// Removal
scene.remove( mesh );

// Cleanup — free GPU memory
mesh.geometry.dispose();
mesh.material.dispose();
if ( mesh.material.map ) mesh.material.map.dispose();
```

### Render Order

Objects render in scene-graph order by default. Override with `renderOrder`:

```js
mesh.renderOrder = 1;  // Higher values render later
```

Useful for transparent objects that need specific draw ordering.

### Clipping

```js
// Per-object clipping planes
mesh.clippingPlanes = [ plane1, plane2 ];
mesh.clipShadows = true;

// Global clipping (renderer)
renderer.clippingPlanes = [ plane1 ];

// ClippingGroup — shared planes for a group of objects
const group = new THREE.ClippingGroup();
group.clippingPlanes = [ plane1, plane2 ];
group.add( mesh1, mesh2 );
```

### Frustum Culling

Automatic by default. Controls which objects are sent to the GPU:

```js
mesh.frustumCulled = true;   // Default: true
```

Disable for objects that might be momentarily outside the frustum but should still render (e.g., large objects near the edge).

### Bounding Volumes

```js
// Geometry bounding
geometry.boundingBox;   // Box3 (computed via geometry.computeBoundingBox())
geometry.boundingSphere; // Sphere (computed via geometry.computeBoundingSphere())

// Object bounding (world-space)
mesh.geometry.computeBoundingBox();
mesh.geometry.boundingBox.getBoundingSphere( sphere );
```

### Visibility

```js
mesh.visible = false;           // Hide object and all children
mesh.visible = true;            // Show

// Check if object is visible (considering parent chain)
mesh.visible;                   // Only checks this object
// Use traverseVisible() to find actually visible descendants
```
