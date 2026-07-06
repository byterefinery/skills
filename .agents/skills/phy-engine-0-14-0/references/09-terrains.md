# Terrains

## Overview

phy supports heightmap-based terrain via the `Landscape` object. Terrain behavior varies by backend.

## Creating Terrain

```js
const terrain = phy.add({
    type: 'terrain',
    name: 'ground',
    size: [100, 100],         // [width, depth] in world units
    heightData: heights,      // Float32Array of height values
    pos: [0, 0, 0],
    sample: 100,              // grid resolution (samples per axis)
    zone: 0.25,               // margin zone for collision accuracy
    material: terrainMaterial,
});
```

### Height Data

`heightData` is a flat `Float32Array` of height values. Size must match `(sample + 1) * (sample + 1)`:

```js
const sample = 100;
const heights = new Float32Array((sample + 1) * (sample + 1));

for (let z = 0; z <= sample; z++) {
    for (let x = 0; x <= sample; x++) {
        const idx = z * (sample + 1) + x;
        heights[idx] = Math.sin(x * 0.1) * Math.cos(z * 0.1) * 5;
    }
}

phy.add({
    type: 'terrain',
    name: 'ground',
    size: [100, 100],
    heightData: heights,
    sample: 100,
});
```

## Per-Engine Behavior

| Engine | Format | Orientation | Notes |
|--------|--------|-------------|-------|
| **PhysX** | Height field | Fixed (can't rotate) | `isAbsolute: true, isTurned: true` |
| **Havok** | Height field | Fixed | `isAbsolute: true, isTurned: true` |
| **Jolt** | Height field | Fixed | `isAbsolute: true, isTurned: false` |
| **Ammo** | Height field | Standard | Uses Bullet terrain shape |
| **Oimo** | Triangle mesh | Any rotation | Falls back to mesh collision |
| **Rapier** | — | — | No native terrain support |

### Orientation Constraints

- **PhysX/Havok/Jolt**: Terrain has fixed orientation. `quat` is forced to `[0, 0, 0, 1]` (PhysX) or standard (others).
- **Oimo**: Terrain is converted to a triangle mesh, supporting any rotation.

## Dynamic Height Updates

Update terrain heights during simulation:

```js
// Modify height data
heights[idx] = newHeight;

// Push update through flow
phy.flow.tmp.push({ name: 'ground', heightData: heights });
```

Or use the terrain's `physicsUpdate` callback:

```js
terrain.physicsUpdate('ground', newHeights);
```

## Terrain Material

The terrain uses an extended shader with `onBeforeCompile` hook:

```js
const mat = phy.material({
    color: 0x3a5f0b,
    // terrain material options
});

phy.add({
    type: 'terrain',
    name: 'ground',
    size: [200, 200],
    heightData: heights,
    sample: 200,
    material: mat,
});
```

## Gotchas

- **PhysX terrain can't rotate** — quaternion is forced to identity. Position the terrain before adding.
- **Height data size** — must be exactly `(sample + 1) * (sample + 1)` Float32 values.
- **`zone` parameter** — collision margin. Default `0.25`. Higher values prevent tunneling at terrain edges.
- **Rapier has no terrain** — use a convex or mesh body instead.
- **Oimo uses mesh fallback** — terrain is converted to triangle mesh, which is less efficient than a height field.
- **Memory** — large terrains (200+ samples) use significant memory for height data.
- **`size` is `[width, depth]`** — not `[x, y, z]`. Y (height) comes from `heightData`.
- **Height updates go through flow** — use `phy.flow.tmp.push()` or `physicsUpdate()`, not `phy.change()`.
