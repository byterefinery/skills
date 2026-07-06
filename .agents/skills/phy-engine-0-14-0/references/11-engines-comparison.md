# Engines Comparison

## Feature Matrix

| Feature | PhysX | Havok | Jolt | Rapier | Ammo | Oimo |
|---------|-------|-------|------|--------|------|------|
| Rigid bodies | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Convex hull | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Triangle mesh | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Compound shapes | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Joints | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Vehicles | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Soft bodies | — | — | — | — | ✓ | ✗ |
| Articulation solver | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Contact events | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| Raycasting | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Terrain | ✓ | ✓ | ✓ | ✗ | ✓ | mesh |
| massCenter | ✓ | ✓ | ✓ | ✓ | — | compound |
| Worker mode | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Compact mode | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## Performance Characteristics

| Engine | Speed | Precision | Stability | Bundle Size |
|--------|-------|-----------|-----------|-------------|
| **PhysX** | 0.9/1.0 | 0.9/1.0 | Excellent | Largest (WASM) |
| **Havok** | 1.0/1.0 | 1.0/1.0 | Excellent | Large (WASM) |
| **Jolt** | 0.6/1.0 | 0.8/1.0 | Good | Medium (WASM) |
| **Rapier** | 0.6/1.0 | 0.9/1.0 | Good | Medium (WASM) |
| **Ammo** | 0.4/1.0 | 0.6/1.0 | Good | Large (WASM) |
| **Oimo** | 0.3/1.0 | 0.6/1.0 | Good | Smallest (pure JS) |

## Selection Guide

### Choose **PhysX** when:
- You need the most complete feature set
- You need articulation solvers for robotics/procedural animation
- You need vehicles with full suspension
- You want industry-standard NVIDIA physics
- Bundle size is not a concern

### Choose **Havok** when:
- You need maximum stability and precision
- You want industry-standard game physics (used in most AAA games)
- You don't need vehicles or soft bodies
- You want the simplest, most reliable simulation

### Choose **Jolt** when:
- You want modern physics (used in Horizon Forbidden West)
- You need a balance of features and performance
- You're OK with fewer options (still maturing)
- You don't need vehicles

### Choose **Rapier** when:
- You want lightweight, fast physics
- You need good stability for simple projects
- You want a pure Rust/WASM solution
- You don't need vehicles

### Choose **Ammo** when:
- You need soft body simulation (cloth, ropes, deformable objects)
- You need vehicles (Bullet-based)
- You're OK with slower performance on complex scenes
- You need Bullet physics compatibility

### Choose **Oimo** when:
- You want the smallest bundle (pure JavaScript, no WASM)
- You need maximum compatibility (no WASM requirements)
- Your simulation is simple (basic rigid bodies and joints)
- You don't need vehicles, soft bodies, or advanced features

## Backend Versions

| Engine | Version | Source |
|--------|---------|--------|
| PhysX | 5.06.10 | [fabmax/physx-js-webidl](https://github.com/fabmax/physx-js-webidl) |
| Havok | 1.3.12 | [BabylonJS/havok](https://github.com/BabylonJS/havok) |
| Jolt | 0.39.0 | [jrouwe/JoltPhysics.js](https://github.com/jrouwe/JoltPhysics.js) |
| Rapier | 0.19.3 | [dimforge/rapier.js](https://github.com/dimforge/rapier.js) |
| Ammo | 3.2.6 | [kripken/ammo.js](https://github.com/kripken/ammo.js) |
| Oimo | 1.2.4 | [saharan/OimoPhysics](https://github.com/saharan/OimoPhysics/) |

## File Requirements

Each backend needs these files served at runtime:

### Build Mode (`compact: false`)

| Engine | Module | Worker |
|--------|--------|--------|
| PhysX | `Physx.module.js` | `Physx.min.js` |
| Havok | `Havok.module.js` | `Havok.min.js` |
| Jolt | `Jolt.module.js` | `Jolt.min.js` |
| Rapier | `Rapier.module.js` | `Rapier.min.js` |
| Ammo | `Ammo.module.js` | `Ammo.min.js` |
| Oimo | `Oimo.module.js` | `Oimo.min.js` |

### Compact Mode (`compact: true`)

| Engine | Module | Classic |
|--------|--------|---------|
| PhysX | `Physx.module.bin` | `Physx.bin` |
| Havok | `Havok.module.bin` | `Havok.bin` |
| Jolt | `Jolt.module.bin` | `Jolt.bin` |
| Rapier | `Rapier.module.bin` | `Rapier.bin` |
| Ammo | `Ammo.module.bin` | `Ammo.bin` |
| Oimo | `Oimo.module.bin` | `Oimo.bin` |

## Known Limitations

- **PhysX**: Largest bundle size. Worker source for PhysX/Havok is private (compiled versions work without restriction).
- **Havok**: No vehicle support. No soft bodies.
- **Jolt**: Still maturing. Fewer configuration options. Contact events not yet supported.
- **Rapier**: No vehicle support. No terrain support. No contact events.
- **Ammo**: Slower with many simultaneous collisions. No active updates.
- **Oimo**: Pure JS means slower for complex scenes. No vehicles. No soft bodies. No contact events on some versions.
