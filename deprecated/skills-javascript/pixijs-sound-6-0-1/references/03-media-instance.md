# Media Instance

## Overview

`IMediaInstance` represents a single playback instance created by `Sound.play()`. Each instance has independent volume, speed, muted, and loop settings. Instances are pooled and reused after playback ends.

## Properties

| Property | Type | Description |
|---|---|---|
| `id` | `number` (readonly) | Auto-incrementing instance ID |
| `progress` | `number` (readonly) | Playback progress, 0 to 1 |
| `paused` | `boolean` | Paused state of this instance |
| `volume` | `number` | Instance volume 0–1 |
| `speed` | `number` | Instance playback rate |
| `loop` | `boolean` | Instance loop flag |
| `muted` | `boolean` | Instance muted flag |

## Methods

### `stop()`

Stop this instance.

```ts
instance.stop();
```

### `set(name, value)`

Set a property by name. Returns `this` for chaining.

```ts
instance.set('volume', 0.5);
instance.set('speed', 0.8);
instance.set('muted', true);
instance.set('loop', false);
instance.set('paused', true);

// Chaining
instance.set('volume', 0.5).set('speed', 0.8);
```

## Events

### `start`

Fired when playback begins.

```ts
instance.on('start', () => {
    console.log('Playback started');
});
```

### `end`

Fired when playback completes (fires per loop iteration).

```ts
instance.on('end', () => {
    console.log('Playback ended');
});
```

### `stop`

Fired when the instance is stopped explicitly.

```ts
instance.on('stop', () => {
    console.log('Playback stopped');
});
```

### `progress`

Fired during playback with progress and duration.

```ts
instance.on('progress', (progress, duration) => {
    console.log(`Progress: ${progress * 100}% of ${duration}s`);
});
```

### `pause`

Fired when paused state changes.

```ts
instance.on('pause', (paused) => {
    console.log(paused ? 'Paused' : 'Resumed');
});
```

### `paused`

Fired when the instance is paused.

```ts
instance.on('paused', () => {
    console.log('Instance paused');
});
```

### `resumed`

Fired when the instance is resumed.

```ts
instance.on('resumed', () => {
    console.log('Instance resumed');
});
```

## Event Methods

### `on(event, fn, context?)`

Subscribe to an event.

```ts
instance.on('end', () => { /* ... */ });
```

### `once(event, fn, context?)`

One-shot event subscription.

```ts
instance.once('end', () => { /* fires once */ });
```

### `off(event, fn?, context?, once?)`

Remove event listener(s).

```ts
instance.off('progress', handler);
instance.off('progress'); // Remove all progress listeners
```

## Instance Lifecycle

1. **Created** — Pooled or new instance from `Sound.play()`
2. **Playing** — Instance is actively playing audio
3. **Paused** — Playback paused, position preserved
4. **Ended** — Playback completed, `end` event fired
5. **Stopped** — Explicitly stopped, `stop` event fired
6. **Pooled** — Returned to pool for reuse

## Usage Patterns

### Per-instance volume control

```ts
const instance = sound.play('explosion');
instance.set('volume', 0.3);
```

### Progress tracking

```ts
const instance = sound.play('music');
instance.on('progress', (progress, duration) => {
    progressBar.value = progress;
});
```

### One-shot completion

```ts
sound.play('explosion').once('end', () => {
    console.log('Explosion finished');
});
```

### Conditional stopping

```ts
const instance = sound.play('music');

// Stop after 10 seconds
setTimeout(() => {
    if (instance && !instance.paused) {
        instance.stop();
    }
}, 10000);
```
