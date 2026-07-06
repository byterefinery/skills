---
name: phy-engine-0-14-0
description: Universal physics bridge for three.js supporting six backends (PhysX, Havok, Jolt, Rapier, Ammo, Oimo) with rigid bodies, joints, vehicles, characters, raycasts, soft bodies, and terrains. Use for 3D physics simulation in games, editors, and interactive demos.
metadata:
  tags:
    - three.js
    - physics
    - 3d
    - game-dev
    - simulation
---

# phy-engine 0.14.0

## Overview

phy-engine is a universal physics abstraction layer for three.js that unifies six physics backends under a single API. It bridges three.js scenes with physics engines running either in a Web Worker (recommended) or directly on the main thread. The engine supports rigid bodies, joints, raycasts, vehicles, character controllers, soft bodies, terrains, and articulation solvers.

### Supported Physics Backends

| Backend | Version | Strengths | Limitations |
|---------|---------|-----------|-------------|
| **PhysX** | 5.06.10 | Most complete API, articulation solvers, vehicles | Largest bundle |
| **Havok** | 1.3.12 | Industry standard, hyper-stable | No vehicle support |
| **Jolt** | 0.39.0 | Used in AAA games (Horizon), fast | Still maturing, fewer options |
| **Rapier** | 0.19.3 | Lightweight, good speed/stability | No vehicle support |
| **Ammo** | 3.2.6 | Bullet physics (WASM), soft bodies | Slower with many collisions, unmaintained |
| **Oimo** | 1.2.4 | Pure JS, lightest, simplest | No vehicles, no soft bodies, unmaintained |

### Architecture

phy-engine uses a four-level progressive loading model:

1. **`phy.init()`** — boot the chosen backend (Worker or Direct mode)
2. **`phy.set()`** — configure global settings (gravity, substeps, FPS)
3. **`phy.add()`** / **`phy.change()`** / **`phy.remove()`** — manage simulation objects
4. **Animation loop** — call `phy.doStep()` (if outside-step) and `phy.step()` each frame

The engine auto-generates names when not provided. All positions are `[x, y, z]` arrays, rotations are in degrees via `rot` or quaternions via `quat`. Mass is set via `mass` or `density` (mass = density × volume). Objects without mass/density are treated as static.

## Usage

### Installation and Setup

```bash
npm install --save phy-engine
```

Copy `node_modules/phy-engine/compact/` or `node_modules/phy-engine/build/` to your public folder (Worker mode needs the files accessible at runtime).

### Basic Initialization

```js
import { phy } from 'phy-engine';

phy.init({
    type: 'PHYSX',       // or 'HAVOK', 'JOLT', 'RAPIER', 'AMMO', 'OIMO'
    worker: true,         // run physics in a Web Worker (recommended)
    compact: true,        // use LZMA-compressed .bin files from /compact/
    scene: scene,         // three.js scene
    renderer: renderer,   // three.js renderer
    callback: onReady,    // called when physics engine is ready
});

function onReady() {
    phy.set({ substep: 1, gravity: [0, -9.81, 0], fps: 60 });
    phy.add({ type: 'plane', size: [300, 1, 300], visible: true });
    phy.add({ type: 'box', size: [1, 1, 1], pos: [0, 4, 0], mass: 1 });
    phy.add({ type: 'sphere', size: [0.5], pos: [0, 6, 0], mass: 1 });
    phy.start();
}
```

### Animation Loop

```js
function animate(stamp) {
    phy.doStep(stamp);  // triggers physics step at configured FPS
    phy.step();          // syncs three.js objects with physics state
    renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);
```

### Adding Bodies

```js
// Static box (no mass/density = static)
phy.add({ name: 'wall', type: 'box', size: [10, 4, 1], pos: [0, 2, -5] });

// Dynamic sphere
phy.add({ name: 'ball', type: 'sphere', size: [0.5], pos: [0, 10, 0], density: 1 });

// Capsule with explicit mass
phy.add({ type: 'capsule', size: [0.3, 1.0], pos: [3, 5, 0], mass: 2 });

// Compound shape (multiple sub-shapes)
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

### Changing Properties

```js
// Wake a sleeping body
phy.change({ name: 'ball', wake: true });

// Move a kinematic body
phy.change({ name: 'platform', pos: [0, 3, 0] });

// Apply impulse
phy.change({ name: 'ball', impulse: [0, 5, 0] });

// Batch changes
phy.change([
    { name: 'a', pos: [0, 1, 0] },
    { name: 'b', pos: [0, 2, 0] },
]);
```

### Removing Objects

```js
phy.remove('ball');
phy.remove(['box1', 'box2', 'box3']);
```

### Multiple Instances

```js
import { phy2 } from 'phy-engine';

const motorA = new phy2();
const motorB = new phy2();

motorA.init({ type: 'HAVOK', worker: true, scene, callback: () => motorA.start() });
motorB.init({ type: 'PHYSX', worker: true, scene, callback: () => motorB.start() });
```

## Gotchas

- **Worker mode requires accessible files** — the `.min.js` or `.bin` backend files must be served from a URL the Worker can load. Copy `build/` or `compact/` to your public folder. For Vite, add `optimizeDeps: { exclude: ['phy-engine'] }` to `vite.config.js` and use `useLocal: true, useModule: true` in init.
- **No mass/density means static** — objects without `mass` or `density` are immovable. Always set one for dynamic bodies.
- **Rotation is in degrees** — use `rot: [x, y, z]` for Euler angles in degrees, or `quat: [x, y, z, w]` for quaternions.
- **`doStep()` vs `step()`** — `doStep(stamp)` gates the physics timestep to the configured FPS. `step()` syncs visual state from the physics array. Both are needed each frame in outside-step mode. In Worker mode with `isTimeout`, the worker handles stepping internally.
- **PhysX-only features** — articulation solvers (`type: 'solver'`) and advanced vehicle types are PhysX-exclusive. Vehicles work on PhysX and Ammo only.
- **Havok has no vehicles** — use PhysX or Ammo if you need vehicle simulation.
- **Compact mode uses LZMA** — `compact: true` loads `.bin` files which are smaller but take longer to decompress. Use `useModule: true` for module-worker support.
- **Name collisions** — if you omit `name`, phy auto-generates one. Always set explicit names for objects you need to reference later via `phy.change()` or `phy.byName()`.
- **`phy.add()` returns an Object3D** — the returned object mirrors physics state. Access `.position`, `.quaternion`, `.velocity`, `.angular` on it.
- **Convex/mesh bodies need vertex data** — for `type: 'convex'` or `type: 'mesh'`, pass a three.js geometry via `shape` or `mesh`. The engine extracts vertices internally.
- **Contact events need `activeContact()`** — call `phy.activeContact()` before adding contact pairs, otherwise contact data won't flow back.
- **Joint body references** — pass `b1` and `b2` as names (strings) or Object3D references. phy resolves them internally.
- **Terrain orientation varies by engine** — PhysX/Havok/Jolt terrains have fixed orientation constraints. Oimo falls back to a mesh representation.

## References

- [01-init-and-config](references/01-init-and-config.md) — Engine initialization, global settings, Worker vs Direct mode, multiple instances
- [02-rigid-bodies](references/02-rigid-bodies.md) — Body types, shapes, mass/density, kinematic bodies, compounds, instances
- [03-joints](references/03-joints.md) — Joint types (hinge, prismatic, cylindrical, generic, fixe, spherical, distance, ragdoll), anchors, limits, drives
- [04-raycasting](references/04-raycasting.md) — Ray creation, parent-relative rays, hit data, callbacks
- [05-collision-and-contact](references/05-collision-and-contact.md) — Collision groups, contact pairs, event callbacks
- [06-vehicles](references/06-vehicles.md) — Car setup, RayCar, Kart, Helicopter, wheel configuration, driving controls
- [07-characters](references/07-characters.md) — Hero character controller, floating ray, slope detection, impulse movement
- [08-soft-bodies](references/08-soft-bodies.md) — Soft cloth, soft rope, soft mesh, soft convex, ellipsoid
- [09-terrains](references/09-terrains.md) — Heightmap terrain, per-engine behavior, dynamic height updates
- [10-solvers-and-articulations](references/10-solvers-and-articulations.md) — Articulation solvers (PhysX only), joint drives, angle animation
- [11-engines-comparison](references/11-engines-comparison.md) — Backend comparison, feature matrix, performance characteristics, selection guide
- [12-api-reference](references/12-api-reference.md) — Complete API surface, phy.set options, phy.add options, utility methods
