# Soft Bodies

## Overview

Soft body simulation is available on **Ammo** (Bullet) backend. Other backends have limited or no soft body support.

phy supports these soft body types:

| Type | Description |
|------|-------------|
| `softCloth` | Cloth simulation (plane with divisions) |
| `softRope` | Rope simulation (tubular path with segments) |
| `softMesh` | Soft triangle mesh |
| `softTriMesh` | Soft triangle mesh (alias) |
| `softConvex` | Soft convex hull |
| `softEllips` | Soft ellipsoid |

## Soft Cloth

```js
phy.add({
    type: 'softCloth',
    name: 'flag',
    size: [10, 0, 10],       // [width, 0, height]
    div: [16, 16],            // [horizontal, vertical] divisions
    pos: [0, 5, 0],
    material: 'soft',
});
```

The cloth is a subdivided plane. Higher divisions = more detail but more CPU.

### Cloth with Color

The cloth geometry includes a color attribute. Vertex colors are auto-updated based on Y position during simulation.

## Soft Rope

```js
phy.add({
    type: 'softRope',
    name: 'rope',
    start: [0, 10, 0],        // start point
    end: [0, 0, 0],           // end point
    numSeg: 20,               // number of segments
    radius: 0.1,              // rope radius
    numRad: 6,                // radial segments
    pos: [0, 5, 0],
});
```

### Custom Path

Use a `Tubular` geometry path:

```js
import { Tubular } from 'three';

const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 10, 0),
    new THREE.Vector3(2, 8, 1),
    new THREE.Vector3(-1, 5, -1),
    new THREE.Vector3(0, 0, 0),
]);

phy.add({
    type: 'softRope',
    name: 'rope',
    path: curve,
    numSeg: 30,
    radius: 0.15,
    numRad: 8,
});
```

## Soft Mesh / TriMesh

```js
import { TorusKnotGeometry } from 'three';

const geo = new TorusKnotGeometry(1, 0.3, 128, 16);

phy.add({
    type: 'softMesh',
    name: 'softBlob',
    shape: geo,
    size: [1, 1, 1],
    pos: [0, 10, 0],
});
```

The geometry vertices are extracted and simulated as soft body points.

## Soft Convex

```js
phy.add({
    type: 'softConvex',
    name: 'softBall',
    shape: geometry,
    size: [1, 1, 1],
    pos: [0, 10, 0],
});
```

## Soft Ellipsoid

```js
phy.add({
    type: 'softEllips',
    name: 'ellipsoid',
    // ellipsoid parameters
    pos: [0, 10, 0],
});
```

## Soft Solver (Alternative)

phy includes a `SoftSolver` extra for custom soft body simulation:

```js
const solver = phy.addSoftSolver({
    // soft solver options
});

// Update in animation loop
phy.updateSoftSolver();

// Clear
phy.clearSoftSolver();
```

## Gotchas

- **Ammo only** — soft body simulation is primarily supported on the Ammo (Bullet) backend.
- **High CPU cost** — soft bodies are expensive. Keep divisions/segments reasonable.
- **Cloth divisions** — `[16, 16]` is a good starting point. `[32, 32]` or higher may cause performance issues.
- **Rope segments** — `numSeg` controls flexibility. More segments = more flexible but more expensive.
- **Geometry extraction** — for `softMesh`/`softConvex`, vertices are extracted from the geometry. The original geometry is cloned and modified.
- **Color attribute** — cloth geometry auto-creates a color attribute. Vertex colors update during simulation.
- **Normal recalculation** — `computeVertexNormals()` is called each frame for soft bodies.
- **`softEllips`** — requires internal point data. Use through the engine's soft body API.
- **SoftSolver** — the extra `SoftSolver` is a separate system from engine-native soft bodies. It uses spring-mass simulation on the main thread.
