---
name: ct-js-5-3-1
description: >
  Ct.js v5.3.1 — 2D game engine built on Pixi.js for browser games. Use when building or working with ct.js games:
  templates, copies, rooms, actions/inputs, camera, sounds, emitters, tilemaps, backgrounds, behaviors,
  content subsystem, styles, timers, or the ct.place collision module. Covers the full ct.js API including
  creating and managing copies, room transitions, input actions, camera following and effects,
  particle emitters, procedural tilemaps, sound playback, content tables, and UI coordinate systems.
  All ct.js games run as vanilla JS in the browser; ct.js IDE is used for asset editing and export only.
metadata:
  tags:
    - game-engine
    - 2d
    - pixi-js
    - game-dev
    - javascript
    - browser
---

# ct-js 5.3.1

## Overview

Ct.js is a 2D game engine that compiles to vanilla JavaScript games running in browsers (or Electron/Neutralino desktop builds). It uses Pixi.js for rendering and sound. The ct.js IDE handles asset creation, room editing, and project export — but all game code runs as plain JavaScript in the browser with no build step.

### Core Concepts

- **Textures** — images (sprites, tilesets, backgrounds). Imported in ct.js IDE, referenced by name in code.
- **Templates** — blueprints for entities. Define base class, texture, events, and behaviors. Think "class" or "prefab".
- **Copies** — runtime instances of templates. Created with `templates.copy()`. Everything on screen is a copy.
- **Rooms** — boundless 2D spaces (levels/maps) containing copies, backgrounds, and tile layers.

### Global API

Ct.js exposes a flat namespace of global objects attached to `window`. No imports needed:

| Object | Purpose |
|---|---|
| `templates` | Create/find copies, iterate all copies |
| `rooms` | Manage rooms, switch, append UI layers |
| `camera` | Viewport control, following, zoom, screen shake |
| `actions` | Input abstraction (keyboard, gamepad, pointer, virtual keys) |
| `inputs` | Create/remove actions programmatically |
| `sounds` | Play/stop/pause/fade sounds, apply filters |
| `res` | Load textures, atlases, scripts; browse asset tree |
| `u` | Utility functions (geometry, math, time, collision helpers) |
| `timer` | Create Promise-based timers |
| `tilemaps` | Create and manage tile layers |
| `backgrounds` | Create and manage background layers |
| `styles` | Text styles for UI labels |
| `emitters` | Particle effects (only if emitter tandems exist) |
| `behaviors` | Add/remove shared logic to templates or rooms |
| `content` | Structured data tables (local database) |
| `scripts` | Custom scripts defined in project |
| `settings` | Render settings (FPS, view mode, fullscreen, high-DPI) |
| `pixiApp` | The underlying Pixi.js Application instance |

### Event System

Game logic is event-driven. Each copy and room responds to events:

- **OnCreate** — once, when the copy is created
- **OnStep** — every frame (game logic, input, movement)
- **OnDraw** — every frame after movement (custom drawing)
- **OnDestroy** — when `this.kill = true` (cleanup)
- **OnStart** (rooms) — after all copies are created in the room
- **OnLeave** (rooms) — when switching away from this room

Frame loop order: Frame Start (copies) → Frame Start (room) → Destroy killed copies → Frame End (copies) → Frame End (room) → input cleared.

### Coordinate Systems

Ct.js has two coordinate spaces: **game coordinates** (managed by camera, used by gameplay copies) and **UI coordinates** (fixed to viewport, unaffected by camera). Use `u.uiToGameCoord()` and `u.gameToUiCoord()` to convert. UI rooms are created with `rooms.append('Name', {isUi: true})`.

## Usage

### Basic Game Setup

```js
// In a room's OnStart event — runs once after all copies are created
camera.follow = templates.list['Player'][0];
camera.borderX = 300;
camera.borderY = 200;
```

### Creating and Managing Copies

```js
// Create a copy at position (100, 200)
var bullet = templates.copy('Bullet', 100, 200);
bullet.direction = 90; // Face downward

// Create with extra parameters (available in OnCreate event)
var enemy = templates.copy('Enemy', 300, 400, {
    health: 100,
    variant: 'boss'
});

// Create in a specific room (e.g., a UI layer)
var uiLayer = rooms.list['UI_HUD'][0];
templates.copyIntoRoom('HUD_HealthBar', 10, 10, uiLayer, {
    maxHealth: 100
});

// Find copies
var players = templates.list['Player']; // Array of all Player copies
var firstPlayer = templates.list['Player'][0];

// Check if copy exists
if (templates.exists('Player')) { /* at least one Player copy */ }

// Check if a specific copy is still valid
if (templates.valid(firstPlayer)) { /* not killed */ }

// Iterate all copies
templates.each(function() {
    if (this !== me && u.pdc(this.x, this.y, me.x, me.y) < 100) {
        this.kill = true;
    }
});

// Destroy a copy
this.kill = true; // Logical deletion; OnStep still runs to completion
```

### Movement

```js
// Basic movement (OnStep)
this.hspeed = actions.MoveX.value * 200;
this.vspeed = actions.MoveY.value * 200;
this.move(); // Apply speed + gravity

// Platformer with collision (requires place catmod)
this.hspeed = actions.MoveX.value * 200;
if (place.occupied(this, this.x, this.y + 1, 'Solid')) {
    if (actions.Jump.pressed) {
        this.vspeed = -400;
    }
}
var result = this.moveSmart('Solid');
if (result && result.y) {
    this.vspeed = 0; // Reset on collision
}

// Precise bullet movement (prevents tunneling)
var obstacle = this.moveBullet('Solid');
if (obstacle && templates.isCopy(obstacle)) {
    obstacle.kill = true;
    this.kill = true;
}

// Grid-based movement
if (actions.MoveX.pressed) {
    this.x += Math.sign(actions.MoveX.value) * 64;
}
```

### Input Actions

```js
// Actions are defined in ct.js IDE (Project → Actions and input methods)
// In code, access via actions.ActionName

// Movement (scalar values -1 to 1)
this.hspeed = actions.MoveX.value * 300;
this.vspeed = actions.MoveY.value * 300;

// Single press detection (true only on the frame pressed)
if (actions.Shoot.pressed) {
    templates.copy('Bullet', this.x, this.y);
}

// Held state (true while held)
if (actions.Shoot.down) {
    // Continuous fire
}

// Release detection (true only on the frame released)
if (actions.Shoot.released) {
    // Stop continuous fire
}

// Create actions programmatically
inputs.addAction('CustomAction', [
    { code: 'keyboard.Space' },
    { code: 'pointer.primary' }
]);
```

### Room Management

```js
// Switch rooms
rooms.switch('Level_02');

// Restart current room
rooms.restart();

// Clear all copies in current room
rooms.clear();

// Add UI layer
rooms.append('UI_HUD', { isUi: true });

// Add background layer (behind main room)
rooms.prepend('BackgroundLayer');

// Merge room content into current room (for prefabs)
var merged = rooms.merge('AssassinsSet');
for (const copy of merged.copies) {
    copy.x += spawnX;
    copy.y += spawnY;
}

// Remove a layered room
rooms.remove(this.pauseMenu);
```

### Camera

```js
// Follow a copy
camera.follow = this;
camera.borderX = 300; // Camera shifts when copy is within 300px of edge
camera.borderY = 200;

// Move camera
camera.moveTo(x, y);     // Smooth transition (uses drift)
camera.teleportTo(x, y); // Instant, resets screen shake

// Zoom
camera.scale.x = 0.5; // Zoom in (smaller = closer)
camera.scale.y = 0.5;

// Rotation
camera.rotation = 45; // Degrees

// Screen shake
camera.shake += 2; // Add impulse (decays over time)

// Coordinate conversion
var gamePos = u.uiToGameCoord(pointer.x, pointer.y);
var uiPos = u.gameToUiCoord(this.x, this.y);
```

### Sounds

```js
// Play sound
sounds.play('Explosion');

// Play looping music
sounds.play('BackgroundMusic', { loop: true });

// 3D positional sound
sounds.playAt('Footstep', this); // Follows copy

// Volume control
sounds.volume('Music', 0.5);
sounds.globalVolume(0.8);

// Fade
sounds.fade('Music', 0, 2000); // Fade to 0 over 2 seconds

// Pause/resume
sounds.pause(); // All sounds
sounds.resume('Music');

// Preload before room switch
sounds.load('BattleMusic').then(() => {
    rooms.switch('Battle');
});
```

### Timers

```js
// Create a timer (Promise-based)
var myTimer = timer.add(2500, 'invincibility');
myTimer.then(() => {
    this.invincible = false;
});

// UI timer (unaffected by game pause)
timer.addUi(1000, 'ui-tick').then(() => {
    // Runs even when game is paused
});

// Manual control
myTimer.reject(); // Stop early (won't trigger then)
myTimer.resolve(); // Trigger immediately
```

## Gotchas

- **No imports or modules** — ct.js games run as vanilla JS with all globals on `window`. Use `templates.copy()`, not `import { templates } from 'ct.js'`.
- **`this.kill = true` does not destroy immediately** — OnStep runs to completion. The copy is removed between OnStep and OnDraw. Use `templates.valid(copy)` to check.
- **`this.move()` includes `u.time`** — speeds are in pixels per second, not per frame. Do not multiply by `u.time` when using `this.move()`.
- **`u.time` vs `u.timeUi`** — `u.time` is affected by game pause and slow-mo; `u.timeUi` is not. Use `u.timeUi` for UI animations.
- **`camera.shake` is relative to screen size** — value of 10 means 10% of the largest screen dimension, not pixels.
- **`templates.list['Name']` returns an array** — always access `[0]` for the first copy. The array updates in real-time.
- **`rooms.current` is the root room** — layered rooms (from `rooms.append`) are accessed via `rooms.list['Name']`.
- **`emitters` is only available if emitter tandems exist** — the module is not bundled otherwise. Check `typeof emitters !== 'undefined'`.
- **`place` catmod is separate** — `this.moveBullet()`, `this.moveSmart()`, `place.occupied()` require the `place` module enabled in project settings.
- **Collision groups are strings** — set in template/tile editor. Use consistent naming: `'Solid'`, `'Enemies'`, `'Player'`.
- **`res.getTexture()` returns an array** — use `res.getTexture('Name')[0]` for single frame, or `res.getTexture('Name', frame)` for specific frame.
- **`PIXI` is available globally** — ct.js exposes Pixi.js as `window.PIXI`. Use it for advanced rendering, custom filters, or direct sprite manipulation.
- **`pixiApp.ticker.speed = 0` pauses the game** — this is the standard way to implement game pause. Set back to `1` to resume.
- **`this.tex = 'NewTexture'` resets animation** — changing texture on AnimatedSprite copies restarts the animation from frame 0.
- **Direction 0 = right, 90 = up, 180 = left, 270 = down** — ct.js uses a non-standard direction system (Y grows downward, 90 is up not down).
- **`camera.realign(room)` is for dynamic UI** — use room editor's UI alignment tools for static UI. `realign` is for copies created at runtime.
- **`settings.viewMode` affects everything** — changing it resizes the viewport. Common: `'fastScale'` for pixel art, `'scaleFit'` for quality scaling with letterboxing.
- **`rooms.merge()` does NOT call events** — merged room's OnCreate/OnStep are not triggered. You get raw copies to position manually.
- **`behaviors.add/remove` only works for dynamic behaviors** — static behaviors (marked with ❄️ in IDE) cannot be removed at runtime.

## References

- [01-templates-copies](references/01-templates-copies.md) — Template base classes, copy properties, events, lifecycle
- [02-rooms](references/02-rooms.md) — Room class, room management, UI layers, merging, aligned copies
- [03-inputs-actions](references/03-inputs-actions.md) — Actions API, input methods, programmatic action creation
- [04-camera-viewport](references/04-camera-viewport.md) — Camera object, following, zoom, rotation, screen shake, coordinate conversion
- [05-movement](references/05-movement.md) — this.move(), moveBullet, moveSmart, grid movement, collision strategies
- [06-place-collision](references/06-place-collision.md) — ct.place module: occupied, free, meet, collide, tracing, tilemap collisions
- [07-sounds](references/07-sounds.md) — Sound playback, 3D audio, filters, volume, preloading
- [08-emitters](references/08-emitters.md) — Particle systems: fire, follow, append, manipulation
- [09-tilemaps](references/09-tilemaps.md) — Procedural tilemap creation, caching, diamond caching
- [10-backgrounds](references/10-backgrounds.md) — Background creation, parallax, movement
- [11-res-assets](references/11-res-assets.md) — Resource loading, asset tree, dynamic texture/atlas loading
- [12-utilities](references/12-utilities.md) — u namespace: geometry, math, time, color conversion, collision helpers
- [13-timers](references/13-timers.md) — Timer API, Promise-based timers, UI vs game timers
- [14-styles-text](references/14-styles-text.md) — Text styles, bitmap fonts, Text/TextBox base classes
- [15-behaviors](references/15-behaviors.md) — Shared logic, dynamic add/remove, fields, enumerations
- [16-content-system](references/16-content-system.md) — Content types, schemas, data tables
- [17-settings](references/17-settings.md) — Render settings, view modes, fullscreen, high-DPI, debug/production
