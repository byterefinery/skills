# Emitters (Particle Systems)

## Creating Effects

Three methods with different behavior:

### `emitters.fire(tandemName, x, y, [options])`

Spawns an effect at a location. Does not follow anything. Use for explosions, impact effects, sparkle bursts.

```js
emitters.fire('HeartTrail', this.x, this.y - 70);
```

### `emitters.follow(parentCopy, tandemName, [options])`

Attaches an effect to a copy. Leaves particles behind when moved. Use for smoke trails, bubble trails.

```js
emitters.follow(this, 'HeartTrail', {
    position: { x: 0, y: -70 }
});
```

### `emitters.append(parentCopy, tandemName, [options])`

Attaches an effect to a copy. Particles move with the copy. Use for magic shields, contained effects.

```js
this.shield = emitters.append(this, 'BubbleEffect');
```

## Options

| Property | Type | Description |
|---|---|---|
| `scale` | `{ x, y }` | Scale the effect |
| `position` | `{ x, y }` | Offset relative to parent copy |
| `prewarmDelay` | `number` | <0: prewarm (simulate before showing); >0: postpone |
| `tint` | `number` | Color tint (e.g. `0xff0000`) |
| `alpha` | `number` | Opacity (0-1) |
| `rotation` | `number` | Rotation in degrees |
| `isUi` | `boolean` | Use UI time scale (unaffected by slow-mo/pause) |
| `depth` | `number` | Depth (default `Infinity` = on top) |
| `room` | `Room` | Target room (default `rooms.current`) |

### Example: Smaller reddish effect above a copy

```js
emitters.follow(this, 'Debuff', {
    scale: { x: 0.75, y: 0.75 },
    position: { x: 0, y: -80 },
    tint: 0xff9999,
    depth: this.zIndex
});
```

## Manipulating Emitters

Each method returns a reference to the created effect:

```js
this.shield = emitters.append(this, 'BubbleEffect');

// Later...
this.shield.stop();   // Stop spawning new particles
this.shield = null;    // Free memory
```

### Emitter Methods and Properties

| Method/Property | Description |
|---|---|
| `emitter.stop()` | Stop spawning new particles; existing particles finish naturally |
| `emitter.clear()` | Instantly clear all particles |
| `emitter.kill = true` | Instantly destroy effect and all particles |
| `emitter.frozen = true` | Pause updating (freeze in place) |
| `emitter.pause()` | Stop spawning; remaining particles still animate |
| `emitter.resume()` | Resume spawning after pause |

## Automatic Cleanup

- Effects stop automatically when their time is up
- Effects stop when their parent copy is destroyed
- `follow` effects leave a nice trail of particles when parent is destroyed

## Gotchas

- **`emitters` only available if emitter tandems exist** — the module is not bundled otherwise. Check `typeof emitters !== 'undefined'`.
- **`position` doesn't work with `emitters.fire()`** — only with `follow` and `append`.
- **`depth` defaults to `Infinity`** — emitters overlay everything by default. Set `depth` to match copy's `zIndex`.
- **`isUi` for pause/slow-mo** — set `isUi: true` for effects that should continue during game pause.
- **`prewarmDelay` negative = prewarm** — simulate N seconds before showing. Positive = postpone.
- **Hold the reference** — emitters auto-cleanup, but hold the reference if you need to stop/kill manually.
- **`emitter.kill = true` vs `emitter.stop()`** — `kill` destroys instantly; `stop` lets existing particles finish.
- **`emitter.clear()` removes all particles** — use for instant cleanup.
- **`emitter.frozen` pauses updates** — different from `pause()` which only stops spawning.
