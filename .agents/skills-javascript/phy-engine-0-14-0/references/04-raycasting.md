# Raycasting

## Creating Rays

Rays cast a line segment through the physics world and report the first body hit. They are visualized as colored lines (configurable).

```js
const ray = phy.add({
    type: 'ray',
    name: 'myRay',
    begin: [0, 10, 0],     // start point
    end: [0, 0, 0],        // end point
    visible: true,         // show ray line
    parent: null,          // attach to a body (name or Object3D)
    callback: onHit,       // called each frame with hit data
    noRotation: false,     // if true, ray follows parent position only
});
```

## Ray Data

The ray's hit data is available via `ray.data`:

```js
{
    name: 'myRay',
    hit: false,            // whether ray hit anything
    body: '',              // name of hit body
    point: [0, 0, 0],      // hit point (world coordinates)
    normal: [0, 0, 0],     // surface normal at hit point
    distance: 0,           // distance from begin to hit point
    angle: 0,              // angle between ray direction and normal
    parent: null,          // parent body reference
}
```

## Callback

```js
function onHit(data) {
    if (data.hit) {
        console.log(`Hit ${data.body} at ${data.point}`);
        console.log(`Normal: ${data.normal}, Distance: ${data.distance}`);
        console.log(`Angle: ${data.angle}°`);
    }
}
```

## Parent-Relative Rays

Attach a ray to a body so it moves/rotates with it:

```js
phy.add({
    type: 'ray',
    name: 'characterRay',
    begin: [0, 0, 0],       // local offset from parent
    end: [0, -2, 0],        // local offset from parent
    parent: 'character',    // parent body name
    callback: onGroundHit,
});
```

The ray's begin/end are in the parent's local space. Each frame, phy transforms them to world space before casting.

Use `noRotation: true` to follow parent position only (ignore rotation).

## Updating Rays

```js
// Change ray endpoints
phy.change({ name: 'myRay', begin: [1, 10, 0], end: [1, 0, 0] });
```

## Visual Colors

Ray lines use these default colors:

| State | Color |
|-------|-------|
| No hit (segment 1) | `[0.1, 0.4, 0.6]` (blue) |
| No hit (segment 2) | `[0.1, 0.4, 0.6]` (blue) |
| Hit (segment 1) | `[1.0, 0.1, 0.1]` (red) |
| Hit (segment 2) | `[0.1, 1.0, 0.1]` (green) |

## Multiple Rays

```js
// Ground check rays for a character
for (let i = 0; i < 4; i++) {
    const angle = (i / 4) * Math.PI * 2;
    const offset = 0.3;
    phy.add({
        type: 'ray',
        name: `groundRay${i}`,
        begin: [Math.cos(angle) * offset, 0, Math.sin(angle) * offset],
        end: [Math.cos(angle) * offset, -3, Math.sin(angle) * offset],
        parent: 'character',
    });
}
```

## Gotchas

- Rays are updated each frame automatically during `phy.step()`.
- The callback fires every frame regardless of hit state.
- `ray.data.hit` is a boolean; check it before reading other data fields.
- Parent rays are transformed using the parent's world matrix each frame.
- Rays don't participate in collision detection — they are query-only.
- Max 100 rays (configurable in `Config.js Max.ray`).
