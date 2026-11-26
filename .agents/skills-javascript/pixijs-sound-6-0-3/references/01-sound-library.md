# SoundLibrary

The singleton `sound` export is an instance of `SoundLibrary`. In the browser bundle it is the `PIXI.sound` global.

## Members

| Member | Type | Notes |
|---|---|---|
| `context` | `IMediaContext` (readonly) | The active backend context (WebAudio or HTMLAudio) |
| `filtersAll` | `Filter[]` get/set | Global filters on all output; WebAudio only (no-op in legacy) |
| `supported` | `boolean` (readonly) | `true` if WebAudio is available in this browser |
| `useLegacy` | `boolean` get/set | Force HTML5 Audio; must be set before loading any files |
| `disableAutoPause` | `boolean` get/set | WebAudio only; default `false` (auto-pause on window blur stays on) |
| `volumeAll` | `number` get/set | Global volume; setter calls `context.refresh()` |
| `speedAll` | `number` get/set | Global playback rate; setter calls `context.refresh()` |
| `togglePauseAll()` | `boolean` | Returns `true` if all sounds are paused after toggle |
| `pauseAll()` / `resumeAll()` | `this` | Chainable |
| `toggleMuteAll()` | `boolean` | Returns `true` if all sounds are muted after toggle |
| `muteAll()` / `unmuteAll()` | `this` | Chainable |
| `stopAll()` | `this` | Stops every sound (instances destroyed); sounds stay registered |
| `removeAll()` | `this` | Stops and destroys all sounds; they cannot be used afterwards |
| `close()` | `this` | Releases/destroys the AudioContext(s); nulls `_context` and `_sounds` |
| `init()` | `this` | Reinitializes: recreates contexts, clears sounds, sets `useLegacy = !supported` |

## add()

Two overloads:

```ts
// Single sound: source can be url string, Options, ArrayBuffer, AudioBuffer,
// HTMLAudioElement, or an existing Sound instance
add(alias: string, options?: Options | string | ArrayBuffer | AudioBuffer | HTMLAudioElement | Sound): Sound;

// Map of sounds: keys are aliases, values any of the above; globalOptions
// override each sound's own options with the same key
add(map: Record<string, Options | string | ArrayBuffer | AudioBuffer | HTMLAudioElement>, globalOptions?: Options): Record<string, Sound>;
```

Behavior:

- `add(alias, soundInstance)` registers an existing `Sound` object as-is.
- Strings become `{ url }`; arrays become `{ url: [...] }`; `ArrayBuffer`/`AudioBuffer`/`HTMLAudioElement` become `{ source }`.
- Re-adding an alias that exists fires `console.assert('Sound with alias ... already exists.')` (does not throw).
- Returns the `Sound` (single) or a `SoundMap` (map form) for chaining.

## Other methods

```ts
exists(alias: string, assert = false): boolean  // pass true to console.assert on missing
isPlaying(): boolean                            // true if ANY registered sound is playing
find(alias: string): Sound                     // console.asserts if missing
stop(alias): Sound                              // returns the Sound
pause(alias): Sound
resume(alias): Sound
volume(alias, volume?): number                  // getter when volume omitted
speed(alias, speed?): number
duration(alias): number                         // NaN until loaded / on failure
remove(alias): this                             // removes the sound AND every alias referencing it
play(alias, options?): IMediaInstance | Promise<IMediaInstance>
                                                // options may be PlayOptions, a sprite name (string),
                                                // or a CompleteCallback
```

## Notes

- `play()` delegates to `find(alias).play(options)` — the second argument as a string is treated as a sprite alias.
- `removeAll()` deduplicates with a `Set` before destroying, so multiple aliases to one Sound destroy it once.
- After `close()`, call `init()` before using the library again (e.g., after a hardware failure).
- `init()` sets `useLegacy = !supported` — an explicit `useLegacy` set after `init()` overrides it.
