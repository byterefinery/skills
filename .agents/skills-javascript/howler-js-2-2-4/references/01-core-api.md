# Core API

## Howl Constructor

### Signature

```js
new Howl(options)
```

### Options Reference

#### `src` — `Array | String` *(required)*

Audio file URLs or base64 data URIs. Provide multiple formats in order of preference — howler.js picks the first codec the browser supports.

```js
src: ['sound.webm', 'sound.mp3', 'sound.wav']
src: 'data:audio/wav;base64,UklGR...'
```

#### `format` — `Array` `[]`

Explicitly specify formats when URL extension detection fails (e.g., SoundCloud streams, extensionless URLs).

```js
src: ['https://api.soundcloud.com/tracks/123/stream'],
format: ['mp3']
```

#### `volume` — `Number` `1.0`

Initial volume from `0.0` (silent) to `1.0` (full). Independent of `Howler.volume()` master control.

#### `html5` — `Boolean` `false`

Force HTML5 Audio backend. Required for streaming audio and large files. Web Audio must fully decode before playback.

#### `loop` — `Boolean` `false`

Loop playback continuously. Can be toggled at runtime with `loop(true/false)`.

#### `preload` — `Boolean | String` `true`

- `true` — download and decode full file immediately
- `'metadata'` — download only metadata (get duration without full download; HTML5 only)
- `false` — do not preload; call `load()` manually when ready

#### `autoplay` — `Boolean` `false`

Automatically play when loaded. Queued until `load` event fires.

#### `mute` — `Boolean` `false`

Start muted.

#### `rate` — `Number` `1.0`

Playback rate multiplier. Range: `0.5` (half speed) to `4.0` (quadruple speed). Affects both speed and pitch.

#### `pool` — `Number` `5`

Size of the inactive sound pool. Each Howl maintains a pool of Sound instances that get recycled after playback ends. Increase for many simultaneous overlapping sounds.

#### `sprite` — `Object` `{}`

Sound sprite definition. Keys are sprite names, values are `[offset_ms, duration_ms, (loop_bool)]`.

```js
sprite: {
  laser:     [0,    300, false],
  explosion: [400,  1000, false],
  music:     [1500, 30000, true],
}
```

A default sprite `__default` covering the full audio is created automatically during load.

#### `xhr` — `Object` `{}`

Configure the XHR request used by Web Audio to fetch audio files.

```js
xhr: {
  method: 'GET',              // HTTP method
  headers: {                  // Custom headers
    Authorization: 'Bearer token',
  },
  withCredentials: false,     // Include cookies
}
```

### Event Callbacks (inline)

All events can be passed as constructor options with `on` prefix:

```js
new Howl({
  src: ['sound.mp3'],
  onload: () => console.log('loaded'),
  onloaderror: (id, msg) => console.error(msg),
  onplayerror: (id, msg) => console.error(msg),
  onplay: (id) => console.log('playing', id),
  onend: (id) => console.log('ended', id),
  onpause: (id) => console.log('paused', id),
  onstop: (id) => console.log('stopped', id),
  onmute: (id) => console.log('muted', id),
  onvolume: (id) => console.log('volume changed', id),
  onrate: (id) => console.log('rate changed', id),
  onseek: (id) => console.log('seeked', id),
  onfade: (id) => console.log('fade done', id),
  onunlock: () => console.log('audio unlocked'),
})
```

## Howl Methods

### `play([sprite | id])` → `Number`

Start playback. Returns the sound ID for individual control.

- Pass a sprite name (string) to play that region
- Pass a sound ID (number) to resume a previously paused sound
- Pass nothing to play the full audio (uses `__default` sprite)

If the sound hasn't loaded yet, the play is queued and fires on `load`.

```js
const id = sound.play('laser');
sound.pause(id);
sound.play(id);  // resume from pause
```

### `pause([id])` → `Howl`

Pause playback, preserving seek position. Omit `id` to pause all sounds in the group.

### `stop([id])` → `Howl`

Stop playback and reset seek to beginning. Omit `id` to stop all.

### `mute([muted], [id])` → `Howl | Boolean`

- `mute()` — returns current mute state
- `mute(true)` — mute all sounds in group
- `mute(false, id)` — unmute specific sound

### `volume([vol], [id])` → `Howl | Number`

- `volume()` — returns group volume
- `volume(0.5)` — set all sounds to 0.5
- `volume(id)` — returns specific sound's volume
- `volume(0.5, id)` — set specific sound's volume

### `fade(from, to, len, [id])` → `Howl`

Fade between two volumes over `len` milliseconds. Fires `fade` event when complete.

```js
sound.fade(1.0, 0.0, 2000, id);  // fade out over 2 seconds
```

With Web Audio, uses native `linearRampToValueAtTime` for smooth fades. With HTML5 Audio, uses an internal interval.

### `rate([rate], [id])` → `Howl | Number`

- `rate()` — returns first sound's playback rate
- `rate(1.5)` — set all sounds to 1.5x
- `rate(id)` — returns specific sound's rate
- `rate(0.5, id)` — set specific sound to 0.5x

### `seek([seconds], [id])` → `Howl | Number`

- `seek()` — returns first sound's current position
- `seek(5.0)` — seek first sound to 5 seconds
- `seek(id)` — returns specific sound's position
- `seek(5.0, id)` — seek specific sound

Seeking a playing sound pauses briefly, repositions, and resumes.

### `loop([bool], [id])` → `Howl | Boolean`

- `loop()` — returns group loop state
- `loop(true)` — enable loop on all sounds
- `loop(id)` — returns specific sound's loop state
- `loop(false, id)` — disable loop on specific sound

### `playing([id])` → `Boolean`

Check if playing. With `id`, checks that specific sound. Without, checks if any sound in the group is playing.

### `duration([id])` → `Number`

Returns duration in seconds. Returns 0 until `load` event fires. With `id`, returns the sprite duration for that sound instance.

### `state()` → `String`

Returns `'unloaded'`, `'loading'`, or `'loaded'`.

### `on(event, fn, [id])` → `Howl`

Attach an event listener. Optionally scope to a specific sound ID.

```js
sound.on('end', (id) => {
  console.log('Sound', id, 'finished');
});

// Scoped to specific sound
sound.on('end', handler, soundId);
```

### `once(event, fn, [id])` → `Howl`

One-shot listener. Auto-removes after first fire.

### `off(event, [fn], [id])` → `Howl`

Remove listeners.

- `off('end')` — remove all `end` listeners
- `off('end', fn)` — remove specific listener
- `off('end', fn, id)` — remove listener for specific sound
- `off()` — remove all event listeners

### `load()` → `Howl`

Manually trigger load. Needed when `preload: false`.

### `unload()` → `null`

Destroy the Howl, stop all sounds, release resources, and remove from cache. The Howl object becomes unusable after this.

## Sound Pool Lifecycle

Each Howl maintains a pool of Sound instances:

1. **Creation**: First `play()` creates a Sound from the pool
2. **Active**: Sound is playing or paused
3. **Ended**: Sound finishes (or is stopped) — marked as ended but kept in pool
4. **Recycle**: Next `play()` reuses an ended Sound, calling `reset()`
5. **Drain**: Excess ended Sounds beyond `pool` size are removed

Paused sounds are **not** recycled — they stay active so they can be resumed. The pool size should accommodate the maximum number of simultaneously active sounds.

## Internal Sprite Format

Internally, howler.js normalizes sprites to this format:

```js
{
  __default: [0, duration * 1000],
  laser: [0, 300, false],
  music: [1500, 30000, true],
}
```

The `__default` sprite is created automatically during load, covering the full audio duration. Sprite values are `[start_offset_ms, duration_ms, (loop_bool)]`.

## Load Error Codes

The `loaderror` event passes an error code:

| Code | Meaning |
|---|---|
| 1 | Fetch aborted by user |
| 2 | Network error |
| 3 | Decode error |
| 4 | Source not suitable (codec/format) |
