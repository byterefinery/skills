# Sounds

## Playing Sounds

```js
sounds.play('MySound');
sounds.play('Music', { loop: true });
```

### Options

| Option | Type | Description |
|---|---|---|
| `start` | `number` | Start time offset (seconds) |
| `end` | `number` | End time (seconds) |
| `loop` | `boolean` | Loop the sound |
| `speed` | `number` | Playback speed (1 = normal) |
| `volume` | `number` | Override volume (0-1) |
| `muted` | `boolean` | Start muted |
| `singleInstance` | `boolean` | Stop any playing instances first |
| `complete` | `Function` | Callback when sound finishes |
| `loaded` | `Function` | Callback when sound finishes loading |
| `filters` | `Filter[]` | pixi-sound filters |

### 3D Positional Sound

```js
// Sound follows a copy
sounds.playAt('Footstep', this);

// Sound at fixed position
sounds.playAt('Explosion', { x: this.x, y: this.y });
```

## Sound Control

```js
sounds.stop();                      // Stop all sounds
sounds.stop('Music');               // Stop specific sound
sounds.pause();                     // Pause all
sounds.pause('Music');              // Pause specific
sounds.resume('Music');             // Resume specific
sounds.playing();                   // Any sound playing?
sounds.playing('Music');            // Specific sound playing?
```

## Volume

```js
sounds.volume('Music', 0.5);        // Set volume (0-1)
sounds.volume('Music');             // Get current volume
sounds.globalVolume(0.8);           // Set global volume
sounds.toggleMuteAll();             // Toggle mute all (returns boolean)
```

## Speed

```js
sounds.speed('Music', 1.5);         // Set playback speed
sounds.speed('Music');              // Get current speed
sounds.speedAll(0.8);               // Set speed for all sounds
```

## Fading

```js
sounds.fade();                      // Fade all to 0 over 1000ms
sounds.fade('Music', 0, 2000);      // Fade Music to 0 over 2000ms
sounds.fade('Music', 1, 500);       // Fade Music to full over 500ms
```

## Preloading

```js
// Preload a single sound
sounds.load('BackgroundMusic').then(() => {
    rooms.switch('MainRoom');
});

// Preload multiple sounds
var promises = ['Ambient', 'Battle', 'Victory'].map(s => sounds.load(s));
Promise.all(promises).then(() => {
    rooms.switch('MainRoom');
});
```

## Sound Filters

```js
// Distortion
sounds.addDistortion('MySound', 0.5); // Amount 0-1

// Equalizer (bands: 32, 64, 125, 250, 500, 1k, 2k, 4k, 8k, 16k Hz)
sounds.addEqualizer('MySound', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

// Reverb
sounds.addReverb('MySound', 3, 2, false); // seconds, decay, reverse

// Stereo panning
sounds.addStereoFilter('MySound', 0.5); // -1 = left, 1 = right, 0 = center

// Telephone effect
sounds.addTelephone('MySound');

// Mono
sounds.addMonoFilter('MySound');

// Remove filters
sounds.removeFilter('MySound');           // Remove all filters
sounds.removeFilter('MySound', 'reverb'); // Remove specific filter
```

Filters can be stacked on the same sound. Apply filters before playing.

## Sound Variants

In ct.js IDE, sounds can have multiple variants. When played, a random variant is selected. Configure in the sound editor.

## Sound Editor Ranges

In ct.js IDE, sound properties (pitch, distortion, reverb) can be set as ranges. Each playback randomly picks values within the range, adding variety.

## Misc

```js
sounds.exists('MySound');    // Check if sound metadata exists
sounds.togglePauseAll();     // Toggle pause all (returns boolean)
```

## Gotchas

- **Filters must be applied before playing** — `sounds.addReverb()` then `sounds.play()`.
- **`sounds.play()` returns a promise or instance** — if sound is preloaded, returns instance; otherwise returns a Promise.
- **`sounds.playAt()` position can be a copy** — pass `this` to make sound follow the copy.
- **`sounds.playAt()` with fixed position** — pass `{x, y}` object for a stationary sound.
- **`sounds.exists()` checks metadata only** — doesn't tell if sound is fully loaded.
- **`sounds.load()` returns a Promise** — use `.then()` or `await` before playing.
- **`sounds.fade()` defaults** — fades to volume 0 over 1000ms if no arguments given.
- **Multiple filters stack** — you can add several filters to the same sound.
- **Sound variants are random** — configured in IDE, not controllable from code.
- **`pixi-sound` under the hood** — sound instances are accessible via `res.pixiSounds`.
- **`sounds.stop()` without args stops everything** — including music.
- **`sounds.volume()` getter/setter** — omit second arg to get current volume.
