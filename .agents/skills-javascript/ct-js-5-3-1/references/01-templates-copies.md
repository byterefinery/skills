# Templates and Copies

## Template Base Classes

Each template in ct.js uses a base class that determines its Pixi.js parent class and available properties:

| Ct.js Base Class | Pixi.js Parent | Use Cases |
|---|---|---|
| **Animated Sprite** | `PIXI.AnimatedSprite` | Characters, items with frame-by-frame animation |
| **Button** | `PIXI.Container` | UI buttons with text and nine-slice panel |
| **Container** | `PIXI.Container` | Groups of elements moved/transformed together |
| **Panel** | `PIXI.NineSlicePlane` | UI panels with fixed corners, stretchable center |
| **Text** | `PIXI.Text` | Text labels, UI text |
| **TextBox** | `PIXI.Container` | Input fields (text, password, email, number) |
| **Repeating texture** | `PIXI.TilingSprite` | Tiled, scrolling backgrounds or surfaces |
| **Sprited counter** | `PIXI.TilingSprite` | Health bars, life counters (sprites in a row) |

### Animated Sprite Properties

```js
this.animationSpeed = 1;       // Animation speed multiplier
this.currentFrame;             // Read-only: current frame index
this.totalFrames;              // Read-only: total frames
this.gotoAndPlay(frameIndex);  // Jump to frame and play
this.gotoAndStop(frameIndex);  // Jump to frame and stop
this.play();                   // Start animation
this.stop();                   // Stop animation
```

### Text Properties

```js
this.text = 'New text';                    // Change displayed text
this.textStyle = styles.get('StyleName');  // Apply a text style
```

### Container Methods

```js
this.addChild(copy, sprite);       // Add children
this.removeChild(copy);            // Remove specific child
this.removeChildAt(index);         // Remove by index
this.children;                     // Array of children
this.setChildIndex(child, index);  // Reorder
this.sortChildren();               // Sort by zIndex
this.getBounds();                  // { x, y, width, height, top, bottom, left, right }
```

### Button Properties

```js
this.text.text = 'New label';  // Change button text
this.disabled = true;          // Disable/enable button
this.panel;                    // The nine-slice plane inside the button
```

### TextBox Properties

```js
this.text;                      // Current text value
this.fieldType;                 // 'text', 'password', 'email', 'number'
this.maxLength;                 // Max characters
```

### Repeating Texture Properties

```js
this.scrollX;                   // Horizontal scroll speed (px/s)
this.scrollY;                   // Vertical scroll speed (px/s)
this.tileScale.x;               // Texture stretch inside rectangle
this.tilePosition.x;            // Manual texture offset
```

### Sprited Counter

```js
this.count = 5;  // Number of sprites shown in a row
```

## Copy Properties

### Movement Properties

| Property | Type | Description |
|---|---|---|
| `x`, `y` | `number` | Current position |
| `xprev`, `yprev` | `number` | Position in previous frame |
| `xstart`, `ystart` | `number` | Position at creation |
| `speed` | `number` | Movement speed (pixels/second) |
| `hspeed`, `vspeed` | `number` | Horizontal/vertical speed |
| `direction` | `number` | Movement direction (0-360°, 0=right, 90=up) |
| `gravity` | `number` | Gravity force (added per second) |
| `gravityDir` | `number` | Gravity direction (default 90 = downward in ct.js coords) |

### Visual Properties

| Property | Type | Description |
|---|---|---|
| `alpha` | `number` | Opacity (0 = invisible, 1 = opaque) |
| `blendMode` | `number` | `PIXI.BLEND_MODES.NORMAL`, `ADD`, `MULTIPLY`, `SCREEN` |
| `zIndex` | `number` | Drawing layer (higher = on top) |
| `angle` | `number` | Rotation in degrees (0-360) |
| `scale` | `PIXI.ObservablePoint` | Scale factor (`this.scale = 0.5` or `this.scale.x`) |
| `tex` | `string` | Texture name (changing resets animation) |
| `tint` | `number` | Color tint (hex, e.g. `0xFF0000` for red) |
| `visible` | `boolean` | Visibility |

### Other Properties

| Property | Type | Description |
|---|---|---|
| `template` | `string` | Name of the template this copy belongs to |
| `kill` | `boolean` | Set to `true` to destroy the copy |
| `timer1`–`timer6` | `number` | Six built-in countdown timers (seconds) |
| `uid` | `number` | Unique identifier |
| `placedInRoom` | `boolean` | `true` if placed in room editor, `false` if created at runtime |
| `behaviors` | `string[]` | List of applied behavior names |
| `shape` | `object` | Collision shape of the current texture |

### Copy Methods

```js
this.move();           // Apply speed + gravity movement
this.addSpeed(spd, dir); // Add speed vector in a direction
this.getRoom();        // Returns the Room that owns this copy
```

## Copy Lifecycle

1. **Creation**: `templates.copy('Name', x, y, exts)` → `OnBeforeCreateModifier` → `OnCreate` → `onCreateModifier` → behavior OnCreate
2. **Each frame**: `onBeforeStep` → `OnStep` → `onAfterStep` → (if killed: `onDestroy` → `OnDestroy`) → `onBeforeDraw` → `OnDraw` → `onAfterDraw`
3. **Destruction**: Set `this.kill = true` → copy removed between OnStep and OnDraw → OnDestroy fires

## Templates API

```js
templates.copy('TemplateName', x, y, exts);              // Create copy in current room
templates.copyIntoRoom('Name', x, y, room, exts);        // Create copy in specific room
templates.each(func);                                    // Apply function to all copies
templates.withCopy(copy, func);                          // Apply function to one copy
templates.withTemplate('Name', func);                    // Apply function to all of one template
templates.exists('TemplateName');                        // Check if any copies exist
templates.valid(obj);                                    // Check if copy is still alive
templates.isCopy(obj);                                   // Check if object is a ct.js copy
templates.list['TemplateName'];                          // Array of all copies of template
templates.templates;                                     // Map of all template definitions
```

## Gotchas

- **`instanceof` doesn't work with ct.js base classes** — they are mixins, not constructors. Use `templates.isCopy()` instead.
- **`this.kill = true` is logical deletion** — OnStep still runs to completion. Copy is physically removed between OnStep and OnDraw.
- **`this.tex` reset animation** — Changing texture on AnimatedSprite copies restarts animation from frame 0.
- **`blendMode` has no effect on Container copies** — Containers don't render anything on their own.
- **`tex` property unavailable on Container and Text templates** — These base classes don't use textures directly.
- **`templates.list` arrays update in real-time** — When copies are killed, they are removed from the array.
- **`this.direction` 0 = right, 90 = up** — Non-standard: Y grows downward, so 90° is up (not down).
- **`this.speed` and `this.direction` are computed** — They derive from `hspeed`/`vspeed`. Setting `speed` adjusts both components proportionally.
- **`this.move()` already uses `u.time`** — Speed values are in pixels per second. Do not multiply by `u.time`.
- **Container children are in local coordinates** — Position children relative to container's origin, not the room.
- **Collision catmods need copies in room directly** — Copies inside containers may not be detected by collision checks.
