# Utilities

The `utils` namespace (`import { utils } from '@pixi/sound'`) provides format support info and one-shot helpers. In the browser bundle it's `PIXI.sound.utils`.

## playOnce

```ts
utils.playOnce(url: string, callback?: (err?: Error) => void): string
```

Plays a URL exactly once and auto-removes it from the library when done. Internally adds a sound with an auto alias (`alias0`, `alias1`, … from an incrementing `PLAY_ID`), `preload: true`, `autoPlay: true`.

- Removed from the library on `complete` (success) **and** on `loaded` error.
- The returned alias is only valid during playback — don't reuse it.
- Error path: logs the error, removes the alias, then calls `callback(err)`.

```ts
const alias = utils.playOnce('assets/one-shot.mp3', (err) => {
    if (!err) console.log('played and removed');
});
```

## sineTone

```ts
utils.sineTone(hertz = 200, seconds = 1): Sound
```

Generates a sine-wave tone as a `Sound`. **WebAudio only.**

- Builds a mono `AudioBuffer` at a fixed 48000 Hz sample rate, amplitude 2.
- In legacy mode (media is not `WebAudioMedia`) it returns an empty, **unloaded** `Sound` (no buffer set).
- Returns a `Sound` object, not a raw buffer — register it with `sound.add(alias, soundObj)` (which accepts a `Sound` instance) or play it directly.

```ts
const tone = utils.sineTone(440, 1);
sound.add('tone', tone);
sound.play('tone');
```

## render

```ts
utils.render(sound: Sound, options?: RenderOptions): TextureSource
```

Renders a loaded sound as a waveform on a canvas, returned as a PixiJS `CanvasSource` (a `TextureSource`). **WebAudio only.**

```ts
interface RenderOptions {
    width?: number;   // default 512
    height?: number;  // default 128
    fill?: string | CanvasPattern | CanvasGradient; // default 'black'
}
```

- In legacy mode (media not `WebAudioMedia`) it returns an **empty canvas** `TextureSource` (no waveform drawn).
- Asserts the media has a `buffer` ("No buffer found, load first") — load the sound first.
- Draws per-column min/max of the first channel as filled rects.

```ts
const texture = utils.render(soundObj, { width: 512, height: 128, fill: '#ccc' });
app.stage.addChild(new PIXI.Sprite(new PIXI.Texture(texture)));
```

## Format support

| Member | Type | Notes |
|---|---|---|
| `supported` | `Record<string, boolean>` | Browser-supported audio formats, keyed by extension |
| `extensions` | `string[]` | **Preferred playback order**: `ogg, oga, opus, m4a, mp3, mpeg, wav, aiff, wma, mid, caf` |
| `mimes` | `string[]` | `['audio/mpeg', 'audio/ogg']` — used to recognize `data:` URLs |
| `validateFormats(typeOverrides?)` | `void` | Re-run detection; pass overrides keyed by extension |

`validateFormats` was already run at module init (it calls `document.createElement('audio').canPlayType(...)` for each extension). Call it again only to recognize a format not in `utils.extensions`. Override dictionary (defaults):

```ts
{
    m4a: 'audio/mp4',
    oga: 'audio/ogg',
    opus: 'audio/ogg; codecs="opus"',
    caf: 'audio/x-caf; codecs="opus"',
}
```

`supported.caf` checks whether the `opus` codec is supported inside the `caf` container.

## Notes

- `playOnce`, `sineTone`, and `render` all depend on the active backend; check `sound.supported` (WebAudio) before relying on WebAudio-only behavior.
- `utils` is a namespace of functions/consts, not a class — call members directly.
