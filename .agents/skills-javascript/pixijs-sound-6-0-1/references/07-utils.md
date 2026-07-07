# Utilities

## Overview

The `utils` namespace provides helper functions for common audio tasks: one-shot playback, tone generation, waveform rendering, and format detection.

## playOnce

Play a sound file once and automatically remove it from the library after completion.

```ts
import { utils } from '@pixi/sound';

const alias = utils.playOnce('assets/one-shot.mp3', (err) => {
    if (!err) {
        console.log('Played successfully');
    }
});
```

- Returns a unique alias string (`alias0`, `alias1`, ...)
- Auto-preloads and auto-plays
- Removes the sound on completion (success or error)
- The alias is only valid during playback

## sineTone

Generate a sine wave tone. **WebAudio only** — returns an empty Sound in legacy mode.

```ts
import { utils, sound } from '@pixi/sound';

// 440 Hz (A4), 1 second
const tone = utils.sineTone(440, 1);

// Register and play
sound.add('tone', tone);
sound.play('tone');
```

Parameters:
- `hertz` — Frequency in Hz (default: 200)
- `seconds` — Duration in seconds (default: 1)

The generated tone uses:
- 48 kHz sample rate
- Single channel (mono)
- Amplitude of 2

## render

Render a sound's waveform as a `TextureSource`. **WebAudio only** — returns empty texture in legacy mode.

```ts
import { utils, sound } from '@pixi/sound';
import { Sprite } from 'pixi.js';

const texture = utils.render(sound.find('music'), {
    width: 512,
    height: 128,
    fill: '#ffffff',
});

const waveform = new Sprite({ texture });
app.stage.addChild(waveform);
```

### RenderOptions

| Option | Type | Default | Description |
|---|---|---|---|
| `width` | `number` | `512` | Width in pixels |
| `height` | `number` | `128` | Height in pixels |
| `fill` | `string \| CanvasPattern \| CanvasGradient` | `'black'` | Fill style |

The render function:
1. Creates an offscreen canvas
2. Reads the first channel of the AudioBuffer
3. Computes min/max amplitude per column
4. Draws vertical bars representing the waveform
5. Returns a `CanvasSource` TextureSource

## supported

Object mapping file extensions to browser support boolean.

```ts
import { utils } from '@pixi/sound';

utils.supported;
// { mp3: true, ogg: true, wav: true, opus: false, ... }

if (utils.supported['mp3']) {
    sound.add('music', 'assets/music.mp3');
}
```

Supported extensions: `mp3`, `ogg`, `oga`, `opus`, `m4a`, `mpeg`, `wav`, `aiff`, `wma`, `mid`, `caf`.

## extensions

Ordered array of supported audio extensions (preference order).

```ts
import { utils } from '@pixi/sound';

utils.extensions;
// ['ogg', 'oga', 'opus', 'm4a', 'mp3', 'mpeg', 'wav', 'aiff', 'wma', 'mid', 'caf']
```

When passing multiple URLs, the library picks the first supported format in this preference order.

## mimes

Array of supported data URI MIME types.

```ts
import { utils } from '@pixi/sound';

utils.mimes;
// ['audio/mpeg', 'audio/ogg']
```

## validateFormats

Re-run format detection with optional type overrides.

```ts
import { utils } from '@pixi/sound';

// Re-validate with custom MIME type mappings
utils.validateFormats({
    m4a: 'audio/mp4; codecs="mp4a.40.2"',
});

// Check results
console.log(utils.supported);
```

This is called automatically at module load. Call again if you need to recognize formats not in the default list.

## Usage Examples

### Dynamic Tone Generation

```ts
import { utils, sound } from '@pixi/sound';

// Generate musical notes
const notes = {
    C4: 261.63,
    D4: 293.66,
    E4: 329.63,
    F4: 349.23,
    G4: 392.00,
    A4: 440.00,
    B4: 493.88,
};

for (const [name, freq] of Object.entries(notes)) {
    sound.add(`note-${name}`, utils.sineTone(freq, 0.5));
}

// Play a melody
sound.play('note-C4');
setTimeout(() => sound.play('note-E4'), 500);
setTimeout(() => sound.play('note-G4'), 1000);
```

### Waveform Visualizer

```ts
import { utils, sound } from '@pixi/sound';
import { Sprite, Graphics } from 'pixi.js';

// Load and render waveform
const soundObj = await Assets.load('assets/track.mp3');
const texture = utils.render(soundObj, {
    width: 1024,
    height: 200,
    fill: '#1099bb',
});

const waveform = new Sprite({ texture });
waveform.anchor.set(0.5);
waveform.position.set(400, 300);
app.stage.addChild(waveform);
```

### Format-Aware Loading

```ts
import { utils, sound } from '@pixi/sound';

function loadSound(name: string, urls: string[]): void {
    // Pick first supported format
    const url = urls.find(u => utils.supported[getExtension(u)]);
    if (url) {
        sound.add(name, url);
    } else {
        console.warn(`No supported format for ${name}`);
    }
}

loadSound('music', ['music.ogg', 'music.mp3', 'music.wav']);
```
