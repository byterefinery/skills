# PIXI.Assets Integration

Importing `@pixi/sound` registers a `soundAsset` extension (via `extensions.add` in `soundAsset.ts`). It has two parts:

1. **Asset extension** (`ExtensionType.Asset`) — `detection.add` extends the recognized asset formats with every supported audio extension.
2. **Load parser** (`ExtensionType.LoadParser`, `LoaderParserPriority.High`) — the actual loader that turns audio files into `Sound` objects and registers them in the library.

## How loading works

- `test(url)` returns true if the URL's extension is in `utils.supported`, or if the URL is a `data:` URL with a mime in `utils.mimes` (`audio/mpeg`, `audio/ogg`).
- `load(url, asset)` calls `Sound.from({ ...asset.data, url, preload: true, loaded(...) })`, then adds the resulting `Sound` to the library **under every alias** and returns it.
- **Alias resolution** (`getAliases`): the asset's first alias, plus the `src` basename without extension (for direct URL loads), deduplicated. So `Assets.load('assets/explosion.mp3')` registers both `'explosion'` and any explicit alias.
- `unload(sound, asset)` removes the sound from the library: it finds an alias that still maps to this exact `Sound` and calls `library.remove(alias)` (which removes all aliases referencing it). If no alias maps to it (removed manually, or alias now belongs to another sound), it calls `sound.destroy()`.

## Asset data → Sound options

The asset's `data` is spread into `Sound.from`, so it accepts **any Options except `url` and `preload`** — including `sprites`, `volume`, `speed`, `loop`, `singleInstance`, `complete`, `loaded`. `url` comes from the asset `src`; `preload` is forced `true`.

```ts
import { Assets } from 'pixi.js';
import { sound } from '@pixi/sound';

Assets.add({
    alias: 'sfx',
    src: 'path/to/sfx.{ogg,mp3}',
    data: {
        volume: 0.5,
        sprites: {
            coin: { start: 0, end: 0.4 },
            jump: { start: 0.5, end: 1.1 },
        },
    },
});

await Assets.load('sfx');
sound.play('sfx', 'coin');
```

## Bundles

Works with `Assets.add` / `Assets.addBundle` / bundle manifests. The demo example registers a bundle:

```ts
const manifest = [
    { alias: 'loop1', src: 'resources/loops/loop1.{opus,mp3}' },
    { alias: 'loop2', src: 'resources/loops/loop2.{opus,mp3}' },
    { alias: 'bird', src: 'resources/bird.mp3' },
    // ...
];
PIXI.Assets.addBundle('demo', manifest);
await PIXI.Assets.loadBundle('demo');
// each alias is now registered in the sound library
```

## Notes

- Because loading auto-registers, do **not** also call `sound.add()` for the same file/alias — it will fire the duplicate-alias `console.assert`.
- `Assets.unload` triggers the parser's `unload`, which removes the sound from the library.
- Glob `src` (e.g. `'file.{ogg,mp3}'`) is a PixiJS Assets feature; the sound parser receives the resolved `src`.
- The parser's `test` also accepts `data:` URLs with the supported mimes, so base64-inlined audio loads through Assets.
