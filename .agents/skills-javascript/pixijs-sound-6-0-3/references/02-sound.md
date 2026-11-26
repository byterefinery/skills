# Sound

`Sound` represents a single piece of loaded media. Properties such as `volume`, `muted`, `loop`, `speed` affect **all** instances of the sound.

## Creation

Use `Sound.from(source)` — the constructor is internal (takes `media` + options). Source forms:

```ts
Sound.from('path/to/file.mp3');                    // url string
Sound.from(['file.ogg', 'file.mp3']);              // url array, best supported format picked
Sound.from(audioData);                             // ArrayBuffer | AudioBuffer | HTMLAudioElement
Sound.from({ ...options });                        // full Options object
```

`Sound.from()` does **not** add the sound to the library. `sound.stopAll()`, `sound.removeAll()`, `sound.isPlaying()` skip it until `sound.add('alias', mySound)`. Global volume, speed, mute, pause, and filters still apply.

### Options

Defaults from the source (`withoutUndefined` merges your options over these):

```ts
{
    autoPlay: false,        // play immediately after load (implies preload)
    singleInstance: false,  // disallow layered instances; new play stops old ones
    url: null,              // string | string[]
    source: null,           // ArrayBuffer | AudioBuffer | HTMLAudioElement
    preload: false,         // start loading immediately (autoPlay implies true)
    volume: 1,              // 1 = 100%
    speed: 1,               // 1 = 100%
    complete: null,         // (sound) => void, global complete callback
    loaded: null,           // (err, sound, instance) => void
    loop: false,
    sprites: undefined,     // Record<string, SoundSpriteData>
}
```

- The options object is frozen; the instance keeps it as `soundObj.options`.
- `loaded(err, sound, instance)` is called once, even if `play()` was called while loading. With WebAudio, error messages name the file and the original error is in `err.cause`. If no callback is given, errors log to the console.

### Multi-format URL arrays

`preferUrl()` filters the array to extensions in `utils.supported`, then sorts by `utils.extensions` order (ogg > oga > opus > m4a > mp3 > mpeg > wav > aiff > wma > mid > caf) and takes the first. Throws `Error('No supported file type found')` when none match. The resolved single url is stored as `soundObj.url`.

## play()

```ts
play(): IMediaInstance | Promise<IMediaInstance>;
play(spriteAlias: string, complete?: CompleteCallback): IMediaInstance | Promise<IMediaInstance>;
play(source?: PlayOptions | CompleteCallback, complete?: CompleteCallback): IMediaInstance | Promise<IMediaInstance>;
```

PlayOptions defaults merged over `{ complete: null, loaded: null, sprite: null, end: null, start: 0, volume: 1, speed: 1, muted: false, loop: false }`:

```ts
{
    start: 0,            // start offset in seconds (also accepts deprecated `offset`)
    end: undefined,      // end time in seconds
    speed: 1,            // instance speed; sound speed and global speed multiply it
    loop: false,         // overrides the Sound's loop setting
    volume: 1,           // overrides the Sound's volume
    muted: false,        // mute this instance only
    sprite: undefined,   // sprite alias to play
    filters: undefined,  // Filter[] (WebAudio only)
    complete: undefined, // (sound) => void
    loaded: undefined,   // (err, sound, instance) => void; called with the instance this call started
    singleInstance: false, // stop existing instances before playing
}
```

### Load queueing (play while not yet loaded)

- If `isLoaded` is false, `play()` returns a **Promise** and starts the preload (first call) or joins the pending queue (later calls).
- Each queued call starts its **own instance** once the sound loads.
- The promise (and every queued promise) **rejects** if loading fails; no `loaded` callback fires on failure.
- `options.loaded` (play-level) is invoked with the instance that call started.

### Sprite resolution in play()

When `options.sprite` is set: asserts the sprite exists; `start = sprite.start + (options.start || 0)`, `end = sprite.end`, `speed = playOptions.speed ?? sprite.speed || 1`, `loop = sprite.loop || options.loop`.

### Instance lifecycle

- `singleInstance` (sound or play option) removes all existing instances before playing.
- A `complete` callback (play or Options-level) fires on `end`; the instance is removed from `_instances` on `end` or `stop` and pooled (`Sound._pool`).
- `isPlaying` is recomputed from `_instances.length > 0`.

## Properties

| Property | Notes |
|---|---|
| `isLoaded` | `true` once the buffer is loaded |
| `isPlaying` | readonly; `true` while instances exist |
| `isPlayable` | `isLoaded && media && media.isPlayable` — the correct check before use |
| `autoPlay` | readonly after creation (settable internally by play queueing) |
| `singleInstance` | get/set |
| `preload` | readonly |
| `url` | readonly; resolved single URL for arrays |
| `options` | readonly; frozen Options |
| `media` | `IMedia` backend object (`WebAudioMedia`/`HTMLAudioMedia`); nulled by `destroy()` |
| `context` | the `IMediaContext` (delegates to the library instance) |
| `paused` | get/set; setter calls `refreshPaused()` |
| `speed` | get/set; setter calls `refresh()` on all instances |
| `volume` | get/set; same |
| `muted` | get/set; same |
| `loop` | get/set; same |
| `duration` | readonly; `media?.duration ?? NaN` — NaN before load, on failure, after `destroy()` |
| `filters` | get/set `Filter[]` (WebAudio only; per media) |
| `instances` | readonly `IMediaInstance[]` currently playing |
| `sprites` | readonly `Record<string, SoundSprite>` |

## Methods

| Method | Notes |
|---|---|
| `stop()` | Stops all instances; also clears `autoPlay` if not yet playable |
| `pause()` / `resume()` | Set the sound-level paused state, refresh all instances |
| `refresh()` | Applies volume/speed/mute/loop changes to all instances (internal) |
| `refreshPaused()` | Applies paused changes (internal) |
| `addSprites(alias, data)` / `addSprites(map)` | See [04-sprites](04-sprites.md) |
| `removeSprites(alias?)` | Remove one or all sprites |
| `autoPlayStart()` | Plays the first instance when `autoPlay` is true (internal, post-load) |
| `destroy()` | Removes instances, sprites, media; `_preloadQueue`/`_loadCallbacks` cleared — a load in progress keeps its own references and still reports to every waiting call |

Prefer `sound.remove(alias)` for library sounds — it removes all aliases referencing the Sound too.
