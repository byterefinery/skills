# Joints

## Joint Types

| Type | Alias | Description |
|------|-------|-------------|
| `fixe` | — | Welds two bodies together rigidly |
| `hinge` | `revolute` | Single-axis rotation (door hinge) |
| `prismatic` | — | Single-axis linear slide |
| `cylindrical` | `slider` | Combined rotation + linear on one axis |
| `spherical` | — | Free rotation around a point (ball joint) |
| `generic` | `universal`, `dof`, `d6` | Configurable multi-DOF joint |
| `distance` | — | Maintains fixed distance between two points |
| `ragdoll` | — | Pre-configured character joint chain |

## Basic Joint Creation

```js
phy.add({
    name: 'myJoint',
    type: 'hinge',
    b1: 'bodyA',           // first body (name or Object3D)
    b2: 'bodyB',           // second body (name or Object3D, or null for ground)
    pos1: [0, 0, 0],       // local anchor on body1
    pos2: [0, 0, 0],       // local anchor on body2
    axis1: [1, 0, 0],      // rotation axis on body1 (local)
    axis2: [1, 0, 0],      // rotation axis on body2 (local)
    visible: false,        // show joint debug visualization
});
```

### World-Space Anchors

Use `worldAnchor` instead of `pos1`/`pos2` to specify a single world position. phy converts to local space automatically:

```js
phy.add({
    type: 'hinge',
    b1: 'bodyA',
    b2: 'bodyB',
    worldAnchor: [2, 3, 0],   // single world position
    worldAxis: [0, 1, 0],     // world-space axis
});
```

### World Quaternion

```js
phy.add({
    type: 'hinge',
    b1: 'bodyA',
    b2: 'bodyB',
    worldAnchor: [2, 3, 0],
    worldQuat: [0, 0, 0, 1],  // quaternion orientation
});
```

## Hinge Joint

Single-axis rotation. Default axis is X `[1, 0, 0]`.

```js
phy.add({
    type: 'hinge',
    b1: 'door',
    b2: 'frame',
    pos1: [0.5, 0, 0],
    pos2: [-0.5, 0, 0],
    axis1: [0, 0, 1],    // rotate around Z
    axis2: [0, 0, 1],
    limit: [-45, 45],    // angular limits in degrees
});
```

### Hinge Drive

```js
phy.change({
    name: 'myHinge',
    drivePosition: {
        rot: [0, 90, 0],      // target rotation
        // or quat: [x, y, z, w]
    },
});
```

## Prismatic Joint

Linear slide along a single axis.

```js
phy.add({
    type: 'prismatic',
    b1: 'drawer',
    b2: 'cabinet',
    axis1: [1, 0, 0],      // slide along X
    axis2: [1, 0, 0],
    limit: [-1, 1],        // linear limits
});
```

## Cylindrical Joint

Combined rotation and linear movement on one axis.

```js
phy.add({
    type: 'cylindrical',
    b1: 'shaft',
    b2: 'housing',
    axis1: [0, 0, 1],
    axis2: [0, 0, 1],
});
```

## Generic Joint

Configurable multi-DOF joint. Supports position and orientation constraints.

```js
phy.add({
    type: 'generic',
    b1: 'bodyA',
    b2: 'bodyB',
    pos1: [0, 0, 0],
    pos2: [0, 0, 0],
    axis1: [1, 0, 0],
    axis2: [1, 0, 0],
    limit: [0, 0, 0, 0, 0, 0],  // [x, y, z, rx, ry, rz] limits
});
```

Mode aliases: `universal`, `dof`, `d6` all map to `generic`.

## Distance Joint

Maintains a fixed distance between two points.

```js
phy.add({
    type: 'distance',
    b1: 'bodyA',
    b2: 'bodyB',
    pos1: [0, 0, 0],
    pos2: [0, 0, 0],
});
```

## Spherical Joint

Free rotation around a fixed point (ball and socket).

```js
phy.add({
    type: 'spherical',
    b1: 'arm',
    b2: 'shoulder',
    pos1: [0, 0, 0],
    pos2: [0, 0, 0],
});
```

## Fixed Joint

Welds two bodies together. They move as a single rigid unit.

```js
phy.add({
    type: 'fixe',
    b1: 'partA',
    b2: 'partB',
    pos1: [0, 0, 0],
    pos2: [0, 0, 0],
});
```

## Changing Joint Properties

```js
// Toggle visibility
phy.change({ name: 'myJoint', visible: true });

// Drive position (for hinge/generic)
phy.change({
    name: 'myJoint',
    drivePosition: { rot: [0, 45, 0] },
});
```

## Joint Debug Visualization

Enable joint visualization globally:

```js
phy.init({ type: 'PHYSX', worker: true, jointVisible: true, ... });
```

Or per-joint:

```js
phy.add({ type: 'hinge', b1: 'a', b2: 'b', visible: true });
```

## Gotchas

- **Axis defaults** — if `axis1`/`axis2` are omitted, they default to `[1, 0, 0]` (X axis).
- **Anchor defaults** — if `pos1`/`pos2` are omitted, they default to `[0, 0, 0]` (body origin).
- **Body references** — `b1` and `b2` accept body names (strings) or Object3D references. phy resolves them internally.
- **Ground joints** — omit `b2` or set to `null` to anchor to the world.
- **`worldAnchor`** is converted to local space for each body automatically.
- **`worldAxis`** is converted to local axes for each body automatically.
- **Havok/Jolt** require both `axis1` and `axis1Y` (perpendicular axis). phy computes this from `quat1`/`quat2` automatically.
- **Oimo** has special handling for `worldQuat` — axes are derived from the quaternion.
- **Ammo hinge** with `worldAxis` needs an extra X-quaternion correction internally.
