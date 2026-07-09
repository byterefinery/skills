# Camera and Viewport

## Camera Geometry

| Property | Type | Description |
|---|---|---|
| `camera.x`, `camera.y` | `number` | Real camera position (no shake applied) |
| `camera.targetX`, `camera.targetY` | `number` | Target position (used with drift for smooth transitions) |
| `camera.computedX`, `camera.computedY` | `number` | Final position (shake + shift applied) |
| `camera.width`, `camera.height` | `number` | Read-only: viewport dimensions |
| `camera.rotation` | `number` | Camera rotation in degrees |
| `camera.scale.x`, `camera.scale.y` | `number` | Zoom factor (1 = no zoom, 0.5 = 2x zoom in, 3 = 3x zoom out) |
| `camera.left`, `camera.top`, `camera.right`, `camera.bottom` | `number` | Camera edges in game coordinates |

## Camera Movement

```js
camera.moveTo(x, y);      // Smooth transition (uses drift)
camera.teleportTo(x, y);  // Instant, resets screen shake
```

### Following a Copy

```js
camera.follow = this;                    // Follow a copy
camera.followX = false;                  // Disable horizontal following
camera.followY = false;                  // Disable vertical following
camera.borderX = 300;                    // Camera shifts when copy is within 300px of edge
camera.borderY = 200;                    // In UI coordinates
```

### Manual Positioning

```js
camera.x = 100;       // Direct position
camera.y = 200;
camera.targetX = 100; // Smooth transition target
camera.targetY = 200;
```

## Zoom and Rotation

```js
camera.scale.x = 0.5;  // Zoom in (smaller value = closer view)
camera.scale.y = 0.5;

camera.rotation = 45;  // Rotate viewport (degrees, clockwise)
```

For smooth zoom/rotation, animate with `u.time` or `tween`:

```js
// Smooth zoom with tween
tween.add({
    obj: camera.scale,
    duration: 500,
    fields: { x: 0.5, y: 0.5 }
});

// Rotation by input
camera.rotation += actions.CameraRotate.value * u.time * 300;
```

## Screen Shake

```js
camera.shake += 2;              // Add impulse (accumulates, decays)
camera.shake = 5;               // Set absolute shake power
camera.shakeDecay = 5;          // Units subtracted per second (0 = no decay)
camera.shakeFrequency = 50;     // Oscillation frequency
camera.shakeX = 1;              // X-axis multiplier
camera.shakeY = 1;              // Y-axis multiplier
camera.shakeMax = 10;           // Maximum shake value
camera.shakePhase;              // Current oscillation phase
```

### Constant Wobble

```js
camera.shakeFrequency = 1;
camera.shakeDecay = 0;
camera.shake = 2;
```

## Camera Modifiers

```js
camera.drift = 0.9;           // Smooth transition (0 = instant, 1 = very smooth)
camera.shiftX = 50;           // Displace camera in UI units (doesn't change camera.x)
camera.shiftY = -30;
```

## Coordinate Conversion

```js
// UI → Game
var gamePos = u.uiToGameCoord(pointer.x, pointer.y);
var gamePos = camera.uiToGameCoord(pointer.x, pointer.y);

// Game → UI
var uiPos = u.gameToUiCoord(this.x, this.y);
var uiPos = camera.gameToUiCoord(this.x, this.y);
```

## Camera Corners and Bounds

```js
camera.getTopLeftCorner();    // { x, y } in game coords (accounts for rotation/scale)
camera.getTopRightCorner();
camera.getBottomLeftCorner();
camera.getBottomRightCorner();
camera.getBoundingBox();      // PIXI.Rectangle of camera in game coords
```

## Camera Clamping

```js
camera.minX = 0;    // Camera won't move left of x=0
camera.maxX = 800;  // Camera won't move right of x=800
camera.minY = 0;
camera.maxY = 600;

// Unset a clamp
delete camera.minX;
// or
camera.minX = undefined;
```

## Realign

```js
// Realign all copies in a room based on new camera dimensions
camera.realign(room);

// Skip realignment for specific copies
copy.skipRealign = true;
```

## Viewport Modes (settings.viewMode)

```js
settings.viewMode = 'asIs';             // No viewport management
settings.viewMode = 'fastScale';        // Proportional fill, no resolution change
settings.viewMode = 'fastScaleInteger'; // Integer scaling (x2, x3, x4)
settings.viewMode = 'expand';           // Fill screen, camera expands
settings.viewMode = 'scaleFit';         // Proportional with letterboxing
settings.viewMode = 'scaleFill';        // Fill screen, no letterboxing (camera expands)
```

## Coordinate Systems

### Game Coordinates

- Managed by camera; affected by camera position, zoom, and rotation
- Almost boundless; spans in any direction
- All gameplay copies exist in game space
- Cannot be repositioned manually (managed by camera)

### UI Coordinates

- Fixed rectangle from `0` to `camera.width` (horizontal) and `0` to `camera.height` (vertical)
- Unaffected by camera movement, zoom, or rotation
- Used for UI rooms: `rooms.append('Name', {isUi: true})`
- UI rooms can be repositioned manually

## Gotchas

- **Don't change camera values in Frame End** — camera updates between Frame Start and Frame End. Changes in Frame End cause coordinate conversion inconsistencies.
- **`camera.scale` is inverse of zoom** — smaller values = closer view (zoom in). `0.5` = 2x zoom in.
- **`camera.shake` is relative to screen size** — value of 10 = 10% of largest screen dimension, not pixels.
- **`camera.borderX/Y` are in UI coordinates** — not game coordinates.
- **`camera.moveTo` uses drift** — set `camera.drift` for smoothness. Use `camera.teleportTo` for instant movement.
- **`camera.shiftX/Y` are in UI units** — they displace the camera without changing `camera.x/y`.
- **`camera.realign` only works for static elements** — uses `xstart`/`ystart` for interpolation. Moving elements won't realign correctly.
- **`camera.realign` is for expand/scaleFill modes** — it has no effect in fastScale or scaleFit modes.
- **`camera.follow` overrides manual position** — when following is active, manual `camera.x/y` changes are overridden.
- **`camera.followX = false` still allows `teleportTo`** — disabling axis following doesn't prevent manual camera movement.
- **Rotated camera corners** — use `getTopLeftCorner()` etc. for rotated viewports; `camera.left/top/right/bottom` don't account for rotation.
- **High-DPI affects camera dimensions** — `settings.highDensity` changes the effective resolution.
- **`PIXI` world coordinates are UI coordinates** — don't use Pixi's world coordinate conversion; use `u.uiToGameCoord()` instead.
