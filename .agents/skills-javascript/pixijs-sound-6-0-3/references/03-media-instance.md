# IMediaInstance

`play()` returns an `IMediaInstance` — a single playback of a Sound. Instances are created from a pool (`Sound._pool`), reused after finishing, and recycled. Do not hold references across plays.

This interface is implemented by `WebAudioInstance` and `HTMLAudioInstance`.

## Properties

| Property | Type | Notes |
|---|---|---|
| `id` | `number` (readonly) | Auto-incrementing |
| `progress` | `number` (readonly) | Playback progress from 0 to 1 |
| `paused` | `boolean` | If the instance is paused; may be `false` even when the sound or global context is paused |
| `volume` | `number` | Instance volume (0-1). Not the effective volume — global and sound volume also apply |
| `speed` | `number` | Instance playback rate. Global and sound speed multiply it |
| `loop` | `boolean` | Whether this instance loops |
| `muted` | `boolean` | Instance muted state |

## Methods

```ts
stop(): void
set(name: 'speed' | 'volume' | 'muted' | 'loop' | 'paused', value: number | boolean): this  // chainable
```

```ts
instance.set('volume', 0.5);
instance.set('speed', 0.8);
```

## Events

Use `on` / `once` / `off` (EventEmitter-style, `this`-returning for chaining):

| Event | Payload |
|---|---|
| `start` | — |
| `end` | — fired when the sound finishes playing |
| `stop` | — "Don't use after this is called." |
| `progress` | `(progress: number, duration: number)` — progress 0-1, total seconds |
| `pause` | `(paused: boolean)` — paused state changes |
| `paused` | — instance is paused |
| `resumed` | — instance is resumed |

```ts
instance.on('progress', (progress, duration) => {});
instance.once('end', () => {});
instance.off('progress', handler);
```

Note the EventEmitter overloads: `progress` and `pause` carry payloads; `start`, `end`, `stop`, `paused`, `resumed` take no arguments.

## Notes

- Per-instance control via `set()` affects only this instance — unlike setting `soundObj.volume`, which refreshes all instances.
- Instance `speed` multiplies with the Sound's speed and the global `speedAll`.
- After `end` or `stop`, the instance is returned to the pool and reinitialized for the next play; stale references become invalid.
