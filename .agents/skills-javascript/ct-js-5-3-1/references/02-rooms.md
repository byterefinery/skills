# Rooms

## Room Class

Rooms derive from `PIXI.Container` and inherit all its methods. They contain copies, backgrounds, tile layers, and advanced entities.

### Notable Room Properties

| Property | Type | Description |
|---|---|---|
| `alpha` | `number` | Room opacity (0 = transparent, 1 = opaque) |
| `isUi` | `boolean` | If `true`, room is unaffected by camera transforms |
| `x`, `y` | `number` | Room location (only works if `isUi` is `true`) |

### UI vs Gameplay Rooms

- **Gameplay rooms** — managed by `camera`, cannot be repositioned manually
- **UI rooms** — created with `rooms.append('Name', {isUi: true})`, can be moved/transformed freely
- UI coordinates: `0` to `camera.width` (horizontal), `0` to `camera.height` (vertical)

## Rooms API

### Current Room

```js
rooms.current;  // The root room (initial room or after rooms.switch)
```

### Room Transitions

```js
rooms.switch('NewRoomName');  // Call onleave on current, load new room
rooms.restart();              // Call onleave, restart current room
rooms.clear();                // Destroy all copies in current room
```

### Layered Rooms

```js
// Add room above main room
rooms.append('UI_HUD', { isUi: true });

// Add room behind main room
rooms.prepend('BackgroundLayer', { color: 0x446ADB });

// Remove a layered room (cannot remove rooms.current)
rooms.remove(layerRoom);

// Merge room content into current room (for prefabs/procedural generation)
var merged = rooms.merge('AssassinsSet');
// Returns { copies: [...], tileLayers: [...], backgrounds: [...] }
```

### Room Access

```js
rooms.templates;                    // List of available room names
rooms.list['RoomName'];             // Array of rooms on stage by name
rooms.list['UI_HUD'][0];            // First instance of UI_HUD room
```

### Merged Room Example

```js
var spawnX = 100, spawnY = 500;
var merged = rooms.merge('AssassinsSet');

for (const copy of merged.copies) {
    copy.xstart += spawnX;
    copy.x += spawnX;
    copy.ystart += spawnY;
    copy.y += spawnY;
}
```

## Aligned Copies

Rooms have methods to align copies based on camera dimension changes. Use these for responsive UI elements.

### `room.makeCopyAligned(copy, options)`

Assumes the copy is positioned relative to current camera dimensions.

### `room.makeCopyAlignedRef(copy, options)`

Assumes the copy is positioned relative to room dimensions as set in ct.js IDE.

```js
// Create a copy aligned to top center
var copy = templates.copy('BossHealthbar', this.template.width / 2, 0);
this.makeCopyAlignedRef(copy, {
    alignX: 'center',
    alignY: 'start'
});
```

#### Alignment Options

| Property | Values | Description |
|---|---|---|
| `alignX` | `'start'`, `'end'`, `'center'`, `'both'`, `'scale'` | Horizontal alignment |
| `alignY` | `'start'`, `'end'`, `'center'`, `'both'`, `'scale'` | Vertical alignment |
| `frame` | `{ x1, y1, x2, y2 }` | Reference frame (percentages of viewport) |
| `padding` | `{ left, right, top, bottom }` | Fixed gaps inside reference frame |

#### Alignment Values

- `'start'` — aligned to top/left of frame
- `'end'` — aligned to bottom/right of frame
- `'center'` — aligned to center of frame
- `'both'` — stretched to fill frame (gaps maintained at fixed size)
- `'scale'` — scaled proportionally to frame

#### Custom Frame Example

```js
// Align to left third of screen
this.makeCopyAlignedRef(copy, {
    alignX: 'both',
    alignY: 'both',
    frame: { x1: 0, y1: 0, x2: 33.3, y2: 100 }
});
```

#### Padding Example

```js
// Scale proportionally with horizontal gaps
this.makeCopyAlignedRef(copy, {
    alignX: 'both',
    alignY: 'start',
    padding: { left: 160, right: 160, top: 0, bottom: 0 }
});
```

## Room Events

- **OnCreate** — called when room is created
- **OnStart** — called after all copies in the room are created
- **OnStep** — called every frame (room-level logic)
- **OnDraw** — called every frame (room-level drawing)
- **OnLeave** — called when switching away from this room

## Gotchas

- **`rooms.current` is always the root room** — layered rooms are accessed via `rooms.list['Name']`.
- **`rooms.merge()` does NOT call events** — no OnCreate, OnStep, etc. for merged copies.
- **`rooms.merge()` result is not live** — the returned object is for initial setup only. Don't store it.
- **`rooms.remove()` cannot remove `rooms.current`** — use `rooms.switch()` to change the root room.
- **`rooms.remove()` triggers OnLeave and OnDestroy** — copies in the removed room get their destroy events.
- **`copy.getRoom().kill`** — check if a copy's room is being removed to prevent execution in dying rooms.
- **UI rooms can be repositioned** — gameplay rooms are managed by camera and override manual position changes.
- **`makeCopyAligned` vs `makeCopyAlignedRef`** — use `makeCopyAligned` for camera-relative positioning, `makeCopyAlignedRef` for IDE-dimension-relative positioning.
- **Default frame is full viewport** — if `frame` is omitted, it defaults to `(0,0)` to `(100,100)`.
- **`skipRealign` property** — set `copy.skipRealign = true` to exclude a copy from `camera.realign()`.
