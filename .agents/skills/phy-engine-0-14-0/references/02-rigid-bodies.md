# Rigid Bodies

## Body Types

phy-engine supports these rigid body shape types:

| Type | Description | Notes |
|------|-------------|-------|
| `box` | Axis-aligned box | Most common, cheapest |
| `sphere` | Sphere | Single size value: `size: [radius]` |
| `cylinder` | Cylinder | `size: [radius, height]` |
| `capsule` | Capsule | `size: [radius, height]` |
| `cone` | Cone | Converted to convex on PhysX/Havok/Jolt |
| `plane` | Infinite plane | Always static, good for ground |
| `mesh` | Triangle mesh | Always static, pass `shape` geometry |
| `convex` | Convex hull | Pass `shape` geometry, dynamic support |
| `compound` | Multiple shapes | Array of `shapes`, each with own type/pos/size |
| `null` | Invisible body | No visual geometry |

### Extra Geometry Types

| Type | Description |
|------|-------------|
| `ChamferBox` | Box with rounded edges (add `radius` for chamfer amount) |
| `ChamferCyl` | Cylinder with rounded edges |
| `highSphere` | High-detail sphere (maps to `sphere` internally) |
| `customSphere` | Custom-segment sphere |
| `stair` | Angled box (auto-calculated rotation) |

## Adding Bodies

```js
phy.add({
    name: 'myBox',          // optional, auto-generated if omitted
    type: 'box',            // shape type
    size: [1, 2, 1],        // [x, y, z] dimensions
    pos: [0, 5, 0],         // [x, y, z] position
    rot: [0, 45, 0],        // Euler rotation in degrees [x, y, z]
    quat: [0, 0, 0, 1],     // quaternion [x, y, z, w] (alternative to rot)
    mass: 1,                // explicit mass
    density: 0.5,           // density (mass = density * volume)
    kinematic: false,       // kinematic body (moved by code, not physics)
    sleep: false,           // start sleeping
    visible: true,          // show visual mesh
    shadow: true,           // cast/receive shadows
    material: 'body',       // material name or THREE.Material
    ray: true,              // enable raycasting on this body
    collision: true,        // participate in collisions
});
```

### Mass vs Density

- Set `mass` for explicit mass control
- Set `density` for volume-based mass (mass = density × volume)
- If both are set, `mass` takes precedence
- No mass/density = static (immovable) body
- `mass: 0` or `density: 0` also makes it static

### Sphere and Cylinder Sizes

```js
// Sphere: single radius value
phy.add({ type: 'sphere', size: [0.5] });

// Cylinder: [radius, height]
phy.add({ type: 'cylinder', size: [0.3, 2.0] });

// Capsule: [radius, height] (height is the cylinder portion)
phy.add({ type: 'capsule', size: [0.3, 1.0] });
```

## Compound Shapes

Compound bodies group multiple sub-shapes into one rigid body:

```js
phy.add({
    type: 'compound',
    pos: [0, 8, 0],
    density: 0.5,
    shapes: [
        { type: 'box', size: [2, 0.2, 1], pos: [0, 0, 0] },
        { type: 'cylinder', size: [0.1, 1], pos: [-0.8, -0.5, 0] },
        { type: 'cylinder', size: [0.1, 1], pos: [0.8, -0.5, 0] },
    ],
});
```

Each sub-shape can have its own `type`, `size`, `pos` (local offset), `rot`, `seg`, and `radius`.

## Convex and Mesh Bodies

For custom geometry, pass a three.js BufferGeometry:

```js
import { TorusKnotGeometry } from 'three';

const geo = new TorusKnotGeometry(1, 0.3, 128, 16);

phy.add({
    type: 'convex',
    shape: geo,
    pos: [0, 10, 0],
    density: 0.5,
});
```

For static mesh collision (triangle mesh):

```js
phy.add({
    type: 'mesh',
    shape: geo,
    pos: [0, 5, 0],
});
```

### Engine-Specific Notes

- **Oimo/Jolt/Ammo/Cannon**: convex geometry must be non-indexed (phy auto-converts)
- **PhysX**: cylinders and cones are auto-converted to convex unless `real: true`
- **PhysX/Havok**: `massCenter` offset is supported directly
- **Rapier/Oimo**: `massCenter` is converted to a compound shape internally

## Kinematic Bodies

Kinematic bodies are moved programmatically and push dynamic bodies but are not affected by forces:

```js
phy.add({
    name: 'conveyor',
    type: 'box',
    size: [4, 0.2, 2],
    pos: [0, 1, 0],
    kinematic: true,
});

// Move it each frame
phy.change({ name: 'conveyor', pos: [Math.sin(time) * 3, 1, 0] });
```

## Instanced Bodies

For large numbers of identical objects, use instancing:

```js
// Create 100 instanced boxes sharing one draw call
for (let i = 0; i < 100; i++) {
    phy.add({
        instance: 'boxes',           // shared instance group name
        type: 'box',
        size: [0.2, 0.2, 0.2],
        pos: [Math.random() * 10 - 5, Math.random() * 10, Math.random() * 10 - 5],
        density: 0.1,
        randomColor: true,
    });
}
```

Options: `instance` (group name), `sizeByInstance` (vary size per instance), `speedMat` (color by velocity), `randomColor`.

## Chamfered Geometry

Add rounded edges to boxes and cylinders:

```js
// Chamfered box
phy.add({
    type: 'box',
    size: [2, 1, 1],
    radius: 0.1,       // chamfer radius — auto-converts to ChamferBox
    pos: [0, 5, 0],
    mass: 1,
});

// Chamfered cylinder
phy.add({
    type: 'cylinder',
    size: [0.5, 2],
    radius: 0.05,      // chamfer radius — auto-converts to ChamferCyl
    pos: [3, 5, 0],
    mass: 1,
});
```

## Breakable Bodies

```js
phy.add({
    type: 'box',
    size: [2, 2, 2],
    pos: [0, 10, 0],
    density: 1,
    breakable: true,
    breakOption: [250, 1, 2, 1],  // [force threshold, min pieces, max pieces, debris size]
});
```

## Mesh Replacement

Replace the default collision shape visual with a custom mesh:

```js
phy.add({
    type: 'box',
    size: [2, 1, 1],
    pos: [0, 5, 0],
    mass: 1,
    mesh: customModel,      // THREE.Object3D or Group
    meshPos: [0, 0, 0],     // mesh offset
    meshRot: [0, 0, 0],     // mesh rotation
    meshScale: [1, 1, 1],   // mesh scale
});
```

## Returned Object3D

`phy.add()` returns a three.js Object3D that mirrors the physics state:

```js
const body = phy.add({ type: 'box', size: [1, 1, 1], pos: [0, 5, 0], mass: 1 });

// Access properties
console.log(body.position);      // THREE.Vector3
console.log(body.quaternion);    // THREE.Quaternion
console.log(body.velocity);      // THREE.Vector3 (linear velocity)
console.log(body.angular);       // THREE.Vector3 (angular velocity)
console.log(body.mass);          // mass value
console.log(body.density);       // density value
console.log(body.isKinematic);   // kinematic flag
console.log(body.sleep);         // sleep state
```

## Changing Body Properties

```js
// Position and rotation
phy.change({ name: 'box', pos: [0, 3, 0], rot: [0, 90, 0] });

// Velocity
phy.change({ name: 'box', vel: [0, 5, 0] });

// Impulse
phy.change({ name: 'box', impulse: [0, 10, 0], impulseCenter: [0, 0, 0] });

// Angular velocity
phy.change({ name: 'box', angular: [0, 5, 0] });

// Wake/sleep
phy.change({ name: 'box', wake: true });
phy.change({ name: 'box', sleep: true });

// Toggle kinematic
phy.change({ name: 'box', kinematic: true });

// Enable velocity tracking
phy.change({ name: 'box', getVelocity: true });

// Edit compound shape sub-shapes
phy.change({ name: 'compound', editShape: [{ pos: [0, 0.5, 0] }, { pos: [0, -0.5, 0] }] });
```

## Collision Groups and Filtering

Use engine-specific flags/masks for collision filtering:

```js
// PhysX: collision flags
phy.add({ type: 'box', size: [1, 1, 1], flags: 0 });  // no collision

// Oimo: collision mask
phy.add({ type: 'box', size: [1, 1, 1], mask: 0 });  // no collision

// Havok: collision mask
phy.add({ type: 'box', size: [1, 1, 1], mask: 32 }); // no collision

// Universal: disable all collisions
phy.add({ type: 'box', size: [1, 1, 1], collision: false });
```

## Explosion Effect

Apply radial force to all bodies:

```js
phy.explosion(position, radius, force);

// Example: explode at origin, radius 10, force 1
phy.explosion([0, 0, 0], 10, 1);
```
