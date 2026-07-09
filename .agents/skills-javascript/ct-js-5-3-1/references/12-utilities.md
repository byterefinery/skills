# Utilities (u)

## Geometry

### Vector Components

```js
u.ldx(length, direction);     // Horizontal component (alias: u.lengthDirX)
u.ldy(length, direction);     // Vertical component (alias: u.lengthDirY)
```

### Distance and Direction

```js
u.distance(obj1, obj2);       // Distance between two objects with x,y
u.direction(obj1, obj2);      // Direction from obj1 to obj2 (degrees)
u.pdn(x1, y1, x2, y2);        // Point direction (alias: u.pointDirection)
u.pdc(x1, y1, x2, y2);        // Point distance (alias: u.pointDistance)
```

### Rotation

```js
u.rotate(x, y, deg);          // Rotate vector by degrees → { x, y }
u.rotateRad(x, y, rad);       // Rotate vector by radians → { x, y }
u.degToRad(deg);              // Degrees to radians
u.radToDeg(rad);              // Radians to degrees
u.deltaDir(dir1, dir2);       // Difference between two directions
```

## Coordinate Conversion

```js
u.uiToGameCoord(x, y);        // UI → game coordinates → { x, y }
u.gameToUiCoord(x, y);        // Game → UI coordinates → { x, y }
```

## Math

```js
u.clamp(min, val, max);       // Clamp value to range
u.lerp(a, b, alpha);          // Linear interpolation (0 = a, 1 = b)
u.unlerp(a, b, val);          // Inverse lerp (position of val in range)
u.map(val, inMin, inMax, outMin, outMax); // Remap value between ranges
```

## Collision Helpers

```js
u.prect(x, y, arg);           // Point in rectangle (alias: u.pointRectangle)
u.pcircle(x, y, arg);         // Point in circle (alias: u.pointCircle)
```

`arg` can be an array `[x1, y1, x2, y2]` (rectangle) or `[x1, y1, radius]` (circle), or a Copy with rectangular/circular shape.

## Time

| Property | Description |
|---|---|
| `u.time` | Previous frame duration in seconds. Affected by pause/slow-mo. |
| `u.timeUi` | Frame duration ignoring pause/slow-mo. |
| `u.delta` | **Deprecated**. Frame ratio (1 = normal, 2 = lagged). Use `u.time`. |
| `u.deltaUi` | **Deprecated**. Use `u.timeUi`. |

### Usage

```js
// Framerate-independent movement
this.x += this.windSpeed * u.time;

// UI animation (unaffected by pause)
this.alpha -= u.timeUi * 0.5;
```

## Color Conversion

```js
u.hexToPixi('#0dfac3');       // CSS hex → Pixi color number
u.pixiToHex(0x0dfac3);        // Pixi color → hex string
```

## Wait

```js
// Wait N milliseconds, then resolve
u.wait(1000).then(() => {
    if (!this.kill) {
        this.kill = true;
    }
});
```

Rejects if a new room loads before resolution.

## Enumeration Iteration

```js
// Loop over enumeration names
u.eachEnumName(EResource, (name) => {
    console.log(name);
});

// Loop over enumeration values
u.eachEnumValue(EnemyState, (value) => {
    console.log(value);
});
```

## Load Script

```js
u.load(url, callback);  // Load script and call callback when done
```

## Gotchas

- **`u.time` is in seconds** — not milliseconds. Multiply speed by `u.time` for framerate-independent movement.
- **`u.delta` is deprecated** — use `u.time` instead.
- **`u.time` affected by pause** — `pixiApp.ticker.speed = 0` makes `u.time` zero. Use `u.timeUi` for pause-independent timing.
- **`u.ldx/ldy` use degrees** — direction 0 = right, 90 = up.
- **`u.distance/direction` need x,y objects** — copies have them; plain numbers won't work.
- **`u.wait()` rejects on room switch** — always check if the target is still valid in the `.then()` callback.
- **`u.hexToPixi()` takes CSS format** — `'#ff0000'`, not `0xff0000`.
- **`u.pixiToHex()` returns CSS format** — use for DOM styling.
- **`u.prect/pcircle` accept Copies** — pass a Copy to use its collision shape.
- **`u.eachEnumName/Value` for built-in enumerations** — custom enumerations may have non-string/non-integer values.
- **`u.lerp` clamps at 0 and 1** — `alpha < 0` returns `a`, `alpha > 1` returns `b`.
